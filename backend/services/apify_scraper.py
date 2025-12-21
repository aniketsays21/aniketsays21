"""
Apify-based product scraper service.

Uses Apify actors to scrape product data from e-commerce sites:
- Shopify stores: First tries direct JSON API, then Apify actor
- Amazon/Flipkart/Others: Uses generic e-commerce scraping tool
"""

import asyncio
import httpx
import re
from typing import Dict, Optional, List
from urllib.parse import urlparse
from loguru import logger

from config.settings import settings


class ApifyScraper:
    """
    Scrape products using Apify actors.
    For Shopify stores, first tries direct JSON API (free), then falls back to Apify.
    """

    BASE_URL = "https://api.apify.com/v2"

    # Known Shopify domains (Indian D2C brands)
    SHOPIFY_DOMAINS = [
        "dotandkey.com", "mamaearth.in", "plumgoodness.com", "mcaffeine.com",
        "minimalistlabs.com", "themomsco.com", "wowskinscience.com", "beardo.in",
        "sugarcosmetics.com", "myglamm.com", "nykaa.com", "purplle.com",
        "boatlifestyle.com", "noise.com", "fireboltt.com", "littleboxindia.com",
        "tfrstore.com", "reneecosmetics.in", "earthrhythm.com", "juicychemistry.com"
    ]

    def __init__(self, api_token: str = None):
        self.api_token = api_token or settings.APIFY_API_TOKEN
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN is required")

        self.shopify_actor = settings.APIFY_SHOPIFY_ACTOR
        self.ecommerce_actor = settings.APIFY_ECOMMERCE_ACTOR
        self.timeout = 120  # seconds to wait for actor run
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json,text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _is_shopify_url(self, url: str) -> bool:
        """Check if URL is from a Shopify store"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")

        for shopify_domain in self.SHOPIFY_DOMAINS:
            if shopify_domain in domain:
                return True

        if "/products/" in parsed.path:
            return True

        return False

    def _get_product_handle(self, url: str) -> Optional[str]:
        """Extract product handle from Shopify URL"""
        # URL pattern: /products/product-handle or /collections/xxx/products/product-handle
        match = re.search(r'/products/([^/?]+)', url)
        if match:
            return match.group(1)
        return None

    def _get_base_url(self, url: str) -> str:
        """Get base URL from full URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    async def scrape(self, url: str) -> Dict:
        """
        Scrape product from URL.
        """
        logger.info(f"Scraping product: {url}")

        if self._is_shopify_url(url):
            logger.info("Detected Shopify store")
            return await self._scrape_shopify(url)
        else:
            logger.info("Using generic e-commerce actor")
            return await self._scrape_generic(url)

    async def _scrape_shopify(self, url: str) -> Dict:
        """
        Scrape Shopify product.
        1. First try direct Shopify JSON API (free, fast)
        2. If blocked, use Apify actor
        """
        # Try direct Shopify JSON API first
        product_handle = self._get_product_handle(url)
        base_url = self._get_base_url(url)

        if product_handle:
            json_url = f"{base_url}/products/{product_handle}.json"
            logger.info(f"Trying direct Shopify JSON API: {json_url}")

            try:
                async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                    response = await client.get(json_url, headers=self.headers)

                    if response.status_code == 200:
                        data = response.json()
                        product = data.get("product", {})

                        if product:
                            logger.info("Direct Shopify JSON API succeeded!")
                            return self._normalize_shopify_json(product, url)
                    else:
                        logger.warning(f"Shopify JSON API returned {response.status_code}")
            except Exception as e:
                logger.warning(f"Direct Shopify JSON failed: {e}")

        # Fallback to Apify actor
        logger.info("Falling back to Apify Shopify actor")
        return await self._scrape_with_apify_shopify(url)

    async def _scrape_with_apify_shopify(self, url: str) -> Dict:
        """Scrape Shopify product using Apify actor"""
        actor_id = self.shopify_actor

        # Input for Shopify actor - correct format based on actor's input schema
        run_input = {
            "shopifyUrl": url,
            "urlType": "Auto-detect",
            "maxProducts": 1
        }

        result = await self._run_actor(actor_id, run_input)

        # Log the raw result for debugging
        logger.info(f"Apify Shopify actor raw result: {result}")

        if result and len(result) > 0:
            item = result[0]
            logger.info(f"Apify returned item keys: {item.keys() if isinstance(item, dict) else 'not a dict'}")
            return self._normalize_shopify_result(item, url)

        # Fallback to generic scraper
        logger.warning("Shopify actor returned no results, trying generic")
        return await self._scrape_generic(url)

    def _normalize_shopify_json(self, product: Dict, url: str) -> Dict:
        """Normalize direct Shopify JSON API response"""
        title = product.get("title", "Unknown Product")

        description = product.get("body_html", "")
        if description and "<" in description:
            from bs4 import BeautifulSoup
            description = BeautifulSoup(description, 'html.parser').get_text(separator=" ", strip=True)

        # Get price from variants
        price = None
        variants = product.get("variants", [])
        if variants:
            price = variants[0].get("price")
            if price:
                price = f"₹{price}"

        # Get images
        images = []
        for img in product.get("images", []):
            src = img.get("src") if isinstance(img, dict) else img
            if src:
                images.append(src)

        return {
            "title": title,
            "description": description[:2000] if description else "",
            "price": price,
            "images": images[:10],
            "metadata": {
                "source": "shopify_json_api",
                "url": url,
                "vendor": product.get("vendor"),
                "product_type": product.get("product_type"),
                "handle": product.get("handle")
            }
        }

    async def _scrape_generic(self, url: str) -> Dict:
        """Scrape product using generic e-commerce actor"""
        actor_id = self.ecommerce_actor

        run_input = {
            "startUrls": [{"url": url}],
            "maxProductsPerStore": 1,
            "scrapeProductDetails": True
        }

        result = await self._run_actor(actor_id, run_input)

        logger.info(f"Generic actor raw result: {result}")

        if result and len(result) > 0:
            item = result[0]
            return self._normalize_generic_result(item, url)

        logger.error(f"No results from Apify for URL: {url}")
        return {
            "title": "Unknown Product",
            "description": "",
            "price": None,
            "images": [],
            "metadata": {"source": "apify_failed", "url": url}
        }

    async def _run_actor(self, actor_id: str, run_input: Dict) -> Optional[List[Dict]]:
        """Run an Apify actor and wait for results."""
        async with httpx.AsyncClient(timeout=60) as client:
            start_url = f"{self.BASE_URL}/acts/{actor_id}/runs?token={self.api_token}"

            logger.info(f"Starting Apify actor: {actor_id}")
            logger.info(f"Actor input: {run_input}")

            try:
                response = await client.post(
                    start_url,
                    json=run_input,
                    headers={"Content-Type": "application/json"}
                )

                logger.info(f"Actor start response: {response.status_code}")

                if response.status_code != 201:
                    logger.error(f"Failed to start actor: {response.status_code} - {response.text}")
                    return None

                run_data = response.json()["data"]
                run_id = run_data["id"]
                dataset_id = run_data["defaultDatasetId"]

                logger.info(f"Actor run started: {run_id}, dataset: {dataset_id}")

            except Exception as e:
                logger.error(f"Error starting actor: {e}")
                return None

            # Poll until completed
            status_url = f"{self.BASE_URL}/actor-runs/{run_id}?token={self.api_token}"

            start_time = asyncio.get_event_loop().time()
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.timeout:
                    logger.error(f"Actor run timed out after {self.timeout}s")
                    return None

                try:
                    response = await client.get(status_url)
                    status_data = response.json()["data"]
                    status = status_data["status"]

                    logger.info(f"Actor status: {status} (elapsed: {int(elapsed)}s)")

                    if status == "SUCCEEDED":
                        break
                    elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                        logger.error(f"Actor run failed with status: {status}")
                        return None

                    await asyncio.sleep(3)

                except Exception as e:
                    logger.error(f"Error polling actor status: {e}")
                    return None

            # Fetch dataset items
            items_url = f"{self.BASE_URL}/datasets/{dataset_id}/items?token={self.api_token}"

            try:
                response = await client.get(items_url)
                if response.status_code == 200:
                    items = response.json()
                    logger.info(f"Got {len(items)} items from dataset")
                    if items:
                        logger.info(f"First item sample: {str(items[0])[:500]}")
                    return items
                else:
                    logger.error(f"Failed to fetch dataset: {response.status_code}")
                    return None

            except Exception as e:
                logger.error(f"Error fetching dataset: {e}")
                return None

    def _normalize_shopify_result(self, item: Dict, url: str) -> Dict:
        """Normalize Shopify actor output to our format"""
        logger.info(f"Normalizing Shopify result keys: {list(item.keys()) if isinstance(item, dict) else 'not a dict'}")

        # Get title
        title = item.get("title") or item.get("name") or "Unknown Product"

        # Get description - Apify returns "descriptionHtml"
        description = (
            item.get("descriptionHtml") or
            item.get("description") or
            item.get("body_html") or
            ""
        )

        # Clean HTML from description
        if description and "<" in description:
            from bs4 import BeautifulSoup
            description = BeautifulSoup(description, 'html.parser').get_text(separator=" ", strip=True)

        # Get price from variants array
        price = None
        variants = item.get("variants", [])
        if variants and len(variants) > 0:
            variant_price = variants[0].get("price")
            if variant_price:
                price = f"₹{variant_price}"

        # Get images - Apify returns images as array of objects with "src" field
        images = []
        for img in item.get("images", []):
            if isinstance(img, dict):
                src = img.get("src")
                if src:
                    images.append(src)
            elif isinstance(img, str):
                images.append(img)

        # Limit to 10 images
        images = images[:10]

        logger.info(f"Normalized result - title: {title}, images: {len(images)}, price: {price}")

        return {
            "title": title,
            "description": description[:2000] if description else "",
            "price": price,
            "images": images,
            "metadata": {
                "source": "apify_shopify",
                "url": url,
                "vendor": item.get("vendor"),
                "product_type": item.get("productType"),
                "handle": item.get("handle"),
            }
        }

    def _normalize_generic_result(self, item: Dict, url: str) -> Dict:
        """Normalize generic e-commerce actor output to our format"""
        title = item.get("title") or item.get("name") or item.get("productName") or "Unknown Product"
        description = item.get("description") or item.get("productDescription") or ""

        price = item.get("price") or item.get("currentPrice") or item.get("salePrice")
        if price:
            price = str(price)
            if not any(c in price for c in ["₹", "$", "€", "£"]):
                price = f"₹{price}"

        images = []
        if "images" in item and isinstance(item["images"], list):
            images = [img if isinstance(img, str) else img.get("url", "") for img in item["images"]]
        elif "image" in item:
            images = [item["image"]] if isinstance(item["image"], str) else []
        elif "imageUrl" in item:
            images = [item["imageUrl"]]

        images = [img for img in images if img][:10]

        return {
            "title": title,
            "description": description[:2000] if description else "",
            "price": price,
            "images": images,
            "metadata": {
                "source": "apify_ecommerce",
                "url": url,
                "brand": item.get("brand"),
                "category": item.get("category"),
                "rating": item.get("rating") or item.get("stars")
            }
        }


async def scrape_product_with_apify(url: str) -> Dict:
    """Convenience function to scrape a product using Apify"""
    scraper = ApifyScraper()
    return await scraper.scrape(url)
