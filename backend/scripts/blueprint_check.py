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
        data = resp.get_json()
        shape_ok = (data or {}).get("status") == "ok" if url != "/api/" else (data or {}).get("service") == "DomKG API"
        print(f"  {'PASS' if status_ok and shape_ok else 'FAIL'}  GET {url:30s} -> {resp.status_code} {data}")
        ok = ok and status_ok and shape_ok

    print("\n[OK] Бардык blueprint HTTP деңгээлинде иштейт." if ok
          else "\n[FAIL] Кээ бир текшерүүлөр ийгиликсиз." )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())