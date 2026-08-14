"""Колдонуучулар Blueprint'и — /api/users."""
from flask import Blueprint, request

from app.models import User
from app.utils.http import error, iso, success

users_bp = Blueprint("users", __name__, url_prefix="/users")


def _user_dict(user):
    """User моделинин ачык көрүнүшү."""
    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_verified": user.is_verified,
        "avatar_url": user.avatar_url,
        "created_at": iso(user.created_at),
    }


@users_bp.get("/ping")
def users_ping():
    """
    Сервистин ден соолугун текшерүү.

    Blueprint'тин иштээрин ырастоочу эң жөнөкөй эндпоинт.
    ---
    tags:
      - users
    summary: Users сервисинин ден соолугун текшерүү
    description: Жөнөкөй ping чакуу — users blueprint'инин катталгандыгын көрсөтөт.
    responses:
      200:
        description: Сервис иштеп жатат
        schema:
          type: object
          properties:
            service:
              type: string
              example: users
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
    return success({"service": "users", "status": "ok"})


@users_bp.get("")
def list_users():
    """
    Колдонуучулардын тизмеси (пагинация менен).

    `limit` жана `offset` аргументтери аркылуу баракталат.
    ---
    tags:
      - users
    summary: Колдонуучулардын тизмеси
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 20
        description: Бир барактагы жазуулардын саны (max 100)
      - name: offset
        in: query
        type: integer
        required: false
        default: 0
        description: Баштоо абалы (skip)
    responses:
      200:
        description: Колдонуучулардын тизмеси
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
                  email:
                    type: string
                  first_name:
                    type: string
      400:
        description: Валидация катасы (limit/offset туура эмес)
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
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except (TypeError, ValueError):
        return error("limit/offset сан болушу керек", 400)

    users = User.query.filter_by(is_active=True).limit(limit).offset(offset).all()
    return success([_user_dict(u) for u in users])


@users_bp.get("/<int:user_id>")
def get_user(user_id):
    """
    Жеке колдонуучунун маалыматы.

    Берилген `user_id` менен катталган колдонуучу кайтарылат.
    ---
    tags:
      - users
    summary: Жеке колдонуучу
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: Колдонуучунун ID
    responses:
      200:
        description: Колдонуучу табылды
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
                email:
                  type: string
                first_name:
                  type: string
      404:
        description: Колдонуучу табылган жок
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
    user = User.query.get(user_id)
    if not user:
        return error("Колдонуучу табылган жок", 404)
    return success(_user_dict(user))