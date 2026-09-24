from app.models import Profile, User
from app.schemas import document_list_schema, document_schema, user_schema


# ---------- dump() turns objects into dictionaries ----------

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


# ---------- GET endpoints ----------

def test_list_documents(client, sample_document):
    response = client.get("/documents")

    assert response.status_code == 200
    documents = response.get_json()["data"]
    assert [doc["title"] for doc in documents] == ["Flask Relationships"]
    assert "chunks" not in documents[0]


def test_get_document_returns_nested_tags_and_chunks(client, sample_document):
    response = client.get(f"/documents/{sample_document.id}")

    assert response.status_code == 200
    document = response.get_json()["data"]
    assert document["title"] == "Flask Relationships"
    assert document["tags"] == [{"id": 1, "name": "flask"}]
    assert [chunk["position"] for chunk in document["chunks"]] == [0, 1]


def test_get_missing_document_returns_404(client):
    response = client.get("/documents/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "not_found",
        "details": {"document_id": ["Document 999 does not exist."]},
    }
