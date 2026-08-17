"""Кыймылсыз мүлк жарнамалары Blueprint'и — /api/properties."""
from flask import Blueprint, g, request
from marshmallow import ValidationError

from app.decorators import active_jwt_required
from app.extensions import db
from app.models import Property
from app.schemas import PropertyCreateSchema, PropertyUpdateSchema
from app.services import ServiceError
from app.services.property_service import PropertyService
from app.utils.http import error, success

properties_bp = Blueprint("properties", __name__, url_prefix="/properties")


def _property_dict(prop, include_owner=False):
    """Property моделинин көрүнүшү."""
    return PropertyService.property_dict(prop, include_owner=include_owner)


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
        query_params = {
            "deal_type": request.args.get("deal_type"),
            "property_type": request.args.get("property_type"),
            "city_id": request.args.get("city_id"),
            "category_id": request.args.get("category_id"),
            "min_price": request.args.get("min_price"),
            "max_price": request.args.get("max_price"),
            "limit": request.args.get("limit", 20),
            "offset": request.args.get("offset", 0),
        }
        properties = PropertyService.list_properties(query_params)
    except ServiceError as exc:
        return error(exc.message, exc.status_code, exc.code, exc.details)
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
    try:
        prop = PropertyService.get_property(property_id)
    except ServiceError as exc:
        return error(exc.message, exc.status_code, exc.code, exc.details)

    prop.increment_view()
    db.session.commit()
    return success(_property_dict(prop, include_owner=True))


@properties_bp.post("")
@active_jwt_required
def create_property():
    """
    Жаңы жарнама түзүү (аутентификацияланган колдонуучу).

    Ээси (owner) JWT токенден аныкталат — `owner_id` body'ден алынбайт.
    Милдеттүү: title, price, category_id, city_id.
    ---
    tags:
      - properties
    summary: Жаңы жарнама түзүү
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - price
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
      400:
        description: Валидация катасы (милдеттүү талаа жетпейт)
      401:
        description: Аутентификация талап
      500:
        description: Сервер катасы
    """
    try:
        payload = PropertyCreateSchema().load(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return error("Validation failed", 400, "VALIDATION_ERROR", exc.messages)
    try:
        prop = PropertyService.create_property(g.current_user, payload)
    except ServiceError as exc:
        return error(exc.message, exc.status_code, exc.code, exc.details)
    return success(_property_dict(prop), status=201, message="Жарнама түзүлдү")