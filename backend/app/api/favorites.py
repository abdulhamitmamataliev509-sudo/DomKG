"""Тандоолор (избранное) Blueprint'и — /api/favorites."""
from flask import Blueprint, request

from app.extensions import db
from app.models import Favorite, Property, User
from app.utils.http import error, iso, success

favorites_bp = Blueprint("favorites", __name__, url_prefix="/favorites")


@favorites_bp.get("/ping")
def favorites_ping():
    """
    Сервистин ден соолугун текшерүү.

    Blueprint'тин иштээрин ырастоочу эң жөнөкөй эндпоинт.
    ---
    tags:
      - favorites
    summary: Favorites сервисинин ден соолугун текшерүү
    description: Жөнөкөй ping чакуу — favorites blueprint'инин катталгандыгын көрсөтөт.
    responses:
      200:
        description: Сервис иштеп жатат
        schema:
          type: object
          properties:
            service:
              type: string
              example: favorites
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
    return success({"service": "favorites", "status": "ok"})


@favorites_bp.get("")
def list_favorites():
    """
    Колдонуучунун тандоолорунун тизмеси.

    `user_id` аргументи аркылуу кайсы колдонуучунун тандоолору
    көрсөтүлөрү аныкталат (аутентификация кийинки кадамда).
    ---
    tags:
      - favorites
    summary: Колдонуучунун тандоолору
    parameters:
      - name: user_id
        in: query
        type: integer
        required: true
        description: Колдонуучунун ID
    responses:
      200:
        description: Тандоолордун тизмеси
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
                  property_id:
                    type: integer
                  created_at:
                    type: string
      400:
        description: user_id көрсөтүлбөгөн
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
    user_id = request.args.get("user_id")
    if not user_id:
        return error("user_id талап кылынат", 400)

    favorites = (
        Favorite.query.filter_by(user_id=user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return success(
        [
            {
                "id": f.id,
                "property_id": f.property_id,
                "created_at": iso(f.created_at),
            }
            for f in favorites
        ]
    )


@favorites_bp.post("")
def add_favorite():
    """
    Мүлктү избранноеге кошуу.

    `user_id` жана `property_id` бирге уникалдуу болушу керек.
    ---
    tags:
      - favorites
    summary: Тандоого кошуу
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - property_id
          properties:
            user_id:
              type: integer
            property_id:
              type: integer
    responses:
      201:
        description: Тандоого кошулду
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      400:
        description: Валидация катасы / кайталанган тандоо
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      404:
        description: Колдонуучу же мүлк табылган жок
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
    user_id = data.get("user_id")
    property_id = data.get("property_id")

    if not user_id or not property_id:
        return error("user_id жана property_id милдеттүү", 400)
    if not User.query.get(user_id) or not Property.query.get(property_id):
        return error("Колдонуучу же мүлк табылган жок", 404)
    if Favorite.query.filter_by(user_id=user_id, property_id=property_id).first():
        return error("Бул мүлк буга чейин тандоодо бар", 400)

    fav = Favorite(user_id=user_id, property_id=property_id)
    db.session.add(fav)
    db.session.commit()
    return success({"id": fav.id}, status=201, message="Тандоого кошулду")


@favorites_bp.delete("/<int:property_id>")
def remove_favorite(property_id):
    """
    Мүлктү избранноеден алып салуу.

    `user_id` аргументи керек — кийинки кадамда JWT'тен алынат.
    ---
    tags:
      - favorites
    summary: Тандоодон алып салуу
    parameters:
      - name: property_id
        in: path
        type: integer
        required: true
        description: Мүлктүн ID
      - name: user_id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Тандоодон алынды
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      400:
        description: user_id көрсөтүлбөгөн
        schema:
          type: object
          properties:
            status:
              type: string
      404:
        description: Тандоо табылган жок
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
    user_id = request.args.get("user_id")
    if not user_id:
        return error("user_id талап кылынат", 400)

    fav = Favorite.query.filter_by(user_id=user_id, property_id=property_id).first()
    if not fav:
        return error("Тандоо табылган жок", 404)

    db.session.delete(fav)
    db.session.commit()
    return success(message="Тандоодон алынды")