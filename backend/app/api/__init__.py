"""API катмары. Ар бир домен өз Blueprint'ине ээ — модулдук жана кеңейтүүгө ыңгайлуу.

Иерархия (nested blueprints):

    /api                         (api_bp)
    ├── /auth                    (auth_bp)
    ├── /users                   (users_bp)
    ├── /categories              (categories_bp)
    ├── /properties              (properties_bp)
    ├── /favorites               (favorites_bp)
    └── /admin                   (admin_bp)
"""
from flask import Blueprint, jsonify

from app.api.auth import auth_bp
from app.api.users import users_bp
from app.api.categories import categories_bp
from app.api.properties import properties_bp
from app.api.favorites import favorites_bp
from app.api.admin import admin_bp

# Ата-эне blueprint — бардык API маршруттарынын тамыры
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/")
def api_index():
    """API сервисинин кыскача маалыматы — модулдардын тизмеси."""
    modules = ["auth", "users", "categories", "properties", "favorites", "admin"]
    return jsonify({"service": "DomKG API", "status": "ok", "modules": modules})


def register_blueprints(app):
    """Бардык домендик blueprint'терди ата-энеге жана app'ка каттайт.

    Бул функцияны `create_app()` ичинде чакыруу жетиштүү —
    калган blueprint'тер ушул жерден башкарылат (SPOF жок).
    """
    api_bp.register_blueprint(auth_bp)
    api_bp.register_blueprint(users_bp)
    api_bp.register_blueprint(categories_bp)
    api_bp.register_blueprint(properties_bp)
    api_bp.register_blueprint(favorites_bp)
    api_bp.register_blueprint(admin_bp)

    app.register_blueprint(api_bp)
    return api_bp