"""
Apify-based product scraper service.

Uses Apify actors to scrape product data from e-commerce sites:
- Shopify stores: Uses specialized Shopify actor
- Amazon/Flipkart/Others: Uses generic e-commerce scraping tool
"""

import asyncio
import httpx
from typing import Dict, Optional, List
from urllib.parse import urlparse
from loguru import logger

from config.settings import settings


class ApifyScraper:
    """
    Scrape products using Apify actors.

    Actors used:
    - Shopify: linen_snack~shopify-product-scraper-extract-product-data-via-json-api
    - Others: apify~e-commerce-scraping-tool
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

    def _is_shopify_url(self, url: str) -> bool:
        """Check if URL is from a Shopify store"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")

        # Check known Shopify domains
        for shopify_domain in self.SHOPIFY_DOMAINS:
            if shopify_domain in domain:
                return True

        # Check URL pattern (Shopify uses /products/ pattern)
        if "/products/" in parsed.path:
            return True

        return False

    async def scrape(self, url: str) -> Dict:
        """
        Scrape product from URL.

        Returns:
            {
                "title": str,
                "description": str,
                "price": str,
                "images": List[str],
                "metadata": Dict
            }
        """
        logger.info(f"Scraping product with Apify: {url}")

        if self._is_shopify_url(url):
            logger.info("Detected Shopify store, using Shopify actor")
            return await self._scrape_shopify(url)
        else:
            logger.info("Using generic e-commerce actor")
            return await self._scrape_generic(url)

    async def _scrape_shopify(self, url: str) -> Dict:
        """Scrape Shopify product using specialized actor"""
        actor_id = self.shopify_actor

        # Input for Shopify actor
        run_input = {
            "startUrls": [{"url": url}],
            "maxItems": 1
        }

        result = await self._run_actor(actor_id, run_input)

        if result and len(result) > 0:
            item = result[0]
            return self._normalize_shopify_result(item, url)

        # Fallback to generic scraper
        logger.warning("Shopify actor returned no results, trying generic")
        return await self._scrape_generic(url)

    async def _scrape_generic(self, url: str) -> Dict:
        """Scrape product using generic e-commerce actor"""
        actor_id = self.ecommerce_actor

        # Input for e-commerce scraping tool
        run_input = {
            "startUrls": [{"url": url}],
            "maxProductsPerStore": 1,
            "scrapeProductDetails": True
        }

        result = await self._run_actor(actor_id, run_input)

        if result and len(result) > 0:
            item = result[0]
            return self._normalize_generic_result(item, url)

        # Return empty result if nothing found
        logger.error(f"No results from Apify for URL: {url}")
        return {
            "title": "Unknown Product",
            "description": "",
            "price": None,
            "images": [],
            "metadata": {"source": "apify_failed", "url": url}
        }

    async def _run_actor(self, actor_id: str, run_input: Dict) -> Optional[List[Dict]]:
        """
        Run an Apify actor and wait for results.

        1. Start the actor run
        2. Poll until completed
        3. Fetch dataset items
        """
        async with httpx.AsyncClient(timeout=60) as client:
            # 1. Start the actor run
            start_url = f"{self.BASE_URL}/acts/{actor_id}/runs?token={self.api_token}"

            logger.info(f"Starting Apify actor: {actor_id}")

            try:
                response = await client.post(
                    start_url,
                    json=run_input,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code != 201:
                    logger.error(f"Failed to start actor: {response.status_code} - {response.text}")
                    return None

                run_data = response.json()["data"]
                run_id = run_data["id"]
                dataset_id = run_data["defaultDatasetId"]

                logger.info(f"Actor run started: {run_id}")

            except Exception as e:
                logger.error(f"Error starting actor: {e}")
                return None

            # 2. Poll until completed
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

                    logger.debug(f"Actor status: {status}")

                    if status == "SUCCEEDED":
                        break
                    elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                        logger.error(f"Actor run failed with status: {status}")
                        return None

                    # Wait before polling again
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"Error polling actor status: {e}")
                    return None

            # 3. Fetch dataset items
            items_url = f"{self.BASE_URL}/datasets/{dataset_id}/items?token={self.api_token}"

            try:
                response = await client.get(items_url)
                if response.status_code == 200:
                    items = response.json()
                    logger.info(f"Got {len(items)} items from dataset")
                    return items
                else:
                    logger.error(f"Failed to fetch dataset: {response.status_code}")
                    return None

            except Exception as e:
                logger.error(f"Error fetching dataset: {e}")
                return None

    def _normalize_shopify_result(self, item: Dict, url: str) -> Dict:
        """Normalize Shopify actor output to our format"""
        # The Shopify actor might return data in different formats
        # Handle common variations

        title = item.get("title") or item.get("name") or item.get("productTitle") or "Unknown Product"

        description = item.get("description") or item.get("body_html") or item.get("productDescription") or ""
        # Clean HTML from description
        if "<" in description:
            from bs4 import BeautifulSoup
            description = BeautifulSoup(description, 'html.parser').get_text(separator=" ", strip=True)

        # Get price
        price = None
        if "price" in item:
            price = str(item["price"])
        elif "variants" in item and item["variants"]:
            price = str(item["variants"][0].get("price", ""))
        elif "priceRange" in item:
            price = item["priceRange"].get("minVariantPrice", {}).get("amount")

        if price:
            price = f"₹{price}" if not price.startswith("₹") else price

        # Get images
        images = []
        if "images" in item:
            if isinstance(item["images"], list):
                for img in item["images"]:
                    if isinstance(img, str):
                        images.append(img)
                    elif isinstance(img, dict):
                        images.append(img.get("src") or img.get("url") or "")
        elif "image" in item:
            img = item["image"]
            if isinstance(img, str):
                images.append(img)
            elif isinstance(img, dict):
                images.append(img.get("src") or img.get("url") or "")

        # Filter out empty strings
        images = [img for img in images if img][:10]

        return {
            "title": title,
            "description": description[:2000] if description else "",
            "price": price,
            "images": images,
            "metadata": {
                "source": "apify_shopify",
                "url": url,
                "vendor": item.get("vendor"),
                "product_type": item.get("product_type") or item.get("productType"),
                "handle": item.get("handle")
            }
        }

    def _normalize_generic_result(self, item: Dict, url: str) -> Dict:
        """Normalize generic e-commerce actor output to our format"""
        title = item.get("title") or item.get("name") or item.get("productName") or "Unknown Product"
        description = item.get("description") or item.get("productDescription") or ""

        # Get price
        price = item.get("price") or item.get("currentPrice") or item.get("salePrice")
        if price:
            price = str(price)
            if not any(c in price for c in ["₹", "$", "€", "£"]):
                price = f"₹{price}"

        # Get images
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
