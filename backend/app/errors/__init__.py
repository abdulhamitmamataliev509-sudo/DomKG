"""Глобалдык error handling — бардык API каталары бирдиктүү JSON форматта.

Ката форматы:
{
    "success": false,
    "error": {
        "code": "RESOURCE_NOT_FOUND",
        "message": "Resource not found",
        "details": {...}        # optional
    }
}

Коопсуздук: production'до raw exception, stack trace, connection string,
секреттер эч качан JSON'го чыкпайт — бардыгы сервер тарапка гана жазылат.
"""
import logging

from flask import current_app, request
from werkzeug.exceptions import HTTPException

from flask import jsonify  # isort:skip


logger = logging.getLogger("domkg.errors")

DEFAULT_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "UNPROCESSABLE_ENTITY",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_SERVER_ERROR",
}


def make_error_body(message, status=400, code=None, details=None):
    """Бирдиктүү ката-форматын курат."""
    code = code or DEFAULT_ERROR_CODES.get(status, f"HTTP_{status}")
    body = {"success": False, "error": {"code": code, "message": str(message)}}
    if details is not None:
        body["error"]["details"] = details
    return body


def problem_response(status, message, code=None, details=None, headers=None):
    """JSON ката-жообун кайтарат (эч качан HTML эмес)."""
    resp = jsonify(make_error_body(message, status=status, code=code, details=details))
    resp.status_code = int(status)
    if headers:
        resp.headers.extend(headers)
    return resp


# ---------------------------------------------------------------------------
# Статус-коддор боюнча handler'лер
# ---------------------------------------------------------------------------
def handle_400(e):
    return problem_response(400, "Invalid request")


def handle_401(e):
    return problem_response(401, "Authentication required")


def handle_403(e):
    return problem_response(403, "Access forbidden")


def handle_404(e):
    return problem_response(404, "Resource not found")


def handle_405(e):
    methods = getattr(e, "valid_methods", None) or []
    allow = ", ".join(sorted(methods))
    message = "Method not allowed"
    headers = {"Allow": allow} if allow else None
    if allow:
        message += f"; allowed: {allow}"
    return problem_response(405, message, headers=headers)


def handle_409(e):
    return problem_response(409, "Conflict")


def handle_422(e):
    return problem_response(422, "Unprocessable entity")


def handle_429(e):
    return problem_response(429, "Too many requests")


def handle_500(e):
    logger.error("HTTP 500 serialized: %s", e)
    return problem_response(500, "Internal server error")


def handle_http_exception(e):
    """Башка HTTP коддор (413, 416, ...) үчүн JSON fallback."""
    code = e.code or 500
    return problem_response(code, e.description or "HTTP error")


def handle_unhandled_exception(e):
    """Күтүлбөгөн exception — production'до детал агызылбайт."""
    logger.error(
        "Unhandled exception: %s: %s on %s %s",
        type(e).__name__,
        e,
        request.method,
        request.path,
    )
    return problem_response(500, "Internal server error")


# ---------------------------------------------------------------------------
# Каттоо
# ---------------------------------------------------------------------------
def register_error_handlers(app):
    """Бардык API/HTTP каталарын бирдиктүү JSON форматка айландырат."""
    handlers = {
        400: handle_400,
        401: handle_401,
        403: handle_403,
        404: handle_404,
        405: handle_405,
        409: handle_409,
        422: handle_422,
        429: handle_429,
        500: handle_500,
    }
    for code, fn in handlers.items():
        app.register_error_handler(code, fn)
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(Exception, handle_unhandled_exception)
    return app