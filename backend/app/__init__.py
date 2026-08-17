import os
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from sqlalchemy import text
from config import config_by_name, validate_environment
from app.errors import problem_response, register_error_handlers
from app.extensions import db, jwt, limiter, migrate


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
    if config_name not in config_by_name:
        config_name = 'development'

    # Production үчүн fail-fast коопсуздук текшерүүсү (секреттер, DEBUG)
    validate_environment(config_name)

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['dev']))

    # ---- CORS: уруксат берилген origin'дер (config'тен; "*" эмес) ----
    cors_origins = app.config.get('CORS_ORIGINS') or [
        'http://localhost:5501', 'http://127.0.0.1:5501'
    ]
    allow_credentials = bool(app.config.get('CORS_ALLOW_CREDENTIALS', False))
    if '*' in cors_origins and allow_credentials:
        raise RuntimeError(
            'CORS: credentials cannot be combined with wildcard origin.'
        )
    CORS(
        app,
        resources={r'/api/*': {'origins': cors_origins}},
        supports_credentials=allow_credentials,
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Rate limiting — config'тен RATELIMIT_ENABLED/RATELIMIT_STORAGE_URI окулат
    limiter.init_app(app)

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
        return problem_response(401, "Authentication required")

    @jwt.invalid_token_loader
    def _invalid_token_loader(_reason):
        return problem_response(401, "Invalid or malformed token")

    @jwt.expired_token_loader
    def _expired_token_loader(_header, _payload):
        return problem_response(401, "Token has expired")

    from app.models import TokenBlocklist as _TokenBlocklist

    @jwt.token_in_blocklist_loader
    def _token_in_blocklist(_jwt_header, jwt_data):
        """Revoked токендерди (access жана refresh) четке кагат."""
        jti = jwt_data.get("jti")
        if not jti:
            return False
        return _TokenBlocklist.query.filter_by(jti=jti).first() is not None

    @jwt.revoked_token_loader
    def _revoked_token_loader(_jwt_header, _jwt_data):
        app.logger.warning(
            "Revoked token used: type=%s jti=%s",
            _jwt_data.get("type"),
            _jwt_data.get("jti"),
        )
        return problem_response(401, "Token has been revoked")

    # Бардык моделдерди каттоо (db.create_all / alembic көрүшү үчүн)
    with app.app_context():
        from app import models  # noqa: F401

        # Модель-индекстер даярдалсын
        db.configure_mappers()

    # API blueprint'терин каттоо (/api/*)
    from app.api import register_blueprints
    register_blueprints(app)

    # Swagger UI — SWAGGER_ENABLED болсо гана (/apidocs/, /apispec.json)
    # Production'до default өчүк; development'де иштейт.
    if app.config.get('SWAGGER_ENABLED', False):
        register_swagger(app)

    # Глобалдык JSON error handling (400/401/403/404/405/409/422/429/500)
    register_error_handlers(app)

    # Health & DB Test Endpoint
    @app.route("/")
    def index():
        return jsonify({"message": "DomKG API is running", "status": "ok"})

    @app.route("/health")
    def health():
        """Liveness-текшерилүү — сервис иштеп жатканын көрсөтөт."""
        return jsonify({"status": "ok"}), 200

    @app.route("/health/db")
    def db_health():
        """Database reachability — ички маалыматтар (connection string, SQL,
        stack) эч качан чыкпайт; ката болсо 503 + жалпы message."""
        try:
            # PostgreSQL туташуусун текшерүү
            db.session.execute(text("SELECT 1"))
            return jsonify({
                "status": "success",
                "database": "connected",
                "message": "PostgreSQL connection is healthy!"
            }), 200
        except Exception as e:
            # Ички чоо-жай сервер логуна гана; клиентке жалпы жооп
            app.logger.error("Health check: DB connection failed: %s", e)
            return jsonify({
                "status": "error",
                "database": "disconnected",
                "error": "Database connection failed"
            }), 503

    return app
