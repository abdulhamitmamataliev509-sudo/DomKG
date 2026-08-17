"""Swagger (Flasgger) спецификациясын текшерүүчү dev-скрипт."""
import sys

from app import create_app


def main() -> int:
    # Swagger Enabled болгону үчүн dev config колдонулат (test config'те өчүк)
    app = create_app("dev")
    client = app.test_client()

    # 1) apidocs UI HTML
    resp = client.get("/apidocs/")
    print(f"GET /apidocs/  -> {resp.status_code}, content-type={resp.mimetype}")
    if resp.status_code != 200:
        print("[FAIL] /apidocs/ ачылган жок")
        return 1

    # 2) JSON спецификация
    spec_resp = client.get("/apispec.json")
    print(f"GET /apispec.json -> {spec_resp.status_code}")
    if spec_resp.status_code != 200:
        print(spec_resp.get_data(as_text=True)[:1000])
        print("[FAIL] /apispec.json түзүлө алган жок (YAML катасы болушу мүмкүн)")
        return 1
    spec = spec_resp.get_json()

    info = spec.get("info", {})
    print(f"  title      : {info.get('title')}")
    print(f"  version    : {info.get('version')}")
    if info.get("title") != "DomKG Real Estate API" or info.get("version") != "1.0.0":
        print("[FAIL] Swagger info туура эмес")
        return 1

    expected_paths = {
        "/api/auth/ping",
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/refresh",
        "/api/auth/logout",
        "/api/auth/me",
        "/api/users",
        "/api/users/{user_id}",
        "/api/users/ping",
        "/api/categories",
        "/api/categories/{category_id}",
        "/api/categories/ping",
        "/api/properties",
        "/api/properties/{property_id}",
        "/api/properties/ping",
        "/api/favorites",
        "/api/favorites/{property_id}",
        "/api/favorites/ping",
        "/api/admin/stats",
        "/api/admin/reports",
        "/api/admin/reports/{report_id}",
        "/api/admin/ping",
    }
    paths = set(spec.get("paths", {}).keys())
    print(f"\n  Документтелген path'тер: {len(paths)}")
    for p in sorted(paths):
        print(f"    - {p}")
    missing = expected_paths - paths
    if missing:
        print(f"\n[FAIL] Жетишпеген path'тер: {sorted(missing)}")
        return 1

    # Ар бир operation'до responses бар экенин текшеребиз
    ops = 0
    for path, methods in spec["paths"].items():
        for m, op in methods.items():
            if m.lower() in ("get", "post", "patch", "put", "delete"):
                ops += 1
                if "responses" not in op or not op.get("summary"):
                    print(f"[FAIL] {path} {m.upper()} — summary/responses жетишпейт")
                    return 1
    print(f"\n[OK] {len(paths)} path, {ops} операция, бардыгы summary+responses менен.")
    return 0


if __name__ == "__main__":
    sys.exit(main())