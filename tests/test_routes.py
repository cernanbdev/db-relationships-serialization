from app import db
from app.models import Document, Tag, User


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


# ---------- POST /documents ----------

def test_create_document(client, app):
    db.session.add(User(email="ada@example.com"))
    db.session.commit()

    response = client.post(
        "/documents",
        json={"title": "Vector Search Notes", "source_url": "https://example.com/vectors", "owner_id": 1},
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "data": {
            "id": 1,
            "title": "Vector Search Notes",
            "source_url": "https://example.com/vectors",
            "owner_id": 1,
            "tags": [],
            "chunks": [],
        }
    }
    assert db.session.get(Document, 1).title == "Vector Search Notes"


def test_create_document_with_invalid_data_returns_validation_error(client, app):
    response = client.post("/documents", json={"title": "", "source_url": "not-a-url"})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "validation_error",
        "details": {
            "title": ["Length must be between 3 and 120."],
            "source_url": ["Not a valid URL."],
            "owner_id": ["Missing data for required field."],
        },
    }
    assert Document.query.count() == 0


def test_create_document_for_missing_owner(client, app):
    response = client.post("/documents", json={"title": "Orphan", "owner_id": 999})

    assert response.status_code == 400
    assert response.get_json()["details"] == {"owner_id": ["User 999 does not exist."]}


# ---------- POST /documents/<id>/chunks ----------

def test_create_chunk(client, sample_document):
    response = client.post(f"/documents/{sample_document.id}/chunks", json={"position": 2, "content": "Third chunk."})

    assert response.status_code == 201
    assert response.get_json()["data"] == {"id": 3, "position": 2, "content": "Third chunk."}


def test_create_chunk_with_invalid_position_and_blank_content(client, sample_document):
    response = client.post(f"/documents/{sample_document.id}/chunks", json={"position": -1, "content": " "})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "validation_error",
        "details": {
            "position": ["Must be greater than or equal to 0."],
            "content": ["Cannot be blank."],
        },
    }


def test_create_chunk_at_taken_position_returns_conflict(client, sample_document):
    # Valid according to the schema, but the database's UNIQUE(document_id, position) says no.
    response = client.post(f"/documents/{sample_document.id}/chunks", json={"position": 0, "content": "Duplicate."})

    assert response.status_code == 409
    assert response.get_json()["error"] == "integrity_error"


# ---------- Tags ----------

def test_create_tag(client, app):
    response = client.post("/tags", json={"name": "embeddings"})

    assert response.status_code == 201
    assert response.get_json() == {"data": {"id": 1, "name": "embeddings"}}


def test_create_duplicate_tag_returns_conflict(client, app):
    client.post("/tags", json={"name": "embeddings"})
    response = client.post("/tags", json={"name": "embeddings"})

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "integrity_error",
        "details": {"name": ["Tag 'embeddings' already exists."]},
    }
    assert Tag.query.count() == 1


def test_add_tag_to_document(client, sample_document):
    db.session.add(Tag(name="retrieval"))
    db.session.commit()

    response = client.post(f"/documents/{sample_document.id}/tags/2")

    assert response.status_code == 200
    assert response.get_json()["data"]["tags"] == [{"id": 1, "name": "flask"}, {"id": 2, "name": "retrieval"}]


def test_adding_the_same_tag_twice_does_not_duplicate_it(client, sample_document):
    client.post(f"/documents/{sample_document.id}/tags/1")
    response = client.post(f"/documents/{sample_document.id}/tags/1")

    assert response.status_code == 200
    assert response.get_json()["data"]["tags"] == [{"id": 1, "name": "flask"}]


def test_add_missing_tag_returns_404(client, sample_document):
    response = client.post(f"/documents/{sample_document.id}/tags/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


# ---------- Users ----------

def test_create_user_with_invalid_email(client, app):
    response = client.post("/users", json={"email": "not-an-email"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "validation_error", "details": {"email": ["Not a valid email address."]}}


def test_create_duplicate_user_returns_conflict(client, app):
    first = client.post("/users", json={"email": "ada@example.com"})
    second = client.post("/users", json={"email": "ada@example.com"})

    assert first.status_code == 201
    assert first.get_json()["data"] == {"id": 1, "email": "ada@example.com", "profile": None}
    assert second.status_code == 409
    assert second.get_json()["details"] == {"email": ["A user with email ada@example.com already exists."]}
