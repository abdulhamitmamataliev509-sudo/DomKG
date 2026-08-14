"""Тандоолор (избранное) Blueprint'и — /api/favorites."""
from flask import Blueprint, g, request

from app.decorators import active_jwt_required
from app.extensions import db
from app.models import Favorite, Property
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
@active_jwt_required
def list_favorites():
    """
    Колдонуучунун тандоолорунун тизмеси (JWT'тен аныкталат).
    ---
    tags:
      - favorites
    summary: Колдонуучунун тандоолору
    security:
      - Bearer: []
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
      401:
        description: Аутентификация талап
      500:
        description: Сервер катасы
        schema:
          type: object
          properties:
            status:
              type: string
    """
    favorites = (
        Favorite.query.filter_by(user_id=g.current_user.id)
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
@active_jwt_required
def add_favorite():
    """
    Мүлктү избранноеге кошуу (өзүнүн тандоосуна).

    Колдонуучу JWT'тен аныкталат; `property_id` гана кабыл алынат.
    ---
    tags:
      - favorites
    summary: Тандоого кошуу
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - property_id
          properties:
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
      401:
        description: Аутентификация талап
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      404:
        description: Мүлк табылган жок
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
    property_id = data.get("property_id")
    if not property_id:
        return error("property_id милдеттүү", 400)
    if not Property.query.get(property_id):
        return error("Мүлк табылган жок", 404)
    if Favorite.query.filter_by(
        user_id=g.current_user.id, property_id=property_id
    ).first():
        return error("Бул мүлк буга чейин тандоодо бар", 400)

    fav = Favorite(user_id=g.current_user.id, property_id=property_id)
    db.session.add(fav)
    db.session.commit()
    return success({"id": fav.id}, status=201, message="Тандоого кошулду")


@favorites_bp.delete("/<int:property_id>")
@active_jwt_required
def remove_favorite(property_id):
    """
    Мүлктү избранноеден алып салуу (өзүнүн тандоосунан).

    Колдонуучу JWT'тен аныкталат.
    ---
    tags:
      - favorites
    summary: Тандоодон алып салуу
    security:
      - Bearer: []
    parameters:
      - name: property_id
        in: path
        type: integer
        required: true
        description: Мүлктүн ID
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
      401:
        description: Аутентификация талап
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
    fav = Favorite.query.filter_by(
        user_id=g.current_user.id, property_id=property_id
    ).first()
    if not fav:
        return error("Тандоо табылган жок", 404)

    db.session.delete(fav)
    db.session.commit()
    return success(message="Тандоодон алынды")