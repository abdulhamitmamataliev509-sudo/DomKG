"""pytest үчүн жалпы фикстуралар.

Blueprint'тер модулдук синглтон болгондуктан, КҮНБҮЗ бир гана app
session боюна түзүлөт. Ар бир тест-модуль өзүнүн ``_fresh_db`` autouse
фикстурасы аркылуу DB'ни тазалап, өз маалыматтарын сеед'дейт.
"""
import pytest

from app import create_app
from app.extensions import db


@pytest.fixture(scope="session")
def app():
    application = create_app("test")
    application.config["TESTING"] = True
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()