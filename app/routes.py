from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Chunk, Document, Tag, User
from app.schemas import (
    chunk_schema,
    document_list_schema,
    document_schema,
    tag_schema,
    user_schema,
)

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


@api.post("/documents/<int:document_id>/chunks")
def create_chunk(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return error_response("not_found", {"document_id": [f"Document {document_id} does not exist."]}, 404)

    try:
        data = chunk_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("validation_error", err.messages, 400)

    chunk = Chunk(position=data["position"], content=data["content"], document=document)
    db.session.add(chunk)
    try:
        db.session.commit()
    except IntegrityError:
        # The UNIQUE(document_id, position) constraint rejected the row.
        db.session.rollback()
        return error_response(
            "integrity_error",
            {"position": [f"Document {document_id} already has a chunk at position {data['position']}."]},
            409,
        )

    return success_response(chunk_schema.dump(chunk), 201)


@api.post("/tags")
def create_tag():
    try:
        data = tag_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("validation_error", err.messages, 400)

    tag = Tag(name=data["name"])
    db.session.add(tag)
    try:
        db.session.commit()
    except IntegrityError:
        # The UNIQUE constraint on tags.name rejected the row.
        db.session.rollback()
        return error_response("integrity_error", {"name": [f"Tag '{data['name']}' already exists."]}, 409)

    return success_response(tag_schema.dump(tag), 201)


@api.post("/documents/<int:document_id>/tags/<int:tag_id>")
def add_tag_to_document(document_id, tag_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return error_response("not_found", {"document_id": [f"Document {document_id} does not exist."]}, 404)

    tag = db.session.get(Tag, tag_id)
    if tag is None:
        return error_response("not_found", {"tag_id": [f"Tag {tag_id} does not exist."]}, 404)

    # Appending to document.tags inserts a row into the document_tags table.
    if tag not in document.tags:
        document.tags.append(tag)
        db.session.commit()

    return success_response(document_schema.dump(document))


@api.post("/users")
def create_user():
    try:
        data = user_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("validation_error", err.messages, 400)

    user = User(email=data["email"])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        # The UNIQUE constraint on users.email rejected the row.
        db.session.rollback()
        return error_response("integrity_error", {"email": [f"A user with email {data['email']} already exists."]}, 409)

    return success_response(user_schema.dump(user), 201)
