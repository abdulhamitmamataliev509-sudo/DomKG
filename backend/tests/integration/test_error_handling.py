"""Phase 18 — Global Error Handling тесттери.

Текшерүүлөр:
- белгисиз маршрут        -> JSON 404
- туура эмес HTTP метод    -> JSON 405
- туура эмес сурам         -> JSON 400/422
- авторизация жок          -> JSON 401
- укугу жок (admin)        -> JSON 403
- күтүлбөгөн сервер катасы -> JSON 500 (детал агызылбайт)
- /health/db ички деталды агызбайт
"""
import pytest
from sqlalchemy.orm import Session
from werkzeug.exceptions import (
    BadRequest,
    Conflict,
    TooManyRequests,
    UnprocessableEntity,
)
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User


@pytest.fixture(scope="session", autouse=True)
def _test_routes(app):
    """Error handler'лерди текшерүүгө арналган тест-маршруттар (бир жолу)."""
    @app.route("/__err/400")
    def _err_400():
        raise BadRequest("bad payload")

    @app.route("/__err/409")
    def _err_409():
        raise Conflict("duplicate resource")

    @app.route("/__err/422")
    def _err_422():
        raise UnprocessableEntity("invalid fields")

    @app.route("/__err/429")
    def _err_429():
        raise TooManyRequests("slow down")

    @app.route("/__err/500")
    def _err_500():
        raise RuntimeError("boom-secret-db-detail")
    yield


@pytest.fixture(autouse=True)
def _fresh_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        u = User(
            email="a@t.kg", first_name="A",
            password_hash=generate_password_hash("pass1234"),
        )
        db.session.add(u)
        db.session.commit()
    yield


def _login(client):
    r = client.post("/api/auth/login", json={"email": "a@t.kg", "password": "pass1234"})
    assert r.status_code == 200
    return r.get_json()["data"]["access_token"]


def test_unknown_route_json_404(client):
    resp = client.get("/api/does-not-exist")
    assert resp.status_code == 404
    assert resp.is_json
    body = resp.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"]


def test_method_not_allowed_json_405(client):
    resp = client.post("/api/auth/ping")  # ping GET гана
    assert resp.status_code == 405
    assert resp.is_json
    body = resp.get_json()
    assert body["error"]["code"] == "METHOD_NOT_ALLOWED"
    assert "Allow" in resp.headers


def test_validation_error_json_400(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "", "password": "x", "first_name": ""},
    )
    assert resp.status_code == 400
    assert resp.is_json
    assert resp.get_json()["error"]["code"] == "BAD_REQUEST"


def test_bad_request_handler_400(client):
    resp = client.get("/__err/400")
    assert resp.status_code == 400
    assert resp.is_json
    body = resp.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "BAD_REQUEST"
    assert "bad payload" not in repr(body)  # raw message JSON'го агызылбайт


def test_unauthorized_json_401(client):
    # токен жок
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.is_json
    assert resp.get_json()["error"]["code"] == "UNAUTHORIZED"

    # туура эмес токен
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.token"})
    assert resp.status_code == 401
    assert resp.is_json
    assert resp.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_forbidden_json_403(client):
    token = _login(client)
    resp = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert resp.is_json
    assert resp.get_json()["error"]["code"] == "FORBIDDEN"


def test_conflict_json_409(client):
    resp = client.get("/__err/409")
    assert resp.status_code == 409
    assert resp.is_json
    assert resp.get_json()["error"]["code"] == "CONFLICT"


def test_unprocessable_json_422(client):
    resp = client.get("/__err/422")
    assert resp.status_code == 422
    assert resp.is_json
    assert resp.get_json()["error"]["code"] == "UNPROCESSABLE_ENTITY"


def test_too_many_requests_json_429(client):
    resp = client.get("/__err/429")
    assert resp.status_code == 429
    assert resp.is_json
    assert resp.get_json()["error"]["code"] == "TOO_MANY_REQUESTS"


def test_internal_server_error_json_500_no_leak(client):
    resp = client.get("/__err/500")
    assert resp.status_code == 500
    assert resp.is_json
    body = resp.get_json()
    assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
    # ички детал агызылбайт
    assert "boom" not in repr(body)
    assert "secret" not in repr(body)


def test_health_db_does_not_leak_internals(monkeypatch, client):
    def _boom(*args, **kwargs):
        raise RuntimeError("secret-dsn=postgresql://user:hunter2@db:5432/x")

    monkeypatch.setattr(Session, "execute", _boom)
    resp = client.get("/health/db")
    assert resp.status_code == 500
    body = resp.get_json()
    assert body.get("database") == "disconnected"
    assert "secret-dsn" not in repr(body)
    assert "hunter2" not in repr(body)