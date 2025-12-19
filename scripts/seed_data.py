"""
Seed initial data for the AI UGC Video Platform
Adds default actions and example backgrounds
"""

import sys
sys.path.append('../backend')

from sqlalchemy.orm import Session
from models.database import SessionLocal, Action, Background, init_db
import json


def seed_actions(db: Session):
    """Create default actions"""
    actions = [
        {
            "name": "Product Showcase",
            "description": "Model holds and displays the product",
            "pose_sequence": {
                "type": "showcase",
                "keyframes": [
                    {"frame": 0, "pose": "neutral"},
                    {"frame": 30, "pose": "hold_product"},
                    {"frame": 60, "pose": "display"},
                ]
            },
            "duration": 5.0,
            "is_active": True
        },
        {
            "name": "Happy Presentation",
            "description": "Model presents product with enthusiasm",
            "pose_sequence": {
                "type": "presentation",
                "keyframes": [
                    {"frame": 0, "pose": "neutral"},
                    {"frame": 20, "pose": "excited"},
                    {"frame": 60, "pose": "pointing"},
                ]
            },
            "duration": 5.0,
            "is_active": True
        },
        {
            "name": "Casual Demo",
            "description": "Casual demonstration of product features",
            "pose_sequence": {
                "type": "demo",
                "keyframes": [
                    {"frame": 0, "pose": "standing"},
                    {"frame": 40, "pose": "gesturing"},
                ]
            },
            "duration": 4.0,
            "is_active": True
        },
        {
            "name": "Excited Reveal",
            "description": "Enthusiastic product reveal",
            "pose_sequence": {
                "type": "reveal",
                "keyframes": [
                    {"frame": 0, "pose": "hidden"},
                    {"frame": 30, "pose": "reveal"},
                    {"frame": 60, "pose": "celebrate"},
                ]
            },
            "duration": 5.0,
            "is_active": True
        },
        {
            "name": "Simple Wave",
            "description": "Model waves while holding product",
            "pose_sequence": {
                "type": "wave",
                "keyframes": [
                    {"frame": 0, "pose": "neutral"},
                    {"frame": 30, "pose": "wave_up"},
                    {"frame": 60, "pose": "wave_down"},
                ]
            },
            "duration": 4.0,
            "is_active": True
        }
    ]

    for action_data in actions:
        existing = db.query(Action).filter(Action.name == action_data["name"]).first()
        if not existing:
            action = Action(**action_data)
            db.add(action)
            print(f"✓ Added action: {action_data['name']}")

    db.commit()


def seed_background_categories(db: Session):
    """Create example background entries"""
    # Note: These are placeholders - you'll need to upload actual image files
    backgrounds = [
        {
            "name": "White Studio",
            "file_path": "/backgrounds/white_studio.jpg",
            "file_url": "/uploads/backgrounds/white_studio.jpg",
            "category": "Studio",
            "is_active": True
        },
        {
            "name": "Modern Office",
            "file_path": "/backgrounds/modern_office.jpg",
            "file_url": "/uploads/backgrounds/modern_office.jpg",
            "category": "Office",
            "is_active": True
        },
        {
            "name": "Outdoor Park",
            "file_path": "/backgrounds/outdoor_park.jpg",
            "file_url": "/uploads/backgrounds/outdoor_park.jpg",
            "category": "Outdoor",
            "is_active": True
        },
        {
            "name": "Cozy Living Room",
            "file_path": "/backgrounds/living_room.jpg",
            "file_url": "/uploads/backgrounds/living_room.jpg",
            "category": "Home",
            "is_active": True
        },
        {
            "name": "Minimalist Background",
            "file_path": "/backgrounds/minimalist.jpg",
            "file_url": "/uploads/backgrounds/minimalist.jpg",
            "category": "Studio",
            "is_active": True
        }
    ]

    for bg_data in backgrounds:
        existing = db.query(Background).filter(Background.name == bg_data["name"]).first()
        if not existing:
            background = Background(**bg_data)
            db.add(background)
            print(f"✓ Added background: {bg_data['name']}")

    db.commit()


def main():
    print("🌱 Seeding database with initial data...\n")

    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Seed actions
        print("Adding actions...")
        seed_actions(db)

        # Seed backgrounds
        print("\nAdding background categories...")
        seed_background_categories(db)

        print("\n✅ Database seeded successfully!")
        print("\nNote: Background images are placeholders.")
        print("Upload actual background images using the API:")
        print("  POST /api/backgrounds")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
