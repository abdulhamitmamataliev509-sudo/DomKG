"""Кыймылсыз мүлк жарнамалары Blueprint'и — /api/properties."""
from flask import Blueprint, jsonify

properties_bp = Blueprint("properties", __name__, url_prefix="/properties")


@properties_bp.get("/ping")
def properties_ping():
    """Blueprint'тин туура катталганын текшерүүчү эндпоинт."""
    return jsonify({"service": "properties", "status": "ok"})


# ---------------------------------------------------------------------------
# Пландалган эндпоинттер:
#
#   GET  /properties                    -> Издөө/фильтр (deal_type, city, price...)
#   POST /properties                    -> Жаңы жарнама түзүү (login керек)
#   GET  /properties/<int:prop_id>      -> Жеке жарнама (көрүү эсептелет)
#   PATCH/PUT /properties/<int:prop_id> -> Жарнаманы жаңылоо (ээси)
#   DELETE /properties/<int:prop_id>    -> Жарнаманы өчүрүү (ээси / admin)
#   POST /properties/<int:prop_id>/images       -> Сүрөт кошуу
#   DELETE /properties/<int:prop_id>/images/<int:image_id> -> Сүрөт өчүрүү
# ---------------------------------------------------------------------------