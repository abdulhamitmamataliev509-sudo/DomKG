"""Idempotent development seed data for the DomKG PostgreSQL database.

This script uses the real Flask application factory and the SQLAlchemy db instance
already configured in the project. It inserts a small, realistic development
catalog for categories, cities, districts, and properties while skipping anything
that already exists.

Important constraints:
- DO NOT change the database schema
- DO NOT create a new database
- DO NOT delete existing data
- DO NOT modify migrations
- DO NOT invent unsupported columns or relationships
- Safe to run multiple times
"""

from __future__ import annotations

import re
import sys
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from app.extensions import db
from app.models import Category, City, District, Property, PropertyImage, User


CATEGORY_SEED = [
    {"name": "Батир", "slug": "batir"},
    {"name": "Үй", "slug": "uy"},
    {"name": "Жер тилкеси", "slug": "jer-tilkesi"},
    {"name": "Коммерциялык мүлк", "slug": "kommerciyalik-mulk"},
    {"name": "Коттедж", "slug": "kottedzh"},
    {"name": "Дача", "slug": "dacha"},
    {"name": "Гараж", "slug": "garazh"},
    {"name": "Кеңсе", "slug": "kenseshe"},
    {"name": "Дүкөн", "slug": "dukon"},
    {"name": "Өндүрүш имараты", "slug": "ondurush-imaraty"},
    {"name": "Кампа", "slug": "kampa"},
    {"name": "Башка", "slug": "bashka"},
]

CITY_SEED = [
    {"name": "Bishkek", "slug": "bishkek"},
    {"name": "Osh", "slug": "osh"},
    {"name": "Jalal-Abad", "slug": "jalal-abad"},
    {"name": "Karakol", "slug": "karakol"},
]

DISTRICT_SEED = [
    {"city_name": "Bishkek", "name": "Lenin", "slug": "lenin"},
    {"city_name": "Bishkek", "name": "Sverdlov", "slug": "sverdlov"},
    {"city_name": "Bishkek", "name": "Pervomaysky", "slug": "pervomaysky"},
    {"city_name": "Osh", "name": "Lenin", "slug": "osh-lenin"},
    {"city_name": "Osh", "name": "Sovetsky", "slug": "osh-sovetsky"},
    {"city_name": "Jalal-Abad", "name": "Central", "slug": "jalal-abad-central"},
    {"city_name": "Jalal-Abad", "name": "Arslanbob", "slug": "arslanbob"},
    {"city_name": "Karakol", "name": "Lenin", "slug": "karakol-lenin"},
    {"city_name": "Karakol", "name": "Central", "slug": "karakol-central"},
]

PROPERTY_SEED = [
    {
        "title": "2-bedroom apartment in downtown Bishkek",
        "category_name": "Батир",
        "city_name": "Bishkek",
        "district_name": "Lenin",
        "owner_email": "user@example@gmail.com",
        "deal_type": "sale",
        "property_type": "apartment",
        "price": "98000",
        "currency": "KGS",
        "rooms": 2,
        "floor": 5,
        "floor_total": 9,
        "bathrooms": 1,
        "area_total": "68.50",
        "area_living": "45.00",
        "area_kitchen": "12.00",
        "has_parking": True,
        "has_balcony": True,
        "has_furniture": False,
        "year_built": 2012,
        "address": "Lenin Street 18, Bishkek",
        "latitude": "42.8746",
        "longitude": "74.6121",
        "status": "active",
        "is_featured": True,
        "images": [
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80",
        ],
    },
    {
        "title": "Modern 3-room apartment with balcony",
        "category_name": "Батир",
        "city_name": "Bishkek",
        "district_name": "Sverdlov",
        "owner_email": "abdulhamitmamataliev509@gmail.com",
        "deal_type": "sale",
        "property_type": "apartment",
        "price": "125000",
        "currency": "KGS",
        "rooms": 3,
        "floor": 7,
        "floor_total": 12,
        "bathrooms": 2,
        "area_total": "92.00",
        "area_living": "67.00",
        "area_kitchen": "14.00",
        "has_parking": True,
        "has_balcony": True,
        "has_furniture": True,
        "year_built": 2018,
        "address": "Sverdlov Street 45, Bishkek",
        "latitude": "42.8750",
        "longitude": "74.5980",
        "status": "active",
        "is_featured": False,
        "images": [
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1200&q=80",
        ],
    },
    {
        "title": "Family house near the city park",
        "category_name": "Үй",
        "city_name": "Bishkek",
        "district_name": "Pervomaysky",
        "owner_email": "user@example@gmail.com",
        "deal_type": "sale",
        "property_type": "house",
        "price": "175000",
        "currency": "USD",
        "rooms": 4,
        "floor": 2,
        "floor_total": 2,
        "bathrooms": 2,
        "area_total": "180.00",
        "area_living": "120.00",
        "area_kitchen": "18.00",
        "has_parking": True,
        "has_balcony": False,
        "has_furniture": False,
        "year_built": 2015,
        "address": "Pervomayskaya 12, Bishkek",
        "latitude": "42.8660",
        "longitude": "74.6300",
        "status": "active",
        "is_featured": True,
        "images": [
            "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1200&q=80",
        ],
    },
    {
        "title": "Land plot for residential construction",
        "category_name": "Жер тилкеси",
        "city_name": "Osh",
        "district_name": "Lenin",
        "owner_email": "abdulhamitmamataliev509@gmail.com",
        "deal_type": "sale",
        "property_type": "land",
        "price": "50000",
        "currency": "KGS",
        "rooms": None,
        "floor": None,
        "floor_total": None,
        "bathrooms": 0,
        "area_total": "600.00",
        "area_living": None,
        "area_kitchen": None,
        "has_parking": False,
        "has_balcony": False,
        "has_furniture": False,
        "year_built": None,
        "address": "Lenin District, Osh",
        "latitude": "40.5283",
        "longitude": "72.7985",
        "status": "active",
        "is_featured": False,
        "images": [],
    },
    {
        "title": "Office space in city center",
        "category_name": "Кеңсе",
        "city_name": "Osh",
        "district_name": "Sovetsky",
        "owner_email": "user@example@gmail.com",
        "deal_type": "rent",
        "property_type": "commercial",
        "price": "4200",
        "currency": "KGS",
        "rooms": 4,
        "floor": 2,
        "floor_total": 4,
        "bathrooms": 2,
        "area_total": "110.00",
        "area_living": None,
        "area_kitchen": None,
        "has_parking": True,
        "has_balcony": False,
        "has_furniture": False,
        "year_built": 2010,
        "address": "Sovetsky Avenue 20, Osh",
        "latitude": "40.5293",
        "longitude": "72.7997",
        "status": "active",
        "is_featured": True,
        "images": [
            "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80",
        ],
    },
    {
        "title": "Retail shop in busy district",
        "category_name": "Дүкөн",
        "city_name": "Jalal-Abad",
        "district_name": "Central",
        "owner_email": "abdulhamitmamataliev509@gmail.com",
        "deal_type": "sale",
        "property_type": "commercial",
        "price": "96000",
        "currency": "KGS",
        "rooms": 2,
        "floor": 1,
        "floor_total": 2,
        "bathrooms": 1,
        "area_total": "75.00",
        "area_living": None,
        "area_kitchen": None,
        "has_parking": True,
        "has_balcony": False,
        "has_furniture": False,
        "year_built": 2009,
        "address": "Central Market Street, Jalal-Abad",
        "latitude": "40.9334",
        "longitude": "73.0006",
        "status": "active",
        "is_featured": False,
        "images": [
            "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1200&q=80",
        ],
    },
    {
        "title": "Cottage with garden and terrace",
        "category_name": "Коттедж",
        "city_name": "Jalal-Abad",
        "district_name": "Arslanbob",
        "owner_email": "user@example@gmail.com",
        "deal_type": "sale",
        "property_type": "house",
        "price": "150000",
        "currency": "USD",
        "rooms": 5,
        "floor": 2,
        "floor_total": 2,
        "bathrooms": 2,
        "area_total": "220.00",
        "area_living": "150.00",
        "area_kitchen": "20.00",
        "has_parking": True,
        "has_balcony": True,
        "has_furniture": True,
        "year_built": 2017,
        "address": "Arslanbob Road 18, Jalal-Abad",
        "latitude": "40.9294",
        "longitude": "73.0037",
        "status": "active",
        "is_featured": True,
        "images": [
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
        ],
    },
    {
        "title": "Spacious 1-bedroom apartment for rent",
        "category_name": "Батир",
        "city_name": "Karakol",
        "district_name": "Lenin",
        "owner_email": "abdulhamitmamataliev509@gmail.com",
        "deal_type": "rent",
        "property_type": "apartment",
        "price": "18000",
        "currency": "KGS",
        "rooms": 1,
        "floor": 2,
        "floor_total": 5,
        "bathrooms": 1,
        "area_total": "42.00",
        "area_living": "28.00",
        "area_kitchen": "8.00",
        "has_parking": False,
        "has_balcony": True,
        "has_furniture": True,
        "year_built": 2014,
        "address": "Lenin Street 7, Karakol",
        "latitude": "42.4900",
        "longitude": "78.3930",
        "status": "active",
        "is_featured": False,
        "images": [
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
        ],
    },
    {
        "title": "Garage with storage and access",
        "category_name": "Гараж",
        "city_name": "Karakol",
        "district_name": "Central",
        "owner_email": "user@example@gmail.com",
        "deal_type": "sale",
        "property_type": "commercial",
        "price": "22000",
        "currency": "KGS",
        "rooms": None,
        "floor": None,
        "floor_total": None,
        "bathrooms": 0,
        "area_total": "24.00",
        "area_living": None,
        "area_kitchen": None,
        "has_parking": True,
        "has_balcony": False,
        "has_furniture": False,
        "year_built": 2005,
        "address": "Central District, Karakol",
        "latitude": "42.4908",
        "longitude": "78.3943",
        "status": "active",
        "is_featured": False,
        "images": [],
    },
    {
        "title": "Production facility in industrial zone",
        "category_name": "Өндүрүш имараты",
        "city_name": "Bishkek",
        "district_name": "Sverdlov",
        "owner_email": "abdulhamitmamataliev509@gmail.com",
        "deal_type": "rent",
        "property_type": "commercial",
        "price": "7800",
        "currency": "KGS",
        "rooms": 6,
        "floor": 1,
        "floor_total": 1,
        "bathrooms": 2,
        "area_total": "420.00",
        "area_living": None,
        "area_kitchen": None,
        "has_parking": True,
        "has_balcony": False,
        "has_furniture": False,
        "year_built": 2007,
        "address": "Industrial Boulevard 5, Bishkek",
        "latitude": "42.8535",
        "longitude": "74.6201",
        "status": "active",
        "is_featured": True,
        "images": [
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
        ],
    },
]


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "")).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "item"


def safe_decimal(value):
    return Decimal(str(value)) if value is not None else None


def find_user_by_email(email: str):
    return User.query.filter_by(email=email, is_active=True).first()


def seed_categories():
    inserted = 0
    skipped = 0
    for index, item in enumerate(CATEGORY_SEED, start=1):
        name = item["name"]
        slug = item["slug"]
        existing = Category.query.filter(db.func.lower(Category.name) == name.lower()).first()
        if existing is not None:
            skipped += 1
            continue
        if Category.query.filter_by(slug=slug).first() is not None:
            skipped += 1
            continue
        category = Category(name=name, slug=slug, sort_order=index, description=f"Seed category: {name}", is_active=True)
        db.session.add(category)
        inserted += 1
    return inserted, skipped


def seed_cities():
    inserted = 0
    skipped = 0
    for index, city in enumerate(CITY_SEED, start=1):
        existing = City.query.filter(
            db.func.lower(City.name) == city["name"].lower()
        ).first()
        if existing is not None:
            skipped += 1
            continue
        slug = city["slug"] or slugify(city["name"])
        if City.query.filter_by(slug=slug).first() is not None:
            skipped += 1
            continue
        db.session.add(City(name=city["name"], slug=slug, sort_order=index, is_active=True))
        inserted += 1
    return inserted, skipped


def seed_districts():
    inserted = 0
    skipped = 0
    for index, district in enumerate(DISTRICT_SEED, start=1):
        city = City.query.filter(db.func.lower(City.name) == district["city_name"].lower()).first()
        if city is None:
            continue
        existing = District.query.filter_by(city_id=city.id, slug=district["slug"]).first()
        if existing is not None:
            skipped += 1
            continue
        existing_name = District.query.filter_by(city_id=city.id, name=district["name"]).first()
        if existing_name is not None:
            skipped += 1
            continue
        district_obj = District(
            city_id=city.id,
            name=district["name"],
            slug=district["slug"],
            sort_order=index,
            is_active=True,
        )
        db.session.add(district_obj)
        inserted += 1
    return inserted, skipped


def seed_properties():
    inserted = 0
    skipped = 0
    owners = User.query.filter_by(is_active=True).order_by(User.id).all()
    if not owners:
        raise RuntimeError("No active users found. Seed requires at least one active user in the database.")

    for item in PROPERTY_SEED:
        owner = find_user_by_email(item["owner_email"]) or owners[0]
        category = Category.query.filter(db.func.lower(Category.name) == item["category_name"].lower()).first()
        city = City.query.filter(db.func.lower(City.name) == item["city_name"].lower()).first()
        if category is None or city is None:
            continue
        district_name = item.get("district_name")
        district = None
        if district_name:
            district = District.query.filter_by(city_id=city.id, name=district_name).first()

        existing = Property.query.filter_by(title=item["title"], owner_id=owner.id).first()
        if existing is not None:
            skipped += 1
            continue

        prop = Property(
            title=item["title"],
            description=f"Seed development listing for {item['title']}",
            owner_id=owner.id,
            category_id=category.id,
            city_id=city.id,
            district_id=district.id if district else None,
            deal_type=item["deal_type"],
            property_type=item["property_type"],
            price=safe_decimal(item["price"]),
            price_per_m2=(safe_decimal(item["price"]) / safe_decimal(item["area_total"])) if item.get("area_total") else None,
            currency=item.get("currency", "KGS"),
            area_total=safe_decimal(item.get("area_total")),
            area_living=safe_decimal(item.get("area_living")),
            area_kitchen=safe_decimal(item.get("area_kitchen")),
            rooms=item.get("rooms"),
            floor=item.get("floor"),
            floor_total=item.get("floor_total"),
            bathrooms=item.get("bathrooms", 1),
            year_built=item.get("year_built"),
            has_parking=bool(item.get("has_parking", False)),
            has_balcony=bool(item.get("has_balcony", False)),
            has_furniture=bool(item.get("has_furniture", False)),
            address=item.get("address"),
            latitude=safe_decimal(item.get("latitude")),
            longitude=safe_decimal(item.get("longitude")),
            status=item.get("status", "active"),
            is_featured=bool(item.get("is_featured", False)),
            view_count=0,
            published_at=datetime.now(timezone.utc),
        )
        db.session.add(prop)
        db.session.flush()

        for index, image_url in enumerate(item.get("images") or [], start=1):
            db.session.add(
                PropertyImage(
                    property_id=prop.id,
                    image_url=image_url,
                    alt_text=item["title"],
                    is_primary=(index == 1),
                    sort_order=index,
                )
            )

        inserted += 1
    return inserted, skipped


def main():
    app = create_app()
    with app.app_context():
        summary = {
            "categories_inserted": 0,
            "categories_skipped": 0,
            "cities_inserted": 0,
            "cities_skipped": 0,
            "districts_inserted": 0,
            "districts_skipped": 0,
            "properties_inserted": 0,
            "properties_skipped": 0,
            "property_images_inserted": 0,
            "property_images_skipped": 0,
        }

        try:
            categories_inserted, categories_skipped = seed_categories()
            summary["categories_inserted"] = categories_inserted
            summary["categories_skipped"] = categories_skipped

            cities_inserted, cities_skipped = seed_cities()
            summary["cities_inserted"] = cities_inserted
            summary["cities_skipped"] = cities_skipped

            districts_inserted, districts_skipped = seed_districts()
            summary["districts_inserted"] = districts_inserted
            summary["districts_skipped"] = districts_skipped

            properties_inserted, properties_skipped = seed_properties()
            summary["properties_inserted"] = properties_inserted
            summary["properties_skipped"] = properties_skipped

            property_images_inserted = PropertyImage.query.count()
            summary["property_images_inserted"] = property_images_inserted
            summary["property_images_skipped"] = 0

            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            print(f"SEED FAILED: {exc}")
            raise

        total_skipped = (
            summary["categories_skipped"]
            + summary["cities_skipped"]
            + summary["districts_skipped"]
            + summary["properties_skipped"]
        )

        print("SEED SUMMARY")
        print(f"categories inserted: {summary['categories_inserted']}")
        print(f"categories skipped: {summary['categories_skipped']}")
        print(f"cities inserted: {summary['cities_inserted']}")
        print(f"cities skipped: {summary['cities_skipped']}")
        print(f"districts inserted: {summary['districts_inserted']}")
        print(f"districts skipped: {summary['districts_skipped']}")
        print(f"properties inserted: {summary['properties_inserted']}")
        print(f"properties skipped: {summary['properties_skipped']}")
        print(f"property images inserted: {summary['property_images_inserted']}")
        print(f"property images skipped: {summary['property_images_skipped']}")
        print(f"records skipped because they already existed: {total_skipped}")


if __name__ == "__main__":
    main()
