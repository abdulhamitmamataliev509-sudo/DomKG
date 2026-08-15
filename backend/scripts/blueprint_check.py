"""HTTP деңгээлинде blueprint'тердин иштешин текшерет (test client)."""
import sys

from app import create_app


def main() -> int:
    app = create_app("test")
    client = app.test_client()

    pings = [
        ("/api/", 200),
        ("/api/auth/ping", 200),
        ("/api/users/ping", 200),
        ("/api/categories/ping", 200),
        ("/api/properties/ping", 200),
        ("/api/favorites/ping", 200),
        ("/api/admin/ping", 200),
    ]
    ok = True
    print("\n=== HTTP blueprint checks ===")
    for url, expected in pings:
        resp = client.get(url)
        status_ok = resp.status_code == expected
        data = resp.get_json() or {}
        if url == "/api/":
            shape_ok = data.get("service") == "DomKG API"
        else:
            # Жооп форматы: {status: success, data: {service, status: ok}}
            shape_ok = data.get("status") == "success" and (data.get("data") or {}).get("status") == "ok"
        print(f"  {'PASS' if status_ok and shape_ok else 'FAIL'}  GET {url:30s} -> {resp.status_code}")
        ok = ok and status_ok and shape_ok

    print("\n[OK] Бардык blueprint HTTP деңгээлинде иштейт." if ok
          else "\n[FAIL] Кээ бир текшерүүлөр ийгиликсиз." )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())