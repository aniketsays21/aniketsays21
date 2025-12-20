import asyncio
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page
import httpx
import re
from loguru import logger


class ProductScraper:
    """
    Scrape product information from e-commerce URLs
    Supports: Amazon, Shopify stores, generic e-commerce sites
    """

    # Known Shopify stores (Indian D2C brands)
    KNOWN_SHOPIFY_DOMAINS = [
        "dotandkey.com", "mamaearth.in", "plumgoodness.com", "mcaffeine.com",
        "minimalistlabs.com", "themomsco.com", "wowskinscience.com", "beardo.in",
        "nykaa.com", "purplle.com", "myglamm.com", "sugarcosmetics.com"
    ]

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

    async def scrape(self, url: str) -> Dict:
        """
        Main scraping method
        Returns: {title, description, price, images, metadata}
        """
        logger.info(f"Starting scrape for URL: {url}")

        # Determine site type
        site_type = self._detect_site_type(url)
        logger.info(f"Detected site type: {site_type}")

        # Use appropriate scraping strategy
        if site_type == "amazon":
            return await self._scrape_amazon(url)
        elif site_type == "shopify":
            return await self._scrape_shopify(url)
        else:
            return await self._scrape_generic(url)

    def _detect_site_type(self, url: str) -> str:
        """Detect the type of e-commerce platform"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        if "amazon" in domain:
            return "amazon"

        # Check known Shopify domains
        for shopify_domain in self.KNOWN_SHOPIFY_DOMAINS:
            if shopify_domain in domain:
                return "shopify"

        # Check URL pattern for Shopify-style product URLs
        if "/products/" in path:
            return "shopify"

        if "shopify" in domain or self._is_shopify_store(url):
            return "shopify"

        return "generic"

    def _is_shopify_store(self, url: str) -> bool:
        """Check if URL is a Shopify store by looking for common patterns"""
        try:
            response = httpx.get(url, timeout=5, follow_redirects=True, headers=self.headers)
            return "Shopify" in response.headers.get("X-ShopId", "") or \
                   "shopify" in response.text.lower()[:2000] or \
                   "cdn.shopify.com" in response.text[:5000]
        except:
            return False

    async def _scrape_amazon(self, url: str) -> Dict:
        """Scrape Amazon product page"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()

            try:
                await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                await page.wait_for_load_state("networkidle", timeout=10000)

                # Extract data
                title = await self._get_text(page, "#productTitle")
                description = await self._get_text(page, "#feature-bullets") or \
                             await self._get_text(page, "#productDescription")
                price = await self._get_text(page, ".a-price-whole") or \
                       await self._get_text(page, "#priceblock_ourprice")

                # Images
                images = await self._extract_amazon_images(page)

                return {
                    "title": title.strip() if title else "Unknown Product",
                    "description": description.strip() if description else "",
                    "price": price.strip() if price else None,
                    "images": images,
                    "metadata": {
                        "source": "amazon",
                        "url": url
                    }
                }

            finally:
                await browser.close()

    async def _scrape_shopify(self, url: str) -> Dict:
        """Scrape Shopify product page"""
        # Try Shopify JSON API first
        product_json_url = url.rstrip("/") + ".json"

        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
                response = await client.get(product_json_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    product = data.get("product", {})

                    return {
                        "title": product.get("title", "Unknown Product"),
                        "description": self._clean_html(product.get("body_html", "")),
                        "price": str(product.get("variants", [{}])[0].get("price", "")),
                        "images": [img["src"] for img in product.get("images", [])],
                        "metadata": {
                            "source": "shopify",
                            "url": url,
                            "product_type": product.get("product_type"),
                            "vendor": product.get("vendor")
                        }
                    }
        except Exception as e:
            logger.warning(f"Shopify JSON API failed: {e}")

        # Fallback to HTML scraping with embedded JSON-LD
        logger.info("Trying HTML scraping with JSON-LD extraction")
        return await self._scrape_shopify_html(url)

    async def _scrape_shopify_html(self, url: str) -> Dict:
        """Scrape Shopify store by parsing HTML and JSON-LD data"""
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=20) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    return await self._scrape_generic(url)

                html = response.text
                soup = BeautifulSoup(html, 'html.parser')

                # Try to extract JSON-LD structured data
                json_ld_data = self._extract_json_ld(soup)
                if json_ld_data:
                    return json_ld_data

                # Try to extract from meta tags
                meta_data = self._extract_meta_tags(soup, url)
                if meta_data.get("title") != "Unknown Product":
                    return meta_data

                # Fallback to generic scraping
                return await self._scrape_generic(url)

        except Exception as e:
            logger.error(f"Shopify HTML scraping failed: {e}")
            return await self._scrape_generic(url)

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract product data from JSON-LD script tags"""
        try:
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)

                    # Handle both single object and array
                    if isinstance(data, list):
                        for item in data:
                            if item.get("@type") == "Product":
                                data = item
                                break
                        else:
                            continue

                    if data.get("@type") == "Product":
                        images = data.get("image", [])
                        if isinstance(images, str):
                            images = [images]

                        price = None
                        offers = data.get("offers", {})
                        if isinstance(offers, list):
                            offers = offers[0] if offers else {}
                        price = offers.get("price") or offers.get("lowPrice")

                        return {
                            "title": data.get("name", "Unknown Product"),
                            "description": data.get("description", ""),
                            "price": f"₹{price}" if price else None,
                            "images": images[:10],
                            "metadata": {
                                "source": "shopify_jsonld",
                                "brand": data.get("brand", {}).get("name") if isinstance(data.get("brand"), dict) else data.get("brand"),
                                "sku": data.get("sku"),
                            }
                        }
                except:
                    continue
        except Exception as e:
            logger.debug(f"JSON-LD extraction failed: {e}")
        return None

    def _extract_meta_tags(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract product data from Open Graph and meta tags"""
        title = None
        description = None
        image = None
        price = None

        # Open Graph tags
        og_title = soup.find("meta", property="og:title")
        og_desc = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")
        og_price = soup.find("meta", property="product:price:amount")

        if og_title:
            title = og_title.get("content")
        if og_desc:
            description = og_desc.get("content")
        if og_image:
            image = og_image.get("content")
        if og_price:
            price = og_price.get("content")

        # Collect all product images from og:image tags
        images = []
        for img_tag in soup.find_all("meta", property="og:image"):
            img_url = img_tag.get("content")
            if img_url and img_url not in images:
                images.append(img_url)

        # Also try to find images in srcset or data attributes
        for img in soup.find_all("img", {"data-srcset": True}):
            srcset = img.get("data-srcset", "")
            urls = re.findall(r'(https?://[^\s,]+)', srcset)
            for u in urls:
                if u not in images and "cdn.shopify.com" in u:
                    images.append(u.split("?")[0])  # Remove query params

        return {
            "title": title or "Unknown Product",
            "description": description or "",
            "price": f"₹{price}" if price else None,
            "images": images[:10],
            "metadata": {
                "source": "meta_tags",
                "url": url
            }
        }

    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text(separator=" ", strip=True)

    async def _scrape_generic(self, url: str) -> Dict:
        """Scrape generic e-commerce page using heuristics"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()

            try:
                await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                await page.wait_for_load_state("networkidle", timeout=10000)

                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Extract using common patterns
                title = self._extract_title(soup)
                description = self._extract_description(soup)
                price = self._extract_price(soup)
                images = await self._extract_images(page, soup, url)

                return {
                    "title": title,
                    "description": description,
                    "price": price,
                    "images": images,
                    "metadata": {
                        "source": "generic",
                        "url": url
                    }
                }

            finally:
                await browser.close()

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title using various selectors"""
        selectors = [
            {"itemprop": "name"},
            {"class": re.compile(r"product.?title", re.I)},
            {"id": re.compile(r"product.?title", re.I)},
            "h1"
        ]

        for selector in selectors:
            if isinstance(selector, str):
                element = soup.find(selector)
            else:
                element = soup.find(attrs=selector)

            if element:
                return element.get_text().strip()

        return "Unknown Product"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        selectors = [
            {"itemprop": "description"},
            {"class": re.compile(r"product.?description", re.I)},
            {"id": re.compile(r"product.?description", re.I)},
        ]

        for selector in selectors:
            element = soup.find(attrs=selector)
            if element:
                return element.get_text().strip()

        return ""

    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product price"""
        selectors = [
            {"itemprop": "price"},
            {"class": re.compile(r"price", re.I)},
            {"id": re.compile(r"price", re.I)},
        ]

        for selector in selectors:
            element = soup.find(attrs=selector)
            if element:
                price_text = element.get_text().strip()
                # Clean up price
                price_match = re.search(r'[\$€£¥]\s*[\d,]+\.?\d*', price_text)
                if price_match:
                    return price_match.group()

        return None

    async def _extract_images(self, page: Page, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract product images"""
        images = []

        # Try to find image gallery
        img_elements = soup.find_all("img", src=re.compile(r"\.(jpg|jpeg|png|webp)", re.I))

        for img in img_elements:
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if src:
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, src)
                # Filter out tiny images (likely icons)
                if not any(x in src.lower() for x in ["icon", "logo", "sprite"]):
                    images.append(full_url)

        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)

        return unique_images[:10]  # Limit to 10 images

    async def _extract_amazon_images(self, page: Page) -> List[str]:
        """Extract images from Amazon product page"""
        images = []

        # Try to get high-res images from the image gallery
        try:
            img_data = await page.evaluate("""
                () => {
                    const images = [];
                    // Try to get from image data
                    if (window.imageGalleryData) {
                        window.imageGalleryData.forEach(img => {
                            if (img.mainUrl) images.push(img.mainUrl);
                        });
                    }
                    // Fallback to img tags
                    document.querySelectorAll('#altImages img, #imageBlock img').forEach(img => {
                        const src = img.src || img.getAttribute('data-old-hires');
                        if (src && !src.includes('sprite')) {
                            images.push(src);
                        }
                    });
                    return [...new Set(images)];
                }
            """)
            images = img_data
        except:
            pass

        return images[:10]

    async def _get_text(self, page: Page, selector: str) -> Optional[str]:
        """Get text content from selector"""
        try:
            element = await page.query_selector(selector)
            if element:
                return await element.inner_text()
        except:
            pass
        return None


# Standalone function for easy import
async def scrape_product(url: str) -> Dict:
    """Convenience function to scrape a product"""
    scraper = ProductScraper()
    return await scraper.scrape(url)
