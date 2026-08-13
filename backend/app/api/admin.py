"""Администратор Blueprint'и — /api/admin.

Текшерилүүчү (admin role/Admin табл.) колдонуучулар үчүн башкаруу
эндпоинттери. Бардык маршруттарга ket-arth admin-текшерүү (middleware)
тийиштүү болот.
"""
from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/ping")
def admin_ping():
    """Blueprint'тин туура катталганын текшерүүчү эндпоинт."""
    return jsonify({"service": "admin", "status": "ok"})


# ---------------------------------------------------------------------------
# Пландалган эндпоинттер:
#
#   GET  /admin/stats            -> Статистика (жарнама, колдонуучу, көрүүлөр)
#   GET  /admin/users            -> Колдонуучуларды башкаруу в тизме
#   PATCH /admin/users/<int:user_id>  -> Колдонуучу статусун өзгөртүү (ban/verify)
#   GET  /admin/reports          -> Арыздардын тизмеси
#   PATCH /admin/reports/<int:report_id> -> Арызды чечүү (resolve/dismiss)
#   GET  /admin/properties       -> Бардык жарнамалар (moderation)
# ---------------------------------------------------------------------------