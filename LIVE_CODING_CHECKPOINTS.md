# Live-Coding Checkpoints: Emergency and Recovery Guide

Every checkpoint is a git tag.
Every tag is a working state where `python seed.py && pytest -q` passes.
The models (and so the database schema) stop changing at `04-document-chunks`.

## The two recovery moves

Memorize these two.
They solve nearly every live-demo failure in under a minute.

**Move 1: restore one broken file** (keeps your other edits):

```bash
git checkout <tag> -- app/models.py      # or app/schemas.py, app/routes.py
python seed.py                           # only needed if models.py changed
```

**Move 2: jump the whole project to a checkpoint** (discards all uncommitted edits):

```bash
git reset --hard <tag>
python seed.py
```

Run both from the repository root with the virtual environment active.
If the server is running, it reloads by itself after either move.
If `flask shell` is open, `exit()` and reopen it.

Use Move 2 only on your `live-session` branch.
If you are on `main` by accident, run `git checkout -b live-session` first.

## Quick reference

| Tag                             | `python seed.py` prints                                          | `pytest -q` |
| ------------------------------- | ---------------------------------------------------------------- | ----------- |
| `00-starter`                    | `Seeded 2 users.`                                                | 1 passed    |
| `01-one-to-many`                | `Seeded 2 users, 3 documents.`                                   | 5 passed    |
| `02-one-to-one`                 | `Seeded 2 users, 2 profiles, 3 documents.`                       | 7 passed    |
| `03-many-to-many`               | `Seeded 2 users, 2 profiles, 3 documents, 3 tags.`               | 9 passed    |
| `04-document-chunks`            | `Seeded 2 users, 2 profiles, 3 documents, 5 chunks, 3 tags.`     | 12 passed   |
| `05-serialization`              | same as 04                                                       | 20 passed   |
| `06-deserialization-validation` | same as 04                                                       | 31 passed   |
| `07-api-responses`              | same as 04                                                       | 34 passed   |
| `08-final`                      | same as 04                                                       | 44 passed   |

To see exactly what any checkpoint adds:

```bash
git diff <previous-tag> <tag>
```

To compare your live code with a checkpoint (comment differences are fine):

```bash
git diff <tag>
```

---

## 00-starter

**Script step:** before class.

**What should currently exist:**
- A Flask app factory (`create_app`) and the shared `db` object.
- SQLite foreign-key enforcement switched on.
- A `User` model with `id` and a unique, required `email`.
- `GET /health` and the `success_response` / `error_response` helpers.
- A placeholder `app/schemas.py`.
- A seed script that creates two users, and one passing test.

**Files:** `app/__init__.py`, `app/models.py`, `app/routes.py`, `app/schemas.py`, `run.py`, `seed.py`, `tests/conftest.py`, `tests/test_health.py`, `requirements.txt`, `pytest.ini`, all documentation.

**Important code:**

```python
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
```

**Verify:**

```bash
python seed.py && pytest -q
```

**Expected output:**

```
Seeded 2 users.
1 passed
```

**Likely live-demo failure:** the virtual environment isn't active, so `python seed.py` fails with `ModuleNotFoundError: No module named 'flask'`.

**Fastest recovery:** `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`), then rerun.
If packages are missing: `pip install -r requirements.txt`.

**Next:** INSTRUCTOR_SCRIPT step 3.
Add `User.documents` and the `Document` class to `app/models.py`.

---

## 01-one-to-many

**Script step:** 3 (minute 18).

**What should currently exist:** everything from 00, plus a `Document` model that belongs to a `User`.

**Files changed:** `app/models.py`, `seed.py`, `tests/test_models.py` (new).

**Important code:**

```python
# on User
documents = db.relationship("Document", back_populates="owner")

# on Document
owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
owner = db.relationship("User", back_populates="documents")
```

**Verify:**

```bash
git checkout 01-one-to-many -- seed.py tests/
python seed.py && pytest -q
```

**Expected output:**

```
Seeded 2 users, 3 documents.
5 passed
```

**Likely live-demo failure:** `db.ForeignKey("user.id")` instead of `"users.id"`.
Error: `NoReferencedTableError: ... could not find table 'user'`.

**Fastest recovery:** fix the string, or `git reset --hard 01-one-to-many && python seed.py`.

**Next:** INSTRUCTOR_SCRIPT step 4.
Add `User.profile` and the `Profile` class.

---

## 02-one-to-one

**Script step:** 4 (minute 25).

**What should currently exist:** everything from 01, plus a `Profile` model with exactly one per user.

**Files changed:** `app/models.py`, `seed.py`, `tests/test_models.py`.

**Important code:**

```python
# on User
profile = db.relationship("Profile", back_populates="user", uselist=False)

# on Profile
user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
user = db.relationship("User", back_populates="profile")
```

**Verify:**

```bash
git checkout 02-one-to-one -- seed.py tests/
python seed.py && pytest -q
```

**Expected output:**

```
Seeded 2 users, 2 profiles, 3 documents.
7 passed
```

**Likely live-demo failure:** the shell shows `PendingRollbackError` after the duplicate-profile demo.

**Fastest recovery:** type `db.session.rollback()` in the shell.
If the model is broken: `git reset --hard 02-one-to-one && python seed.py`.

**Next:** INSTRUCTOR_SCRIPT step 5.
Add `document_tags`, `Document.tags`, and the `Tag` class.

---

## 03-many-to-many

**Script step:** 5 (minute 32).

**What should currently exist:** everything from 02, plus `Tag` and the `document_tags` association table.

**Files changed:** `app/models.py`, `seed.py`, `tests/test_models.py`.

**Important code:**

```python
document_tags = db.Table(
    "document_tags",
    db.Column("document_id", db.Integer, db.ForeignKey("documents.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)

# on Document
tags = db.relationship("Tag", secondary=document_tags, back_populates="documents", order_by="Tag.name")

# on Tag
name = db.Column(db.String(50), nullable=False, unique=True)
documents = db.relationship("Document", secondary=document_tags, back_populates="tags")
```

**Verify:**

```bash
git checkout 03-many-to-many -- seed.py tests/
python seed.py && pytest -q
```

**Expected output:**

```
Seeded 2 users, 2 profiles, 3 documents, 3 tags.
9 passed
```

**Likely live-demo failure:** `NameError: name 'document_tags' is not defined`, because the table was typed below `Document`.

**Fastest recovery:** move the `document_tags = db.Table(...)` block to just below `from app import db`.
Or `git reset --hard 03-many-to-many && python seed.py`.

**Next:** INSTRUCTOR_SCRIPT step 7 (scenario), then step 8.
Add `Document.chunks` and the `Chunk` class.

---

## 04-document-chunks

**Script step:** 8 (minute 43).

**What should currently exist:** the complete model layer.
The database schema does not change after this checkpoint.

**Files changed:** `app/models.py`, `seed.py`, `tests/test_models.py`, `tests/conftest.py` (adds the `sample_document` fixture).

**Important code:**

```python
# on Document
chunks = db.relationship("Chunk", back_populates="document", order_by="Chunk.position")

# on Chunk
__table_args__ = (
    db.CheckConstraint("position >= 0", name="ck_chunks_position_non_negative"),
    db.UniqueConstraint("document_id", "position", name="uq_chunks_document_position"),
)
document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False)
document = db.relationship("Document", back_populates="chunks")
```

**Verify:**

```bash
git checkout 04-document-chunks -- seed.py tests/
python seed.py && pytest -q
```

**Expected output:**

```
Seeded 2 users, 2 profiles, 3 documents, 5 chunks, 3 tags.
12 passed
```

**Likely live-demo failure:** forgetting to run `python seed.py` after adding `Chunk`.
Error: `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: chunks`.

**Fastest recovery:** `python seed.py`.
If the model is broken: `git reset --hard 04-document-chunks && python seed.py`.

**Next:** INSTRUCTOR_SCRIPT step 9 (constraint demo in the shell), then step 10.
Replace `app/schemas.py` with the output-only schemas.

---

## 05-serialization

**Script steps:** 10 and 11 (minutes 52 to 61).

**What should currently exist:** Marshmallow schemas that `dump()` nested tags and chunks, plus `GET /documents` and `GET /documents/<id>`.
Schemas have **no validation rules yet**.

**Files changed:** `app/schemas.py`, `app/routes.py`, `tests/test_schemas.py` (new), `tests/test_routes.py` (new).

**Important code:**

```python
class DocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    ...
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)
    chunks = fields.List(fields.Nested(ChunkSchema), dump_only=True)

document_list_schema = DocumentSchema(many=True, exclude=("chunks",))
```

```python
@api.get("/documents/<int:document_id>")
def get_document(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return error_response("not_found", {"document_id": [f"Document {document_id} does not exist."]}, 404)
    return success_response(document_schema.dump(document))
```

**Verify:**

```bash
git checkout 05-serialization -- seed.py tests/
python seed.py && pytest -q
python run.py                                  # Terminal 1
curl http://127.0.0.1:5555/documents/1         # Terminal 3
```

**Expected output:** `20 passed`, and the curl returns `{"data": {"id": 1, "title": "Flask Relationships", ... "tags": [...], "chunks": [...]}}`.

**Likely live-demo failure:** `RecursionError: maximum recursion depth exceeded` because a `documents` field was added to `TagSchema`.
Or `Address already in use` when starting the server.

**Fastest recovery:** `git checkout 05-serialization -- app/schemas.py`.
For the port, see "Port already in use" in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

**Next:** INSTRUCTOR_SCRIPT step 12.
Demo `load()` with no rules, then add validators to `app/schemas.py`.

---

## 06-deserialization-validation

**Script step:** 12 (minute 61).

**What should currently exist:** the final schemas with `required`, `Length`, `Url`, `Range`, `Email`, and the custom `not_blank` validator.
Routes are unchanged from 05.

**Files changed:** `app/schemas.py`, `tests/test_schemas.py`.

**Important code:**

```python
def not_blank(value):
    if not value.strip():
        raise ValidationError("Cannot be blank.")

title = fields.Str(required=True, validate=validate.Length(min=3, max=120))
source_url = fields.Url(allow_none=True)
owner_id = fields.Int(required=True)
position = fields.Int(required=True, validate=validate.Range(min=0))
content = fields.Str(required=True, validate=not_blank)
```

**Verify:**

```bash
git checkout 06-deserialization-validation -- tests/
pytest -q
```

**Expected output:** `31 passed`.

**Likely live-demo failure:** `NameError: name 'ValidationError' is not defined` (import line not updated), or the shell still using old schema code.

**Fastest recovery:** `git checkout 06-deserialization-validation -- app/schemas.py`, then `exit()` and reopen `flask --app run shell`.

**Next:** INSTRUCTOR_SCRIPT step 13.
Add `POST /documents` to `app/routes.py`, first without `try`/`except`.

---

## 07-api-responses

**Script steps:** 13 and 14 (minutes 68 to 78).

**What should currently exist:** `POST /documents` that returns 201 on success and a 400 `validation_error` envelope on bad input.

**Files changed:** `app/routes.py`, `tests/test_routes.py`.

**Important code:**

```python
@api.post("/documents")
def create_document():
    try:
        data = document_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("validation_error", err.messages, 400)

    owner = db.session.get(User, data["owner_id"])
    if owner is None:
        return error_response("validation_error", {"owner_id": [f"User {data['owner_id']} does not exist."]}, 400)

    document = Document(title=data["title"], source_url=data.get("source_url"), owner=owner)
    db.session.add(document)
    db.session.commit()

    return success_response(document_schema.dump(document), 201)
```

**Verify:**

```bash
git checkout 07-api-responses -- tests/
pytest -q
curl -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "", "source_url": "not-a-url"}'
```

**Expected output:** `34 passed`, and the curl returns 400 with `title`, `source_url`, and `owner_id` in `details`.

**Likely live-demo failure:** curl returns an HTML page.
Either the `Content-Type` header is missing (415), or `ValidationError` isn't caught yet (500).

**Fastest recovery:** add `-H "Content-Type: application/json"` to curl.
For the route: `git checkout 07-api-responses -- app/routes.py`.

**Next:** INSTRUCTOR_SCRIPT step 15.
Commit the live work and check out `08-final`:

```bash
git add -A && git commit -m "Live session through checkpoint 07"
git checkout 08-final
```

---

## 08-final

**Script steps:** 15 to 18 (minutes 78 to 90), plus extension activities.

**What should currently exist:** the complete solution.
`POST /documents/<id>/chunks`, `POST /tags`, `POST /documents/<id>/tags/<tag_id>`, and `POST /users`, each with `IntegrityError` handling that returns a 409 `integrity_error` envelope where a UNIQUE constraint applies.

**Files changed:** `app/routes.py`, `tests/test_routes.py`.

**Important code:**

```python
tag = Tag(name=data["name"])
db.session.add(tag)
try:
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    return error_response("integrity_error", {"name": [f"Tag '{data['name']}' already exists."]}, 409)
```

**Verify:**

```bash
python seed.py && pytest -q
curl -X POST http://127.0.0.1:5555/tags -H "Content-Type: application/json" -d '{"name": "flask"}'
```

**Expected output:** `44 passed`, and the curl returns 409 with `{"error": "integrity_error", "details": {"name": ["Tag 'flask' already exists."]}}`.

**Likely live-demo failure:** `git checkout 08-final` refuses because of uncommitted changes.

**Fastest recovery:** `git stash -u && git checkout 08-final`.
If the server stopped, `python run.py`.

**Next:** INSTRUCTOR_SCRIPT step 16 (API design discussion), then the exit check.
