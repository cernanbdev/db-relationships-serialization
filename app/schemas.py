from marshmallow import Schema, fields


class TagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    # No "documents" field here. Tag -> documents -> tags -> documents ...
    # would recurse forever, and API consumers don't need it inside a document.


class ChunkSchema(Schema):
    id = fields.Int(dump_only=True)
    position = fields.Int()
    content = fields.Str()


class DocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    source_url = fields.Str()
    owner_id = fields.Int()

    # Nested relationships are output only. Chunks and tags are added through
    # their own endpoints, so POST /documents does not accept them.
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)
    chunks = fields.List(fields.Nested(ChunkSchema), dump_only=True)


class ProfileSchema(Schema):
    id = fields.Int(dump_only=True)
    display_name = fields.Str(dump_only=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str()
    profile = fields.Nested(ProfileSchema, dump_only=True, allow_none=True)
    # No "documents" field: a user's documents are a separate concern.


# Schema instances used by the routes.
document_schema = DocumentSchema()
# The list view leaves out chunks: a document can have hundreds of them.
document_list_schema = DocumentSchema(many=True, exclude=("chunks",))
chunk_schema = ChunkSchema()
tag_schema = TagSchema()
user_schema = UserSchema()
