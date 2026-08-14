import os
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from sqlalchemy import text
from config import config_by_name
from app.extensions import db, jwt, migrate


# ---------------------------------------------------------------------------
# Swagger / Flasgger конфигурациясы
# ---------------------------------------------------------------------------
SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "DomKG Real Estate API",
        "description": (
            "DomKG кыймылсыз мүлк платформасынын REST API документациясы"
        ),
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Access токен. Формат: Bearer <your_access_token>"
        },
        "RefreshToken": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Refresh токен. Формат: Bearer <your_refresh_token>"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ],
    "basePath": "/",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"]
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: str(rule.rule).startswith("/api/"),
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}


def register_swagger(app):
    """Swagger UI (Flasgger) өндүрүп, /apidocs/ дареги боюнча ачат."""
    return Swagger(
        app,
        template=SWAGGER_TEMPLATE,
        config=SWAGGER_CONFIG,
    )


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config.from_object(config_by_name.get(config_name, config_by_name['dev']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ---- JWT callback'тери: ырааттуу JSON каталар + колдонуучу жүктөө ----
    from app.models import User as _User

    @jwt.user_identity_loader
    def _user_identity_loader(identity):
        return str(identity)

    @jwt.user_lookup_loader
    def _user_lookup_loader(_jwt_header, jwt_data):
        ident = jwt_data.get("sub")
        if not ident:
            return None
        try:
            return db.session.get(_User, int(ident))
        except (TypeError, ValueError):
            return None

    @jwt.unauthorized_loader
    def _unauthorized_loader(_reason):
        return jsonify({"status": "error", "message": "Аутентификация талап кылынат"}), 401

    @jwt.invalid_token_loader
    def _invalid_token_loader(_reason):
        return jsonify({"status": "error", "message": "Жараксыз токен"}), 401

    @jwt.expired_token_loader
    def _expired_token_loader(_header, _payload):
        return jsonify({"status": "error", "message": "Токендин мөөнөтү өткөн"}), 401

    # Бардык моделдерди каттоо (db.create_all / alembic көрүшү үчүн)
    with app.app_context():
        from app import models  # noqa: F401

        # Модель-индекстер даярдалсын
        db.configure_mappers()

    # API blueprint'терин каттоо (/api/*)
    from app.api import register_blueprints
    register_blueprints(app)

    # Swagger UI (/apidocs/) — blueprint'тер катталган соң ишке киришет
    register_swagger(app)

    # Health & DB Test Endpoint
    @app.route("/")
    def index():
        return jsonify({"message": "DomKG API is running", "status": "ok"})

    @app.route("/health/db")
    def db_health():
        try:
            # PostgreSQL туташуусун текшерүү
            db.session.execute(text("SELECT 1"))
            return jsonify({
                "status": "success",
                "database": "connected",
                "message": "PostgreSQL connection is healthy!"
            }), 200
        except Exception as e:
            return jsonify({
                "status": "error",
                "database": "disconnected",
                "error": str(e)
            }), 500

    return app
