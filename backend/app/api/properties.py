"""Кыймылсыз мүлк жарнамалары Blueprint'и — /api/properties."""
from flask import Blueprint, request

from app.extensions import db
from app.models import Property, PropertyImage
from app.utils.http import error, iso, success

properties_bp = Blueprint("properties", __name__, url_prefix="/properties")


def _property_dict(prop, include_owner=False):
    """Property моделинин көрүнүшү."""
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
        "published_at": iso(prop.published_at),
        "created_at": iso(prop.created_at),
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


@properties_bp.get("/ping")
def properties_ping():
    """
    Сервистин ден соолугун текшерүү.

    Blueprint'тин иштээрин ырастоочу эң жөнөкөй эндпоинт.
    ---
    tags:
      - properties
    summary: Properties сервисинин ден соолугун текшерүү
    description: Жөнөкөй ping чакуу — properties blueprint'инин катталгандыгын көрсөтөт.
    responses:
      200:
        description: Сервис иштеп жатат
        schema:
          type: object
          properties:
            service:
              type: string
              example: properties
            status:
              type: string
              example: ok
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    return success({"service": "properties", "status": "ok"})


@properties_bp.get("")
def list_properties():
    """
    Жарнамалардын тизмеси (издөө/фильтр).

    `deal_type`, `property_type`, `city_id`, `category_id`, `min_price`,
    `max_price` фильтрлери колдонулат. `limit`/`offset` пагинация.
    ---
    tags:
      - properties
    summary: Жарнамалардын тизмеси (издөө)
    parameters:
      - name: deal_type
        in: query
        type: string
        required: false
        enum: [sale, rent]
        description: Сатуу же ижара
      - name: property_type
        in: query
        type: string
        required: false
        enum: [apartment, house, land, commercial]
      - name: city_id
        in: query
        type: integer
        required: false
      - name: category_id
        in: query
        type: integer
        required: false
      - name: min_price
        in: query
        type: number
        required: false
      - name: max_price
        in: query
        type: number
        required: false
      - name: limit
        in: query
        type: integer
        required: false
        default: 20
      - name: offset
        in: query
        type: integer
        required: false
        default: 0
    responses:
      200:
        description: Жарнамалардын тизмеси
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  price:
                    type: string
                  deal_type:
                    type: string
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except (TypeError, ValueError):
        return error("limit/offset сан болушу керек", 400)

    query = Property.query.filter(Property.status == "active")
    if request.args.get("deal_type") in ("sale", "rent"):
        query = query.filter(Property.deal_type == request.args["deal_type"])
    if request.args.get("property_type"):
        query = query.filter(Property.property_type == request.args["property_type"])
    if request.args.get("city_id"):
        query = query.filter(Property.city_id == request.args["city_id"])
    if request.args.get("category_id"):
        query = query.filter(Property.category_id == request.args["category_id"])
    if request.args.get("min_price"):
        query = query.filter(Property.price >= request.args["min_price"])
    if request.args.get("max_price"):
        query = query.filter(Property.price <= request.args["max_price"])

    properties = (
        query.order_by(Property.created_at.desc()).limit(limit).offset(offset).all()
    )
    return success([_property_dict(p) for p in properties])


@properties_bp.get("/<int:property_id>")
def get_property(property_id):
    """
    Жеке жарнаманын маалыматы.

    Ар бир чакууда `view_count` бирге көбөйөт.
    ---
    tags:
      - properties
    summary: Жеке жарнама (көрүү эсептелет)
    parameters:
      - name: property_id
        in: path
        type: integer
        required: true
        description: Жарнаманын ID
    responses:
      200:
        description: Жарнама табылды
        schema:
          type: object
          properties:
            status:
              type: string
            data:
              type: object
              properties:
                id:
                  type: integer
                title:
                  type: string
                price:
                  type: string
                view_count:
                  type: integer
      404:
        description: Жарнама табылган жок
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    prop = Property.query.get(property_id)
    if not prop or prop.status != "active":
        return error("Жарнама табылган жок", 404)

    prop.increment_view()
    db.session.commit()
    return success(_property_dict(prop, include_owner=True))


@properties_bp.post("")
def create_property():
    """
    Жаңы жарнама түзүү.

    Мисал базасы үчүн `owner_id` түздөн-түз берилет (аутентификация
    кийинки кадамда кошулат). Милдеттүү: title, price, owner_id,
    category_id, city_id.
    ---
    tags:
      - properties
    summary: Жаңы жарнама түзүү
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - price
            - owner_id
            - category_id
            - city_id
          properties:
            title:
              type: string
              example: 2 бөлмөлүү батир
            description:
              type: string
            price:
              type: number
              example: 95000
            currency:
              type: string
              default: KGS
            deal_type:
              type: string
              enum: [sale, rent]
              default: sale
            property_type:
              type: string
              default: apartment
            owner_id:
              type: integer
            category_id:
              type: integer
            city_id:
              type: integer
            district_id:
              type: integer
            rooms:
              type: integer
    responses:
      201:
        description: Жарнама түзүлдү
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
            data:
              type: object
              properties:
                id:
                  type: integer
                title:
                  type: string
      400:
        description: Валидация катасы (милдеттүү талаа жетпейт)
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    data = request.get_json(silent=True) or {}
    required = ["title", "price", "owner_id", "category_id", "city_id"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Милдеттүү талаалар: {', '.join(missing)}", 400)

    prop = Property(
        title=data["title"],
        description=data.get("description"),
        price=data["price"],
        currency=data.get("currency", "KGS"),
        deal_type=data.get("deal_type", "sale"),
        property_type=data.get("property_type", "apartment"),
        owner_id=data["owner_id"],
        category_id=data["category_id"],
        city_id=data["city_id"],
        district_id=data.get("district_id"),
        rooms=data.get("rooms"),
        floor=data.get("floor"),
        floor_total=data.get("floor_total"),
        address=data.get("address"),
        status=data.get("status", "active"),
    )
    db.session.add(prop)
    db.session.commit()
    return success(_property_dict(prop), status=201, message="Жарнама түзүлдү")