"""HTTP жооптор үчүн консистенттүү helper'дер.

Ийгиликтүү жооп (өзгөрүлбөгөн):
    {"status": "success", "message": ..., "data": ...}

Ката жообу (жаңы бирдиктүү формат, Phase 18):
    {"success": false, "error": {"code": "BAD_REQUEST", "message": "..."}}
"""
from datetime import datetime

from flask import jsonify

from app.errors import make_error_body


def success(data=None, status=200, message=None):
    """Ийгиликтүү жооп (өзгөрүлбөйт — мурунку контракт)."""
    payload = {"status": "success"}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def error(message, status=400, code=None, errors=None):
    """Ката жообу — бирдиктүү глобалдык формат колдонулат.

    Args:
        message: Адамга түшүнүктүү билдирүү.
        status: HTTP статус коду.
        code: Опционалдуу код (мис. "BAD_REQUEST") — берилбесе DEFAULT_ERROR_CODES колдонулат.
        errors: (deprecated) details үчүн, миг. валидация каталары.
    """
    payload = make_error_body(message, status=status, code=code, details=errors)
    return jsonify(payload), status


def iso(value):
    """datetime'ти ISO-8601 сапка айландырат (timezone-aware)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
