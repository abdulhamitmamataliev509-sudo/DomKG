"""Аутентификация Blueprint'и — /api/auth.

Катталуу, кирүү, токен жаңылоо, чыгуу жана учурдагы колдонуучу
операциялары ушул жерде жайгашат.
"""
from flask import Blueprint, jsonify

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/ping")
def auth_ping():
    """Blueprint'тин туура катталганын текшерүүчү эндпоинт."""
    return jsonify({"service": "auth", "status": "ok"})


# ---------------------------------------------------------------------------
# Пландалган эндпоинттер (кийинки кадамдарда ишке ашат):
#
#   POST   /auth/register          -> Катталуу (email, password, name)
#   POST   /auth/login             -> Кирип, access/refresh токен алуу
#   POST   /auth/refresh           -> Refresh токен менен access токенди жаңылоо
#   POST   /auth/logout            -> Чыгуу (refresh токенди инвальдациялоо)
#   GET    /auth/me                -> Учурдагы колдонуучунун профили
# ---------------------------------------------------------------------------