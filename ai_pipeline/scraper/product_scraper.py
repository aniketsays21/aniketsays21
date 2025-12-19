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

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

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
        domain = urlparse(url).netloc.lower()

        if "amazon" in domain:
            return "amazon"
        elif "shopify" in domain or self._is_shopify_store(url):
            return "shopify"
        else:
            return "generic"

    def _is_shopify_store(self, url: str) -> bool:
        """Check if URL is a Shopify store by looking for common patterns"""
        try:
            response = httpx.get(url, timeout=5, follow_redirects=True)
            return "Shopify" in response.headers.get("X-ShopId", "") or \
                   "shopify" in response.text.lower()[:1000]
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
        # Shopify stores often have a .json endpoint
        product_json_url = url.rstrip("/") + ".json"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(product_json_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    product = data.get("product", {})

                    return {
                        "title": product.get("title", "Unknown Product"),
                        "description": product.get("body_html", ""),
                        "price": str(product.get("variants", [{}])[0].get("price", "")),
                        "images": [img["src"] for img in product.get("images", [])],
                        "metadata": {
                            "source": "shopify",
                            "url": url,
                            "product_type": product.get("product_type"),
                            "vendor": product.get("vendor")
                        }
                    }
        except:
            logger.warning("Shopify JSON API failed, falling back to HTML scraping")

        # Fallback to HTML scraping
        return await self._scrape_generic(url)

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
