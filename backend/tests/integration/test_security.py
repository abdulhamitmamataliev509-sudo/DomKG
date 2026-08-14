"""Security & Authorization тесттери (Phase 15).

Капталган аймактар:
- /api/admin/* : anonymous 401, non-admin 403, admin 200.
- property creation: owner JWT'тен, башканын атынан түзүү мүмкүн эмес.
- favorites: ар бир колдонуучу өзүнүн гана тандоосун көрөт/өзгөртөт.
- inactive колдонуучу: login да, корголгон эндпоинт да иштөөгө жол бербейт.
- /api/users* : public жооптордо email/phone жок; owner/admin гана көрөт.
- legitimate owner операциялары иштей берет.
"""
import pytest
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Admin, Category, City, Favorite, Property, Report, User


@pytest.fixture(scope="session")
def app():
    # Blueprint'тер модулдук синглтон — app бир гана жолу түзүлөт
    application = create_app("test")
    application.config["TESTING"] = True
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


def _seed(app):
    admin_user = User(
        email="admin@test.kg", first_name="Admin",
        password_hash=generate_password_hash("adminpass123"),
    )
    user_a = User(
        email="a@test.kg", first_name="A",
        password_hash=generate_password_hash("apass1234"),
    )
    user_b = User(
        email="b@test.kg", first_name="B",
        password_hash=generate_password_hash("bpass1234"),
    )
    inactive = User(
        email="off@test.kg", first_name="Off", is_active=False,
        password_hash=generate_password_hash("offpass123"),
    )
    db.session.add_all([admin_user, user_a, user_b, inactive])
    db.session.flush()
    db.session.add(Admin(user_id=admin_user.id, role="super_admin", is_active=True))

    cat = Category(name="Батир", slug="apartment")
    city = City(name="Бишкек", slug="bishkek")
    db.session.add_all([cat, city])
    db.session.flush()

    prop = Property(
        title="P1", price=1000, owner_id=user_a.id,
        category_id=cat.id, city_id=city.id, status="active",
    )
    db.session.add(prop)
    db.session.flush()

    db.session.add(Favorite(user_id=user_b.id, property_id=prop.id))
    report = Report(property_id=prop.id, reporter_id=user_a.id, reason="spam")
    db.session.add(report)
    db.session.commit()

    app.extensions["seed"] = {
        "admin": admin_user.id,
        "a": user_a.id,
        "b": user_b.id,
        "inactive": inactive.id,
        "property": prop.id,
        "cat": cat.id,
        "city": city.id,
        "report": report.id,
    }


@pytest.fixture(autouse=True)
def _fresh_db(app):
    """Ар бир тесттин алдында DB'ни тазалап, колдонуучуларды кайра сеедирует."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        _seed(app)
    yield


@pytest.fixture()
def client(app):
    return app.test_client()


def _seed_data(app):
    return app.extensions["seed"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _login(client, email, password):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"login failed: {r.get_json()}"
    return r.get_json()["data"]["access_token"]


# --------------------------------------------------------------------------
# 1. Admin endpoints — authorization
# --------------------------------------------------------------------------
def test_admin_anonymous_401(client):
    assert client.get("/api/admin/stats").status_code == 401
    assert client.get("/api/admin/reports").status_code == 401


def test_admin_normal_user_403(client):
    token = _login(client, "a@test.kg", "apass1234")
    assert client.get("/api/admin/stats", headers=_auth(token)).status_code == 403
    assert client.get("/api/admin/reports", headers=_auth(token)).status_code == 403


def test_admin_admin_200(client):
    token = _login(client, "admin@test.kg", "adminpass123")
    assert client.get("/api/admin/stats", headers=_auth(token)).status_code == 200
    assert client.get("/api/admin/reports", headers=_auth(token)).status_code == 200


# --------------------------------------------------------------------------
# 2. Property creation — IDOR (owner from JWT, not body)
# --------------------------------------------------------------------------
def test_create_property_owner_from_token(client, app):
    seed = _seed_data(app)
    token_a = _login(client, "a@test.kg", "apass1234")

    # body'де башка колдонуучунун owner_id берилсе да, ээси JWT'тен алынат
    r = client.post(
        "/api/properties",
        headers=_auth(token_a),
        json={
            "title": "P-from-token",
            "price": 2000,
            "owner_id": seed["b"],  # зыяндуу чакуу
            "category_id": seed["cat"],
            "city_id": seed["city"],
        },
    )
    assert r.status_code == 201
    with app.app_context():
        prop = Property.query.filter_by(title="P-from-token").first()
        assert prop is not None
        assert prop.owner_id == seed["a"], "owner JWT'ден алынуусу керек"


def test_create_property_anonymous_401(client, app):
    seed = _seed_data(app)
    r = client.post(
        "/api/properties",
        json={"title": "X", "price": 1, "category_id": seed["cat"], "city_id": seed["city"]},
    )
    assert r.status_code == 401


# --------------------------------------------------------------------------
# 3. Favorites — isolation between users
# --------------------------------------------------------------------------
def test_favorites_isolated_between_users(client, app):
    seed = _seed_data(app)
    property_id = seed["property"]
    token_a = _login(client, "a@test.kg", "apass1234")
    token_b = _login(client, "b@test.kg", "bpass1234")

    # A өзүнүн тизмесин көрөт (B'дин favorite'и — A'га көрүнбөйт)
    r_a = client.get("/api/favorites", headers=_auth(token_a))
    assert r_a.status_code == 200
    assert r_a.get_json()["data"] == []

    # A B'дин favorite'ин алып сала албайт (404 — өзүнүкү эмес)
    assert client.delete(f"/api/favorites/{property_id}", headers=_auth(token_a)).status_code == 404
    # B өзүнүкүн алып сала алат
    assert client.delete(f"/api/favorites/{property_id}", headers=_auth(token_b)).status_code == 200

    # Anonymous — 401
    assert client.get("/api/favorites").status_code == 401
    assert client.post("/api/favorites", json={"property_id": 1}).status_code == 401


# --------------------------------------------------------------------------
# 4. Inactive users
# --------------------------------------------------------------------------
def test_inactive_user_login_rejected(client):
    assert (
        client.post(
            "/api/auth/login", json={"email": "off@test.kg", "password": "offpass123"}
        ).status_code
        == 401
    )


def test_inactive_token_rejected_on_protected(client, app):
    seed = _seed_data(app)
    with app.app_context():
        token = create_access_token(identity=str(seed["inactive"]))
    assert client.get("/api/auth/me", headers=_auth(token)).status_code == 401
    assert client.get("/api/admin/stats", headers=_auth(token)).status_code == 401


# --------------------------------------------------------------------------
# 5. User privacy (PII)
# --------------------------------------------------------------------------
def test_public_users_do_not_expose_pii(client, app):
    seed = _seed_data(app)
    # list — PII жок
    r = client.get("/api/users")
    assert r.status_code == 200
    for u in r.get_json()["data"]:
        assert "email" not in u and "phone" not in u

    # Башка колдонуучунун деталы — анонимге PII жок
    body = client.get(f"/api/users/{seed['b']}").get_json()
    assert "email" not in body["data"] and "phone" not in body["data"]


def test_owner_and_admin_see_private_info(client, app):
    seed = _seed_data(app)
    token_a = _login(client, "a@test.kg", "apass1234")
    token_admin = _login(client, "admin@test.kg", "adminpass123")

    # Ээси өзүнүн private маалыматын көрөт
    own = client.get(f"/api/users/{seed['a']}", headers=_auth(token_a)).get_json()
    assert own["data"].get("email") == "a@test.kg"

    # Админ башканын private маалыматын көрөт
    admin_view = client.get(f"/api/users/{seed['b']}", headers=_auth(token_admin)).get_json()
    assert admin_view["data"].get("email") == "b@test.kg"


# --------------------------------------------------------------------------
# 6. Legitimate operations still work
# --------------------------------------------------------------------------
def test_legitimate_owner_flow(client, app):
    seed = _seed_data(app)
    token_a = _login(client, "a@test.kg", "apass1234")

    # A өзүнүн жарнамасын түзө алат
    r = client.post(
        "/api/properties",
        headers=_auth(token_a),
        json={"title": "Legit", "price": 500, "category_id": seed["cat"], "city_id": seed["city"]},
    )
    assert r.status_code == 201
    created_id = r.get_json()["data"]["id"]

    # A өзүнүн favorite'ин кошо алат жана көрө алат
    add = client.post("/api/favorites", headers=_auth(token_a), json={"property_id": created_id})
    assert add.status_code == 201
    lst = client.get("/api/favorites", headers=_auth(token_a)).get_json()
    assert any(f["property_id"] == created_id for f in lst["data"])


def test_admin_resolve_report(client, app):
    seed = _seed_data(app)
    report_id = seed["report"]

    # Кадимки колдонуучу чече албайт (403)
    token_a = _login(client, "a@test.kg", "apass1234")
    assert (
        client.patch(
            f"/api/admin/reports/{report_id}",
            headers=_auth(token_a),
            json={"status": "resolved"},
        ).status_code
        == 403
    )

    # Админ чечет (200) — resolved_by сессиядан
    token_admin = _login(client, "admin@test.kg", "adminpass123")
    r = client.patch(
        f"/api/admin/reports/{report_id}",
        headers=_auth(token_admin),
        json={"status": "resolved", "resolution_note": "ok"},
    )
    assert r.status_code == 200
    with app.app_context():
        report = db.session.get(Report, report_id)
        assert report.status == "resolved"
        assert report.resolved_by == seed["admin"]


