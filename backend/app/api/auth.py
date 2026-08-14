"""Аутентификация Blueprint'и — /api/auth.

Катталуу, кирүү жана учурдагы колдонуучу операциялары.
"""
from flask import Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User
from app.utils.http import error, iso, success

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _user_dict(user):
    """User моделинин ачык (public) көрүнүшү."""
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


@auth_bp.get("/ping")
def auth_ping():
    """
    Сервистин ден соолугун текшерүү.

    Blueprint'тин иштээрин ырастоочу эң жөнөкөй эндпоинт.
    ---
    tags:
      - auth
    summary: Auth сервисинин ден соолугун текшерүү
    description: Жөнөкөй ping чакуу — auth blueprint'инин катталгандыгын көрсөтөт.
    responses:
      200:
        description: Сервис иштеп жатат
        schema:
          type: object
          properties:
            service:
              type: string
              example: auth
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
              example: error
    """
    return success({"service": "auth", "status": "ok"})


@auth_bp.post("/register")
def register():
    """
    Жаңы колдонуучуну катталуу.

    Электрондук почта, пароль жана ысым милдеттүү. Пароль
    hash'талып сакталат; email уникалдуу болушу керек.
    ---
    tags:
      - auth
    summary: Жаңы колдонуучу каттоо
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - first_name
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              format: password
              example: strong-pass-123
            first_name:
              type: string
              example: Айбек
            last_name:
              type: string
              example: Асанов
            phone:
              type: string
              example: "+996700123456"
    responses:
      201:
        description: Колдонуучу ийгиликтүү катталды
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
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
      400:
        description: Валидация катасы (милдеттүү талаа жетишпейт)
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
            message:
              type: string
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    first_name = (data.get("first_name") or "").strip()

    if not email or not password or not first_name:
        return error("email, password жана first_name милдеттүү талаалар", 400)
    if len(password) < 6:
        return error("Пароль кеминде 6 белгиден турушу керек", 400)

    if User.query.filter_by(email=email).first():
        return error("Бул email менен колдонуучу бар", 400)

    user = User(
        email=email,
        phone=(data.get("phone") or "").strip() or None,
        first_name=first_name,
        last_name=(data.get("last_name") or "").strip() or None,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return success(_user_dict(user), status=201, message="Колдонуучу катталды")


@auth_bp.post("/login")
def login():
    """
    Колдонуучуну киргизүү.

    Email жана пароль текшерилет. JWT токен кийинки кадамда ишке
    ашат — азырынча колдонуучунун маалыматы кайтарылат.
    ---
    tags:
      - auth
    summary: Системага кирүү
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              format: password
              example: strong-pass-123
    responses:
      200:
        description: Ийгиликтүү кирүү
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
                email:
                  type: string
                first_name:
                  type: string
      400:
        description: Валидация катасы (талаа жет пейт)
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      401:
        description: Туура эмес email же пароль
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
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error("email жана password милдеттүү", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return error("Email же пароль туура эмес", 401)

    return success(_user_dict(user), message="Кирүү ийгиликтүү")


@auth_bp.get("/me")
def me():
    """
    Учурдагы колдонуучунун профили.

    Аутентификация (JWT) кийинки кадамда ишке ашат; азырынча 401
    кайтарат.
    ---
    tags:
      - auth
    summary: Учурдагы колдонуучунун маалыматы
    description: Аутентификация али ишке ашкан эмес — 401 кайтарылат.
    responses:
      401:
        description: Аутентификация керек (JWT кийинки кадамда)
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
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
    return error("Аутентификация (JWT) кийинки кадамда ишке ашат", 401)