"""JWT-негизделген авторизация декораторлору.

- active_jwt_required: JWT + активдүү колдонуучу талап
  (Anonymous -> 401, inactive -> 401). Колдонуучуну ``g.current_user``
  кылып коёт.
- admin_required: JWT + активдүү + админ
  (Anonymous -> 401, authenticated non-admin -> 403, admin -> өтөт).
- is_admin / get_optional_active_user: жардамчы функциялар.
"""
from functools import wraps

from flask import g
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request

from app.extensions import db
from app.models import Admin, User
from app.utils.http import error


def _load_active_user():
    """Токендин identity'синен активдүү колдонуучуну жүктөйт (жок болсо None)."""
    identity = get_jwt_identity()
    if not identity:
        return None
    try:
        user = db.session.get(User, int(identity))
    except (TypeError, ValueError):
        return None
    if user is None or not user.is_active:
        return None
    return user


def active_jwt_required(fn):
    """Активдүү, аутентификацияланган колдонуучу гана өтөт."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = _load_active_user()
        if user is None:
            return error("Аутентификация талап кылынат же аккаунт өчүрүлгөн", 401)
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """Активдүү админ гана өтөт. Non-admin -> 403."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = _load_active_user()
        if user is None:
            return error("Аутентификация талап кылынат же аккаунт өчүрүлгөн", 401)
        admin = Admin.query.filter_by(user_id=user.id, is_active=True).first()
        if admin is None:
            return error("Админ укугу талап кылынат", 403)
        g.current_user = user
        g.current_admin = admin
        return fn(*args, **kwargs)
    return wrapper


def is_admin(user):
    """Колдонуучу активдүү админ беле?"""
    if user is None:
        return False
    return Admin.query.filter_by(user_id=user.id, is_active=True).first() is not None


def get_optional_active_user():
    """Optional JWT: токен бар жана колдонуучу активдүү болсо кайтарат,
    жок болсо None (ката кайтарылбайт — публичный эндпоинттер үчүн)."""
    try:
        verify_jwt_in_request(optional=True)
    except Exception:
        return None
    return _load_active_user()
