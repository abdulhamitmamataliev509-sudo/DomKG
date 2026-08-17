from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Property
from app.schemas import PropertyCreateSchema, PropertyUpdateSchema
from app.services import ServiceError


class PropertyService:
    @staticmethod
    def list_properties(query_params):
        query = Property.query.filter(Property.status == "active")
        deal_type = query_params.get("deal_type")
        property_type = query_params.get("property_type")
        city_id = query_params.get("city_id")
        category_id = query_params.get("category_id")
        min_price = query_params.get("min_price")
        max_price = query_params.get("max_price")

        if deal_type in ("sale", "rent"):
            query = query.filter(Property.deal_type == deal_type)
        if property_type:
            query = query.filter(Property.property_type == property_type)
        if city_id:
            query = query.filter(Property.city_id == city_id)
        if category_id:
            query = query.filter(Property.category_id == category_id)
        if min_price is not None:
            try:
                query = query.filter(Property.price >= float(min_price))
            except (TypeError, ValueError):
                raise ServiceError("min_price must be numeric", 400, "VALIDATION_ERROR")
        if max_price is not None:
            try:
                query = query.filter(Property.price <= float(max_price))
            except (TypeError, ValueError):
                raise ServiceError("max_price must be numeric", 400, "VALIDATION_ERROR")

        limit = int(query_params.get("limit", 20))
        offset = int(query_params.get("offset", 0))
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)
        return query.order_by(Property.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def get_property(property_id):
        prop = Property.query.get(property_id)
        if not prop or prop.status != "active":
            raise ServiceError("Property not found", 404, "NOT_FOUND")
        return prop

    @staticmethod
    def create_property(owner, payload):
        data = PropertyCreateSchema().load(payload)
        prop = Property(
            title=data["title"],
            description=data.get("description"),
            deal_type=data.get("deal_type", "sale"),
            property_type=data.get("property_type", "apartment"),
            price=data["price"],
            price_per_m2=data.get("price_per_m2"),
            currency=data.get("currency", "KGS"),
            owner_id=owner.id,
            category_id=data["category_id"],
            city_id=data["city_id"],
            district_id=data.get("district_id"),
            rooms=data.get("rooms"),
            floor=data.get("floor"),
            floor_total=data.get("floor_total"),
            bathrooms=data.get("bathrooms", 1),
            year_built=data.get("year_built"),
            has_parking=data.get("has_parking", False),
            has_balcony=data.get("has_balcony", False),
            has_furniture=data.get("has_furniture", False),
            area_total=data.get("area_total"),
            area_living=data.get("area_living"),
            area_kitchen=data.get("area_kitchen"),
            address=data.get("address"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            status=data.get("status", "active"),
            is_featured=data.get("is_featured", False),
        )
        db.session.add(prop)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ServiceError("Unable to create property", 409, "CONFLICT")
        return prop

    @staticmethod
    def update_property(owner, property_id, payload):
        prop = Property.query.get(property_id)
        if not prop:
            raise ServiceError("Property not found", 404, "NOT_FOUND")
        if prop.owner_id != owner.id:
            raise ServiceError("You can only update your own property", 403, "FORBIDDEN")

        data = PropertyUpdateSchema().load(payload)
        for key, value in data.items():
            setattr(prop, key, value)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ServiceError("Unable to update property", 409, "CONFLICT")
        return prop

    @staticmethod
    def property_dict(prop, include_owner=False):
        data = {
            "id": prop.id,
            "title": prop.title,
            "description": prop.description,
            "deal_type": prop.deal_type,
            "property_type": prop.property_type,
            "price": str(prop.price) if prop.price is not None else None,
            "price_per_m2": str(prop.price_per_m2) if prop.price_per_m2 is not None else None,
            "currency": prop.currency,
            "owner_id": prop.owner_id,
            "category_id": prop.category_id,
            "city_id": prop.city_id,
            "district_id": prop.district_id,
            "rooms": prop.rooms,
            "floor": prop.floor,
            "floor_total": prop.floor_total,
            "area_total": str(prop.area_total) if prop.area_total is not None else None,
            "address": prop.address,
            "latitude": str(prop.latitude) if prop.latitude is not None else None,
            "longitude": str(prop.longitude) if prop.longitude is not None else None,
            "status": prop.status,
            "is_featured": prop.is_featured,
            "view_count": prop.view_count,
            "published_at": prop.published_at.isoformat() if prop.published_at else None,
            "created_at": prop.created_at.isoformat() if prop.created_at else None,
            "images": [
                {
                    "id": img.id,
                    "image_url": img.image_url,
                    "is_primary": img.is_primary,
                    "sort_order": img.sort_order,
                }
                for img in prop.images
            ],
        }
        if include_owner and prop.owner:
            data["owner"] = {
                "id": prop.owner.id,
                "first_name": prop.owner.first_name,
                "last_name": prop.owner.last_name,
                "phone": prop.owner.phone,
            }
        return data
