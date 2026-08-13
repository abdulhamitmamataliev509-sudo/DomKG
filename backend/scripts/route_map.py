"""Катталган бардык API маршруттарын көрсөтүүчү dev-курал.

Колдонуу:  python -m scripts.route_map
"""
import sys

from app import create_app


def main() -> int:
    app = create_app()  # default: development config
    print("\n=== Registered URL map ===")
    rules = sorted(app.url_map.iter_rules(), key=lambda r: str(r))
    for rule in rules:
        methods = ",".join(sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"}))
        print(f"  {methods:10s} {rule.rule}  ->  {rule.endpoint}")

    expected = [
        "/api/",
        "/api/auth/ping",
        "/api/users/ping",
        "/api/categories/ping",
        "/api/properties/ping",
        "/api/favorites/ping",
        "/api/admin/ping",
    ]
    actual = {str(r) for r in app.url_map.iter_rules()}
    missing = [u for u in expected if u not in actual]
    if missing:
        print(f"\n[FAIL] Жетишпеген маршруттар: {missing}")
        return 1
    print("\n[OK] Бардык күтүлгөн blueprint маршруттары катталган.")
    return 0


if __name__ == "__main__":
    sys.exit(main())