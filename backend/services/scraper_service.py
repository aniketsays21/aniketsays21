import sys
import os

# Add parent directory to path to import ai_pipeline
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from models.database import Product
from ai_pipeline.scraper.product_scraper import scrape_product as scrape_product_util
from loguru import logger


async def scrape_product(url: str, db: Session) -> Product:
    """
    Scrape product from URL and save to database
    """
    # Check if already scraped
    existing = db.query(Product).filter(Product.url == url).first()
    if existing:
        logger.info(f"Product already scraped: {url}")
        return existing

    # Scrape product
    logger.info(f"Scraping product: {url}")
    product_data = await scrape_product_util(url)

    # Save to database
    product = Product(
        url=url,
        title=product_data["title"],
        description=product_data["description"],
        price=product_data.get("price"),
        images=product_data["images"],
        extra_metadata=product_data.get("metadata")
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    logger.info(f"Product saved: {product.id}")
    return product
