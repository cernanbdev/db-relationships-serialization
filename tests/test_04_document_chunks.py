import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Chunk


def test_document_chunks_are_ordered_by_position(sample_document):
    assert [chunk.position for chunk in sample_document.chunks] == [0, 1]
    assert sample_document.chunks[0].document is sample_document


def test_database_rejects_negative_chunk_position(sample_document):
    # CheckConstraint("position >= 0") protects the table even without Marshmallow.
    db.session.add(Chunk(position=-1, content="Bad position", document=sample_document))

    with pytest.raises(IntegrityError):
        db.session.commit()


def test_database_rejects_two_chunks_at_the_same_position(sample_document):
    db.session.add(Chunk(position=0, content="Duplicate position", document=sample_document))

    with pytest.raises(IntegrityError):
        db.session.commit()
