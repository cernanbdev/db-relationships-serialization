import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Document, Tag, User


def test_documents_and_tags_work_in_both_directions(app):
    ada = User(email="ada@example.com")
    flask_tag = Tag(name="flask")
    doc_one = Document(title="Doc One", owner=ada, tags=[flask_tag])
    doc_two = Document(title="Doc Two", owner=ada, tags=[flask_tag])
    db.session.add_all([doc_one, doc_two])
    db.session.commit()

    assert doc_one.tags == [flask_tag]
    # Order is not guaranteed on this side, so compare the titles as a set.
    assert {doc.title for doc in flask_tag.documents} == {"Doc One", "Doc Two"}


def test_tag_name_must_be_unique(app):
    db.session.add(Tag(name="flask"))
    db.session.commit()

    db.session.add(Tag(name="flask"))
    with pytest.raises(IntegrityError):
        db.session.commit()
