import os
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text
from config import config_by_name
from app.extensions import db, migrate

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config.from_object(config_by_name.get(config_name, config_by_name['dev']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Бардык моделдерди каттоо (db.create_all / alembic көрүшү үчүн)
    with app.app_context():
        from app import models  # noqa: F401

        # Модель-индекстер даярдалсын
        db.configure_mappers()

    # API blueprint'терин каттоо (/api/*)
    from app.api import register_blueprints
    register_blueprints(app)

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
