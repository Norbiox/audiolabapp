import pytest
import shutil

from app import create_app
from app.models import db


@pytest.yield_fixture(scope='session')
def app():
    _app = create_app('app.config.DevelopmentConfig')
    ctx = _app.app_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.yield_fixture(scope='function')
def database(app):
    db.drop_all()
    db.create_all()
    yield db
    db.session.close()
    db.drop_all()
    for i in app.config['UPLOADS_DEFAULT_DEST'].iterdir():
        shutil.rmtree(i)


@pytest.yield_fixture(scope='session')
def client(app):
    return app.test_client()
