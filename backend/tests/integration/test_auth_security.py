"""Phase 19 — Authentication Security тесттери (A..N).

Капталган багыттар:
- active/inactive login
- inactive колдонуучу корголгон эндпоинттерде
- refresh токен иштери
- logout / revoked refresh / revoked access
- туура эмес токен түрү (access<->refresh)
- missing/invalid/expired токендер
- login rate limiting
- password жана password_hash эч качан API'ден чыкпайт
"""
from datetime import timedelta

import pytest
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import TokenBlocklist, User


def _seed(app):
    active = User(
        email="a@t.kg", first_name="A",
        password_hash=generate_password_hash("pass1234"),
    )
    inactive = User(
        email="off@t.kg", first_name="Off", is_active=False,
        password_hash=generate_password_hash("offpass123"),
    )
    db.session.add_all([active, inactive])
    db.session.commit()
    app.extensions["seed"] = {"active": active.id, "inactive": inactive.id}


@pytest.fixture(autouse=True)
def _fresh_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        _seed(app)
    yield


def _seed_(app):
    return app.extensions["seed"]


def _login(client, email="a@t.kg", password="pass1234"):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"login failed: {r.get_json()}"
    d = r.get_json()["data"]
    return d["access_token"], d["refresh_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# A — активдүү колдонуучу login ийгиликтүү
def test_active_login_success(client):
    access, refresh = _login(client)
    assert access and refresh


# B — inactive колдонуучу login четке кагылат
def test_inactive_login_rejected(client):
    r = client.post(
        "/api/auth/login", json={"email": "off@t.kg", "password": "offpass123"}
    )
    assert r.status_code == 401
    assert r.is_json


# C — inactive колдонуучу корголгон эндпоинтте четке кагылат
def test_inactive_protected_request_rejected(client, app):
    inactive_id = _seed_(app)["inactive"]
    with app.app_context():
        token = create_access_token(identity=str(inactive_id))
    assert client.get("/api/auth/me", headers=_auth(token)).status_code == 401
    assert client.post(
        "/api/auth/logout", headers=_auth(token), json={"refresh_token": "x"}
    ).status_code == 401


# D — refresh токен иштейт
def test_refresh_success(client):
    access, refresh = _login(client)
    assert access
    r = client.post("/api/auth/refresh", headers=_auth(refresh))
    assert r.status_code == 200
    assert r.get_json()["data"]["access_token"]


# E — logout ийгиликтүү
def test_logout_success(client, app):
    access, refresh = _login(client)
    r = client.post(
        "/api/auth/logout", headers=_auth(access), json={"refresh_token": refresh}
    )
    assert r.status_code == 200
    assert r.get_json()["status"] == "success"
    with app.app_context():
        assert TokenBlocklist.query.count() == 2  # access + refresh jti


# F — revoked refresh токен кайра колдонулбайт
def test_refresh_with_revoked_token_rejected(client):
    access, refresh = _login(client)
    assert (
        client.post("/api/auth/logout", headers=_auth(access), json={"refresh_token": refresh}).status_code
        == 200
    )
    r = client.post("/api/auth/refresh", headers=_auth(refresh))
    assert r.status_code == 401
    assert r.get_json()["error"]["code"] == "UNAUTHORIZED"


# F2 — revoked access токен да четке кагылат (logout'тан кийин)
def test_revoked_access_token_rejected(client):
    access, refresh = _login(client)
    assert (
        client.post("/api/auth/logout", headers=_auth(access), json={"refresh_token": refresh}).status_code
        == 200
    )
    assert client.get("/api/auth/me", headers=_auth(access)).status_code == 401


# G — access токен refresh ордуна колдонулса четке кагылат
def test_access_token_used_as_refresh_rejected(client):
    access, _ = _login(client)
    r = client.post("/api/auth/refresh", headers=_auth(access))
    assert r.status_code == 401


# H — refresh токен access ордуна колдонулса четке кагылат
def test_refresh_token_used_as_access_rejected(client):
    _, refresh = _login(client)
    r = client.get("/api/auth/me", headers=_auth(refresh))
    assert r.status_code == 401


# I — токен жок болсо четке кагылат
def test_missing_token_rejected(client):
    assert client.get("/api/auth/me").status_code == 401


# J — туура эмес токен четке кагылат
def test_invalid_token_rejected(client):
    r = client.get("/api/auth/me", headers=_auth("not.a.valid.jwt"))
    assert r.status_code == 401
    assert r.is_json


# K — мөөнөтү өткөн токен четке кагылат
def test_expired_token_rejected(client, app):
    user_id = _seed_(app)["active"]
    with app.app_context():
        token = create_access_token(
            identity=str(user_id), expires_delta=timedelta(seconds=-5)
        )
    r = client.get("/api/auth/me", headers=_auth(token))
    assert r.status_code == 401
    assert r.get_json()["error"]["code"] == "UNAUTHORIZED"


# L — login rate limiting иштейт
def test_login_rate_limit_enforced(client, app):
    old_limit = app.config["RATE_LIMIT_LOGIN"]
    app.config["RATE_LIMIT_LOGIN"] = "3 per minute"
    try:
        statuses = []
        for _ in range(4):
            r = client.post(
                "/api/auth/login", json={"email": "a@t.kg", "password": "wrong-pass"}
            )
            statuses.append(r.status_code)
    finally:
        app.config["RATE_LIMIT_LOGIN"] = old_limit
    assert 429 in statuses, f"rate limit not enforced: {statuses}"


# M — пароль эч качан API'ден чыкпайт
def test_password_never_returned(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "new@t.kg", "password": "super-secret-pass", "first_name": "N"},
    )
    assert r.status_code == 201
    raw = r.get_data(as_text=True)
    assert '"password"' not in raw

    access, _ = _login(client, email="new@t.kg", password="super-secret-pass")
    raw_login = client.post(
        "/api/auth/login", json={"email": "new@t.kg", "password": "super-secret-pass"}
    ).get_data(as_text=True)
    assert '"password"' not in raw_login

    assert '"password"' not in client.get(
        "/api/auth/me", headers=_auth(access)
    ).get_data(as_text=True)


# N — password_hash эч качан чыкпайт
def test_password_hash_never_returned(client, app):
    access, _ = _login(client)
    uid = _seed_(app)["active"]
    lookups = [
        client.get("/api/users"),
        client.get(f"/api/users/{uid}"),
        client.get(f"/api/users/{uid}", headers=_auth(access)),
        client.get("/api/auth/me", headers=_auth(access)),
    ]
    for resp in lookups:
        raw = resp.get_data(as_text=True)
        assert "password_hash" not in raw, f"leak in {resp.request.path}"
        assert "password" not in raw, f"leak in {resp.request.path}"