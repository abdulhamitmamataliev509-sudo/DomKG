"""Категориялар Blueprint'и — /api/categories."""
from flask import Blueprint, jsonify

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.get("/ping")
def categories_ping():
    """Blueprint'тин туура катталганын текшерүүчү эндпоинт."""
    return jsonify({"service": "categories", "status": "ok"})


# ---------------------------------------------------------------------------
# Пландалган эндпоинттер:
#
#   GET /categories                     -> Категориялардын дарагы/тизмеси
#   GET /categories/<int:category_id>   -> Жеке категория
#   GET /categories/<int:category_id>/subcategories -> Суб-категориялар
#   GET /categories/<int:category_id>/properties   -> Категориядагы жарнамалар
#   POST /categories                    -> Категория түзүү (admin)
#   PATCH/DELETE /categories/<id>       -> Өзгөртүү / өчүрүү (admin)
# ---------------------------------------------------------------------------