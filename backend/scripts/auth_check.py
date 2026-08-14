"""JWT auth схемасын текшерүү: register -> token, login -> token, /me коргоо."""
import sys

from app import create_app
from app.extensions import db


def main() -> int:
    app = create_app("test")
    client = app.test_client()

    with app.app_context():
        db.create_all()

        # 1) Register -> 201 + token
        r = client.post(
            "/api/auth/register",
            json={
                "email": "jwt@test.kg",
                "password": "secret123",
                "first_name": "Айбек",
                "last_name": "Асанов",
                "phone": "+996700000001",
            },
        )
        data = r.get_json()
        token = (data or {}).get("data", {}).get("access_token") if r.status_code == 201 else None
        print(f"register          -> {r.status_code} | token={'yes' if token else 'NO'}")
        if r.status_code != 201 or not token:
            print("  body:", data)
            return 1

        # 2) Login wrong password -> 401
        r = client.post(
            "/api/auth/login",
            json={"email": "jwt@test.kg", "password": "wrong-pass"},
        )
        print(f"login (bad pass)  -> {r.status_code} | expected 401")
        if r.status_code != 401:
            return 1

        # 3) Login correct -> 200 + token
        r = client.post(
            "/api/auth/login",
            json={"email": "jwt@test.kg", "password": "secret123"},
        )
        data = r.get_json()
        token = (data or {}).get("data", {}).get("access_token") if r.status_code == 200 else None
        print(f"login (good pass) -> {r.status_code} | token={'yes' if token else 'NO'}")
        if r.status_code != 200 or not token:
            print("  body:", data)
            return 1

        # 4) /me without token -> 401
        r = client.get("/api/auth/me")
        print(f"/me (no token)    -> {r.status_code} | expected 401")
        if r.status_code != 401:
            return 1

        # 5) /me with token -> 200 + user email
        r = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        body = r.get_json()
        email = (body or {}).get("data", {}).get("email") if r.status_code == 200 else None
        print(f"/me (with token)  -> {r.status_code} | email={email}")
        if r.status_code != 200 or email != "jwt@test.kg":
            print("  body:", body)
            return 1

        print("\n[OK] JWT auth схемасы толук иштейт.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())