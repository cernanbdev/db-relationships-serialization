from flask import Blueprint, request
from marshmallow import ValidationError

from app import db
from app.models import Document, User
from app.schemas import document_list_schema, document_schema

api = Blueprint("api", __name__)


# Every response uses one of two shapes:
#   success: {"data": ...}
#   error:   {"error": "some_error_code", "details": {...}}
def success_response(data, status=200):
    return {"data": data}, status


def error_response(error, details, status):
    return {"error": error, "details": details}, status


@api.get("/health")
def health():
    return success_response({"status": "ok"})


@api.get("/documents")
def list_documents():
    documents = Document.query.order_by(Document.id).all()
    return success_response(document_list_schema.dump(documents))


@api.get("/documents/<int:document_id>")
def get_document(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return error_response("not_found", {"document_id": [f"Document {document_id} does not exist."]}, 404)
    return success_response(document_schema.dump(document))


@api.post("/documents")
def create_document():
    # 1. Validate and deserialize the incoming JSON.
    try:
        data = document_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("validation_error", err.messages, 400)

    # 2. The schema checked the shape of owner_id; only the database knows if that user exists.
    owner = db.session.get(User, data["owner_id"])
    if owner is None:
        return error_response("validation_error", {"owner_id": [f"User {data['owner_id']} does not exist."]}, 400)

    # 3. Build the SQLAlchemy object and save it.
    document = Document(title=data["title"], source_url=data.get("source_url"), owner=owner)
    db.session.add(document)
    db.session.commit()

    # 4. Serialize the saved object back to JSON.
    return success_response(document_schema.dump(document), 201)
