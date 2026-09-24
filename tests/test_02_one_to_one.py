import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Profile, User


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
