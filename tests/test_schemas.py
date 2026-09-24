import pytest
from marshmallow import ValidationError

from app.models import Profile, User
from app.schemas import (
    chunk_schema,
    document_list_schema,
    document_schema,
    tag_schema,
    user_schema,
)


# ---------- Serialization: dump() turns objects into dictionaries ----------

def test_dump_document_includes_basic_fields(sample_document):
    result = document_schema.dump(sample_document)

    assert result["id"] == sample_document.id
    assert result["title"] == "Flask Relationships"
    assert result["source_url"] == "https://example.com/flask"
    assert result["owner_id"] == sample_document.owner_id


def test_dump_document_nests_tags_and_chunks(sample_document):
    result = document_schema.dump(sample_document)

    assert result["tags"] == [{"id": 1, "name": "flask"}]
    assert [chunk["position"] for chunk in result["chunks"]] == [0, 1]
    assert result["chunks"][0]["content"] == "First chunk."


def test_nested_data_does_not_recurse_back_to_documents(sample_document):
    result = document_schema.dump(sample_document)

    # TagSchema and ChunkSchema deliberately leave out their document(s).
    assert "documents" not in result["tags"][0]
    assert "document" not in result["chunks"][0]
    # We also chose not to embed the whole owner object.
    assert "owner" not in result


def test_document_list_leaves_out_chunks(sample_document):
    result = document_list_schema.dump([sample_document])

    assert "chunks" not in result[0]
    assert result[0]["tags"] == [{"id": 1, "name": "flask"}]


def test_dump_user_nests_profile_but_not_documents(app):
    user = User(id=1, email="ada@example.com", profile=Profile(id=1, display_name="Ada L."))

    assert user_schema.dump(user) == {
        "id": 1,
        "email": "ada@example.com",
        "profile": {"id": 1, "display_name": "Ada L."},
    }


# ---------- Deserialization: load() validates incoming data ----------

def test_load_valid_document():
    data = document_schema.load({"title": "Flask Relationships", "source_url": "https://example.com", "owner_id": 1})

    assert data == {"title": "Flask Relationships", "source_url": "https://example.com", "owner_id": 1}


def test_source_url_is_optional():
    data = document_schema.load({"title": "No Source", "owner_id": 1})

    assert "source_url" not in data


def test_title_is_required():
    with pytest.raises(ValidationError) as error:
        document_schema.load({"owner_id": 1})

    assert error.value.messages == {"title": ["Missing data for required field."]}


def test_title_must_be_between_3_and_120_characters():
    with pytest.raises(ValidationError) as error:
        document_schema.load({"title": "AI", "owner_id": 1})

    assert error.value.messages == {"title": ["Length must be between 3 and 120."]}


def test_source_url_must_be_a_valid_url():
    with pytest.raises(ValidationError) as error:
        document_schema.load({"title": "Flask Relationships", "source_url": "not-a-url", "owner_id": 1})

    assert error.value.messages == {"source_url": ["Not a valid URL."]}


def test_dump_only_fields_cannot_be_loaded():
    with pytest.raises(ValidationError) as error:
        document_schema.load({"id": 99, "title": "Flask Relationships", "owner_id": 1})

    assert error.value.messages == {"id": ["Unknown field."]}


def test_chunk_position_cannot_be_negative():
    with pytest.raises(ValidationError) as error:
        chunk_schema.load({"position": -1, "content": "Some text."})

    assert error.value.messages == {"position": ["Must be greater than or equal to 0."]}


def test_chunk_position_must_be_an_integer():
    with pytest.raises(ValidationError) as error:
        chunk_schema.load({"position": "first", "content": "Some text."})

    assert error.value.messages == {"position": ["Not a valid integer."]}


def test_chunk_content_cannot_be_blank():
    with pytest.raises(ValidationError) as error:
        chunk_schema.load({"position": 0, "content": "   "})

    assert error.value.messages == {"content": ["Cannot be blank."]}


def test_tag_name_has_a_length_limit():
    with pytest.raises(ValidationError) as error:
        tag_schema.load({"name": "x" * 51})

    assert error.value.messages == {"name": ["Length must be between 2 and 50."]}


def test_user_email_must_be_valid():
    with pytest.raises(ValidationError) as error:
        user_schema.load({"email": "not-an-email"})

    assert error.value.messages == {"email": ["Not a valid email address."]}
