"""Колдонуучулар Blueprint'и — /api/users."""
from flask import Blueprint, jsonify

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("/ping")
def users_ping():
    """Blueprint'тин туура катталганын текшерүүчү эндпоинт."""
    return jsonify({"service": "users", "status": "ok"})


# ---------------------------------------------------------------------------
# Пландалган эндпоинттер:
#
#   GET    /users                    -> Колдонуучулардын тизмеси (пагинация)
#   GET    /users/<int:user_id>      -> Жеке колдонуучу
#   GET    /users/<int:user_id>/properties  -> Колдонуучунун жарнамалары
#   PATCH  /users/<int:user_id>      -> Профилди жаңылоо (өзү / admin)
#   DELETE /users/<int:user_id>      -> Колдонуучуну өчүрүү (admin)
# ---------------------------------------------------------------------------