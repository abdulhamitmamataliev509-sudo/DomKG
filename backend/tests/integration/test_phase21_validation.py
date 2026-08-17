import pytest
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Category, City, User


@pytest.fixture
def seeded_user(app):
    with app.app_context():
        user = User(
            email="phase21@test.kg",
            first_name="Phase",
            last_name="TwentyOne",
            password_hash=generate_password_hash("pass1234"),
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def seeded_lookup(app):
    with app.app_context():
        category = Category(name="Apartment", slug="apartment", description="Apartment listing")
        city = City(name="Bishkek", slug="bishkek")
        db.session.add_all([category, city])
        db.session.commit()
        return {"category_id": category.id, "city_id": city.id}


@pytest.fixture
def auth_client(client, seeded_user):
    resp = client.post(
        "/api/auth/login",
        json={"email": "phase21@test.kg", "password": "pass1234"},
    )
    assert resp.status_code == 200
    token = resp.get_json()["data"]["access_token"]
    return token


def test_property_create_requires_valid_payload(client, auth_client, seeded_lookup):
    resp = client.post(
        "/api/properties",
        json={
            "title": "Nice apartment",
            "price": 90000,
            "deal_type": "rent",
            "property_type": "apartment",
            "category_id": seeded_lookup["category_id"],
            "city_id": seeded_lookup["city_id"],
        },
        headers={"Authorization": f"Bearer {auth_client}"},
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["title"] == "Nice apartment"
    assert data["owner_id"]


def test_property_update_allows_owner_patch(client, auth_client, seeded_lookup):
    create = client.post(
        "/api/properties",
        json={
            "title": "Original apartment",
            "price": 90000,
            "deal_type": "rent",
            "property_type": "apartment",
            "category_id": seeded_lookup["category_id"],
            "city_id": seeded_lookup["city_id"],
        },
        headers={"Authorization": f"Bearer {auth_client}"},
    )
    property_id = create.get_json()["data"]["id"]

    resp = client.patch(
        f"/api/properties/{property_id}",
        json={"title": "Updated apartment", "price": 95000},
        headers={"Authorization": f"Bearer {auth_client}"},
    )

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["data"]["title"] == "Updated apartment"
    assert body["data"]["price"] == "95000.00"


def test_property_create_rejects_missing_required_fields(client, auth_client, seeded_lookup):
    resp = client.post(
        "/api/properties",
        json={
            "price": 90000,
            "deal_type": "rent",
            "property_type": "apartment",
            "category_id": seeded_lookup["category_id"],
            "city_id": seeded_lookup["city_id"],
        },
        headers={"Authorization": f"Bearer {auth_client}"},
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_property_create_rejects_invalid_enum_and_unknown_field(client, auth_client, seeded_lookup):
    resp = client.post(
        "/api/properties",
        json={
            "title": "Bad apartment",
            "price": 90000,
            "deal_type": "boat",
            "property_type": "apartment",
            "category_id": seeded_lookup["category_id"],
            "city_id": seeded_lookup["city_id"],
            "unexpected": "field",
        },
        headers={"Authorization": f"Bearer {auth_client}"},
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_property_create_rejects_negative_price(client, auth_client, seeded_lookup):
    resp = client.post(
        "/api/properties",
        json={
            "title": "Bad price",
            "price": -10,
            "deal_type": "sale",
            "property_type": "apartment",
            "category_id": seeded_lookup["category_id"],
            "city_id": seeded_lookup["city_id"],
        },
        headers={"Authorization": f"Bearer {auth_client}"},
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_duplicate_favorite_returns_conflict(client, auth_client, seeded_lookup):
    with client.application.app_context():
        category = Category.query.get(seeded_lookup["category_id"])
        city = City.query.get(seeded_lookup["city_id"])
        from app.models import Property

        prop = Property(
            title="Favorite property",
            price=50000,
            deal_type="sale",
            property_type="apartment",
            owner_id=User.query.filter_by(email="phase21@test.kg").first().id,
            category_id=category.id,
            city_id=city.id,
            status="active",
        )
        db.session.add(prop)
        db.session.commit()
        property_id = prop.id

    first = client.post(
        "/api/favorites",
        json={"property_id": property_id},
        headers={"Authorization": f"Bearer {auth_client}"},
    )
    second = client.post(
        "/api/favorites",
        json={"property_id": property_id},
        headers={"Authorization": f"Bearer {auth_client}"},
    )
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.get_json()["error"]["code"] == "CONFLICT"


def test_duplicate_user_email_is_conflict(client):
    first = client.post(
        "/api/auth/register",
        json={"email": "dup@test.kg", "password": "pass1234", "first_name": "Dup"},
    )
    second = client.post(
        "/api/auth/register",
        json={"email": "dup@test.kg", "password": "pass1234", "first_name": "Dup"},
    )
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.get_json()["error"]["code"] == "CONFLICT"


def test_response_does_not_expose_password_hash(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "hashsafe@test.kg", "password": "pass1234", "first_name": "Safe"},
    )
    assert resp.status_code == 201
    payload = resp.get_json()
    assert "password_hash" not in repr(payload)
    assert "password" not in repr(payload)
