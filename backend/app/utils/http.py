"""HTTP жооптор үчүн консистенттүү helper'дер.

Бардык API жооптору бирдей форматка ээ болот:
    success -> {"status": "success", "message": ..., "data": ...}
    error   -> {"status": "error", "message": ..., "errors": ...}
"""
from datetime import datetime

from flask import jsonify


def success(data=None, status=200, message=None):
    """Ийгиликтүү жооп (200/201)."""
    payload = {"status": "success"}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def error(message, status=400, errors=None):
    """Ката жообу (400/401/404/500...)."""
    payload = {"status": "error", "message": message}
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status


def iso(value):
    """datetime'ти ISO-8601 сапка айландырат (timezone-aware)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
