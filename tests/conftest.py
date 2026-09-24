import pytest

from app import create_app, db


@pytest.fixture
def app():
    # Each test gets a brand-new in-memory database, so tests never affect each other.
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
