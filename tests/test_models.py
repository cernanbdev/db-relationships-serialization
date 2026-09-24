import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Document, Profile, Tag, User


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


# ---------- One-to-one: User -> Profile ----------

def test_user_profile_is_a_single_object_not_a_list(app):
    ada = User(email="ada@example.com")
    ada.profile = Profile(display_name="Ada L.")
    db.session.add(ada)
    db.session.commit()

    # uselist=False gives us an object instead of a list.
    assert isinstance(ada.profile, Profile)
    assert ada.profile.user is ada


def test_database_rejects_a_second_profile_for_the_same_user(app):
    ada = User(email="ada@example.com")
    db.session.add(ada)
    db.session.commit()

    # Bypass the relationship and insert two profiles directly by user_id.
    db.session.add(Profile(display_name="First", user_id=ada.id))
    db.session.add(Profile(display_name="Second", user_id=ada.id))
    with pytest.raises(IntegrityError):
        db.session.commit()


# ---------- Many-to-many: Document <-> Tag ----------

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
