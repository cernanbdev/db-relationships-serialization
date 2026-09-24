import pytest

from app import create_app, db
from app.models import Chunk, Document, Tag, User


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


@pytest.fixture
def sample_document(app):
    """A document with one owner, two chunks, and one tag."""
    owner = User(email="ada@example.com")
    document = Document(title="Flask Relationships", source_url="https://example.com/flask", owner=owner)
    document.tags.append(Tag(name="flask"))
    document.chunks.append(Chunk(position=1, content="Second chunk."))
    document.chunks.append(Chunk(position=0, content="First chunk."))
    db.session.add(document)
    db.session.commit()
    return document
