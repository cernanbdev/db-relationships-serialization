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
