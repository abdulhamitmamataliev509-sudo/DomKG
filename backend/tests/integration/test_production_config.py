"""Phase 20 — Production Configuration & Secrets тесттери (A..G).

Капталган багыттар:
A. production SECRET_KEY жок — башталбайт (fail-fast)
B. production JWT_SECRET_KEY жок — башталбайт
C. production DEBUG=False / TESTING=False
D. CORS — уруксат берилген origin'дер гана
E. SWAGGER_ENABLED=false болсо /apidocs/ өчүк
F. /health/db ички маалыматты агызбайт
G. production конфигурациясы env менен туура жүктөлөт
"""
import pytest
from sqlalchemy.orm import Session

from config import (
    DEV_JWT_SECRET_KEY,
    DEV_SECRET_KEY,
    DevelopmentConfig,
    ProductionConfig,
    validate_environment,
)


# A — production SECRET_KEY жок болсо башталбайт
def test_prod_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("JWT_SECRET_KEY", "test-prod-jwt-secret")
    with pytest.raises(RuntimeError) as ei:
        validate_environment("prod")
    assert "SECRET_KEY" in str(ei.value)


# B — production JWT_SECRET_KEY жок болсо башталбайт
def test_prod_requires_jwt_secret_key(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.setenv("SECRET_KEY", "test-prod-secret")
    with pytest.raises(RuntimeError) as ei:
        validate_environment("prod")
    assert "JWT_SECRET_KEY" in str(ei.value)


# A2 — белгилүү dev-default'тер да production'до кабыл алынбайт
def test_prod_rejects_known_default_secrets(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", DEV_SECRET_KEY)
    monkeypatch.setenv("JWT_SECRET_KEY", DEV_JWT_SECRET_KEY)
    with pytest.raises(RuntimeError):
        validate_environment("prod")


# C — production DEBUG/TESTING өчүк; dev'де ал ачык
def test_production_debug_off():
    assert ProductionConfig.DEBUG is False
    assert ProductionConfig.TESTING is False
    assert ProductionConfig.FLASK_ENV == "production"


def test_development_debug_on():
    assert DevelopmentConfig.DEBUG is True
    assert DevelopmentConfig.FLASK_ENV == "development"


# D — CORS уруксат берилген origin'дерге гана жооп берет
def test_cors_allowed_origin(client, app):
    allowed = app.config.get("CORS_ORIGINS") or []
    assert allowed  # wildcard "*" эмес тизме
    origin = allowed[0]
    r = client.get("/api/users", headers={"Origin": origin})
    assert r.headers.get("Access-Control-Allow-Origin") == origin


def test_cors_disallowed_origin(client):
    r = client.get("/api/users", headers={"Origin": "http://evil.example"})
    assert r.headers.get("Access-Control-Allow-Origin") is None


# E — SWAGGER_ENABLED=false болсо /apidocs/ өчүк
def test_swagger_disabled_when_config_false(client, app):
    assert app.config.get("SWAGGER_ENABLED") is False
    assert client.get("/apidocs/").status_code == 404


def test_dev_config_swagger_enabled_by_default():
    assert DevelopmentConfig.SWAGGER_ENABLED is True
    assert ProductionConfig.SWAGGER_ENABLED is False


# F — /health/db ички маалыматты агызбайт
def test_health_db_does_not_leak_credentials(client):
    def _boom(*args, **kwargs):
        raise RuntimeError("secret-dsn=postgresql://user:hunter2@db:5432/x")

    original = Session.execute
    Session.execute = _boom
    try:
        resp = client.get("/health/db")
    finally:
        Session.execute = original
    assert resp.status_code == 503
    raw = resp.get_data(as_text=True)
    assert "secret-dsn" not in raw
    assert "hunter2" not in raw
    assert "disconnected" in raw


def test_health_liveness_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.is_json
    assert r.get_json()["status"] == "ok"


# G — production конфигурациясы env өзгөрмөлөрү менен туура жүктөлөт
def test_prod_config_loads_with_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-prod-secret-42")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-prod-jwt-secret-42")
    cfg = validate_environment("prod")
    assert cfg is ProductionConfig
    assert cfg.DEBUG is False
    assert cfg.TESTING is False