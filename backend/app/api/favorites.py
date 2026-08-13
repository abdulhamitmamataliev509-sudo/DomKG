"""Тандоолор (избранное) Blueprint'и — /api/favorites.

Колдонуучунун сакталган мүлктөрүн башкаруу: тизме, кошуу, алып салуу.
"""
from flask import Blueprint, jsonify

favorites_bp = Blueprint("favorites", __name__, url_prefix="/favorites")


@favorites_bp.get("/ping")
def favorites_ping():
    """Blueprint'тин туура катталганын текшерүүчү эндпоинт."""
    return jsonify({"service": "favorites", "status": "ok"})


# ---------------------------------------------------------------------------
# Пландалган эндпоинттер:
#
#   GET    /favorites                    -> Учурдагы колдонуучунун тандоолору
#   POST   /favorites                    -> Мүлктү избранноеге кошуу {property_id}
#   DELETE /favorites/<int:property_id>  -> Мүлктү избранноеден алып салуу
# ---------------------------------------------------------------------------