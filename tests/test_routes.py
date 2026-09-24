from app import db
from app.models import Document, User


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
