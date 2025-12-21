"""
Product scraper service.

Uses Apify actors for reliable product scraping:
- Shopify stores: Specialized Shopify actor
- Amazon/Flipkart/Others: Generic e-commerce actor
"""

from sqlalchemy.orm import Session
from models.database import Product
from services.apify_scraper import scrape_product_with_apify
from loguru import logger


async def scrape_product(url: str, db: Session) -> Product:
    """
    Scrape product from URL and save to database.

    Uses Apify actors for scraping:
    - Shopify URLs → Shopify product scraper actor
    - Other URLs → E-commerce scraping tool actor
    """
    # Check if already scraped
    existing = db.query(Product).filter(Product.url == url).first()
    if existing:
        logger.info(f"Product already scraped: {url}")
        return existing

    # Scrape product using Apify
    logger.info(f"Scraping product with Apify: {url}")
    product_data = await scrape_product_with_apify(url)

    # Save to database
    product = Product(
        url=url,
        title=product_data["title"],
        description=product_data["description"],
        price=product_data.get("price"),
        images=product_data["images"],
        extra_data=product_data.get("metadata")
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    logger.info(f"Product saved: {product.id} - {product.title}")
    return product
