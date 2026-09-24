import re

import pytest

from app import create_app, db

LAST_CHECKPOINT = 8
CHECKPOINT_TEST_FILE = re.compile(r"test_(\d{2})_\w+\.py")


# Test files are named after the checkpoint that makes them pass (test_03_many_to_many.py).
# While building the app live, `pytest -q --checkpoint 3` runs only files 00 through 03.
# With no flag every file runs, which is what the finished app needs.
def pytest_addoption(parser):
    parser.addoption(
        "--checkpoint",
        type=int,
        choices=range(LAST_CHECKPOINT + 1),
        default=LAST_CHECKPOINT,
        metavar="N",
        help=f"run only the tests for checkpoints 0 through N (default {LAST_CHECKPOINT})",
    )


def pytest_ignore_collect(collection_path, config):
    match = CHECKPOINT_TEST_FILE.fullmatch(collection_path.name)
    if match and int(match.group(1)) > config.getoption("checkpoint"):
        return True
    return None


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
    """A document with one owner, two chunks, and one tag. Needs checkpoint 04."""
    # Imported here so this file still loads before these models exist.
    from app.models import Chunk, Document, Tag, User

    owner = User(email="ada@example.com")
    document = Document(title="Flask Relationships", source_url="https://example.com/flask", owner=owner)
    document.tags.append(Tag(name="flask"))
    document.chunks.append(Chunk(position=1, content="Second chunk."))
    document.chunks.append(Chunk(position=0, content="First chunk."))
    db.session.add(document)
    db.session.commit()
    return document
