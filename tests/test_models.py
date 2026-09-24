import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Document, User


# ---------- One-to-many: User -> Documents ----------

def test_user_has_many_documents(app):
    ada = User(email="ada@example.com")
    Document(title="First Doc", owner=ada)
    Document(title="Second Doc", owner=ada)
    db.session.add(ada)
    db.session.commit()

    assert [doc.title for doc in ada.documents] == ["First Doc", "Second Doc"]


def test_document_owner_id_is_the_foreign_key(app):
    ada = User(email="ada@example.com")
    document = Document(title="First Doc", owner=ada)
    db.session.add(document)
    db.session.commit()

    # Setting document.owner filled in the foreign key column for us.
    assert document.owner_id == ada.id
    assert document.owner is ada


def test_document_requires_an_existing_owner(app):
    # Foreign key constraint: owner 999 does not exist.
    db.session.add(Document(title="Orphan", owner_id=999))

    with pytest.raises(IntegrityError):
        db.session.commit()


def test_user_email_must_be_unique(app):
    db.session.add(User(email="ada@example.com"))
    db.session.commit()

    db.session.add(User(email="ada@example.com"))
    with pytest.raises(IntegrityError):
        db.session.commit()
