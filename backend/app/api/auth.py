"""Аутентификация Blueprint'и — /api/auth.

Катталуу, кирүү, токен жаңылоо жана учурдагы колдонуучу операциялары.
"""
from datetime import datetime, timezone

from flask import Blueprint, current_app, g, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.decorators import active_jwt_required

from app.extensions import db, limiter
from app.models import TokenBlocklist, User
from app.utils.http import error, iso, success

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _revoke_token(jti, token_type, user_id, expires_at):
    """JWT jti'ни denylist'ке кошот — raw токен сакталбайт, минималдуу маалымат."""
    if jti and not TokenBlocklist.query.filter_by(jti=jti).first():
        db.session.add(
            TokenBlocklist(
                jti=jti,
                token_type=token_type,
                user_id=user_id,
                expires_at=expires_at,
            )
        )


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
    ---
    tags:
      - auth
    summary: Auth сервисинин ден соолугун текшерүү
    responses:
      200:
        description: Сервис иштеп жатат
    """
    return success({"service": "auth", "status": "ok"})


@auth_bp.post("/register")
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_REGISTER", "5 per minute"))
def register():
    """
    Жаңы колдонуучуну каттоо.
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

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return success(
        {
            "user": _user_dict(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        status=201,
        message="Колдонуучу катталды",
    )


@auth_bp.post("/login")
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_LOGIN", "10 per minute"))
def login():
    """
    Колдонуучуну киргизүү.
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
      401:
        description: Туура эмес email же пароль
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error("email жана password милдеттүү", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        current_app.logger.warning("Login failed email=%s (bad credentials)", email)
        return error("Email же пароль туура эмес", 401)
    # Деактивацияланган аккаунт кире албайт (колдонуучуну санашоо кылбаш үчүн
    # ошол эле жалпы 401-сообщение кайтарылат).
    if not user.is_active:
        current_app.logger.warning("Login blocked for inactive user id=%s", user.id)
        return error("Email же пароль туура эмес", 401)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    current_app.logger.info("Login success user_id=%s", user.id)
    return success(
        {
            "user": _user_dict(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        message="Кирүү ийгиликтүү",
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """
    Access токенди жаңылоо (Refresh Token аркылуу).
    ---
    tags:
      - auth
    summary: Access токенди жаңылоо
    security:
      - RefreshToken: []
    responses:
      200:
        description: Жаңы access токен берилди
      401:
        description: Refresh токен туура эмес же мөөнөтү өткөн
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id)) if user_id else None
    if user is None or not user.is_active:
        return error("Аккаунт өчүрүлгөн же табылган жок", 401)
    new_access_token = create_access_token(identity=str(user.id))
    return success({"access_token": new_access_token}, message="Токен жаңыланды")


@auth_bp.get("/me")
@active_jwt_required
def me():
    """
    Учурдагы колдонуучунун профили.
    ---
    tags:
      - auth
    summary: Учурдагы колдонуучунун маалыматы
    security:
      - Bearer: []
    responses:
      200:
        description: Учурдагы колдонуучунун маалыматы
      401:
        description: Токен жетпейт же аккаунт өчүрүлгөн
    """
    return success(_user_dict(g.current_user))


@auth_bp.post("/logout")
@active_jwt_required
def logout():
    """
    Чыгуу — refresh токенди (жана учурдагы access токенди) revoked кылат.

    Талап: `Authorization: Bearer <access_token>` + body'де `refresh_token`.
    ---
    tags:
      - auth
    summary: Чыгуу (refresh токенди жокко чыгаруу)
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - refresh_token
          properties:
            refresh_token:
              type: string
              description: Revoked кылынучу refresh токен (login'ден алынган)
    responses:
      200:
        description: Чыгуу ийгиликтүү — refresh жана access revoked
      400:
        description: refresh_token жеткирилген жок
      401:
        description: Аутентификация талап / туура эмес refresh токен
      403:
        description: Refresh токен башка колдонуучуга таандык
    """
    data = request.get_json(silent=True) or {}
    refresh_token = (data.get("refresh_token") or "").strip()
    if not refresh_token:
        return error("refresh_token талап кылынат", 400)

    try:
        decoded = decode_token(refresh_token)
    except Exception:
        current_app.logger.warning("Logout with invalid refresh token user_id=%s", g.current_user.id)
        return error("Refresh токен туура эмес", 401)

    if decoded.get("type") != "refresh":
        return error("Refresh токен керек", 400)
    if str(decoded.get("sub")) != str(g.current_user.id):
        current_app.logger.warning(
            "Logout rejected: refresh token belongs to another user (%s != %s)",
            decoded.get("sub"),
            g.current_user.id,
        )
        return error("Refresh токен учурдагы колдонуучуга таандык эмес", 403)

    access_payload = get_jwt()
    _revoke_token(
        access_payload.get("jti"),
        "access",
        g.current_user.id,
        datetime.fromtimestamp(access_payload["exp"], timezone.utc)
        if access_payload.get("exp")
        else None,
    )
    _revoke_token(
        decoded.get("jti"),
        "refresh",
        g.current_user.id,
        datetime.fromtimestamp(decoded["exp"], timezone.utc)
        if decoded.get("exp")
        else None,
    )
    db.session.commit()
    current_app.logger.info("Logout user_id=%s (access+refresh revoked)", g.current_user.id)
    return success(message="Чыгуу ийгиликтүү — токендер жокко чыгарылды")