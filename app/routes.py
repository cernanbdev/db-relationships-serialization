from flask import Blueprint

from app import db
from app.models import Document
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
