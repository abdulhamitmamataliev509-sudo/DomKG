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


@pytest.fixture(autouse=True)
def _reset_db(app):
    with app.app_context():
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    yield
    with app.app_context():
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture(scope="session", autouse=True)
def _test_routes(app):
    """Error handler'лерди текшерүүгө арналган тест-маршруттар.

    Ар бир тест-модулдун биринчи сурамынан МУРУН катталат (conftest
    session-autouse → биринчи request'ке чейин ишке кирет).
    """
    from werkzeug.exceptions import (
        BadRequest,
        Conflict,
        TooManyRequests,
        UnprocessableEntity,
    )

    @app.route("/__err/400")
    def _err_400():
        raise BadRequest("bad payload")

    @app.route("/__err/409")
    def _err_409():
        raise Conflict("duplicate resource")

    @app.route("/__err/422")
    def _err_422():
        raise UnprocessableEntity("invalid fields")

    @app.route("/__err/429")
    def _err_429():
        raise TooManyRequests("slow down")

    @app.route("/__err/500")
    def _err_500():
        raise RuntimeError("boom-secret-db-detail")
    yield