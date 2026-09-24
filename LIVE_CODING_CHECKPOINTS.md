# Live-Coding Checkpoints: Emergency and Recovery Guide

You build the whole app on one branch (`live-session`, created from `starter`) and never switch branches.
The seed data and the tests for every checkpoint are already on that branch.
You switch them on by passing the checkpoint number you have reached:

```bash
python seed.py --checkpoint N
pytest -q --checkpoint N
```

Each new model also needs a migration before the seed and tests can use it:

```bash
flask --app run db migrate -m "Create <table> table"
flask --app run db upgrade
```

The models (and so the database schema) stop changing at `04-document-chunks`.
That is the last migration.

## The two recovery moves

Memorize these two.
They solve nearly every live-demo failure in under a minute.
Neither one moves you off your branch.

**Move 1: restore one broken file** from its checkpoint tag (keeps your other edits):

```bash
git checkout <tag> -- app/models.py      # or app/schemas.py, app/routes.py
flask --app run db migrate -m "..."      # only if models.py changed
flask --app run db upgrade               # only if models.py changed
python seed.py --checkpoint N            # only if models.py changed
```

**Move 2: start the database over** (when a migration went wrong or the data is in a state you don't trust):

```bash
rm instance/knowledge_base.db            # Windows: del instance\knowledge_base.db
flask --app run db upgrade
python seed.py --checkpoint N
```

If a bad migration file was generated, delete it from `migrations/versions/` before Move 2.
See "A migration went wrong" in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

Run both from the repository root with the virtual environment active.
If the server is running, it reloads by itself after either move.
If `flask shell` is open, `exit()` and reopen it.

The tags hold the reference lesson files in `app/`.
They predate the migrations and the per-checkpoint tests, so never `git reset --hard` to a tag; restore single files from it instead.

## Quick reference

| Checkpoint                      | Migration created                     | `python seed.py --checkpoint N` prints                           | `pytest -q --checkpoint N` |
| ------------------------------- | ------------------------------------- | ---------------------------------------------------------------- | -------------------------- |
| `00-starter`                    | `users` (already on `starter`)        | `Seeded 2 users.`                                                | 2 passed                   |
| `01-one-to-many`                | `documents`                           | `Seeded 2 users, 3 documents.`                                   | 6 passed                   |
| `02-one-to-one`                 | `profiles`                            | `Seeded 2 users, 3 documents, 2 profiles.`                       | 8 passed                   |
| `03-many-to-many`               | `tags`, `document_tags`               | `Seeded 2 users, 3 documents, 2 profiles, 3 tags.`               | 10 passed                  |
| `04-document-chunks`            | `chunks`                              | `Seeded 2 users, 3 documents, 2 profiles, 3 tags, 5 chunks.`     | 13 passed                  |
| `05-serialization`              | none                                  | same as 04                                                       | 21 passed                  |
| `06-deserialization-validation` | none                                  | same as 04                                                       | 32 passed                  |
| `07-api-responses`              | none                                  | same as 04                                                       | 35 passed                  |
| `08-final`                      | none                                  | same as 04                                                       | 45 passed                  |

To see exactly what any checkpoint adds to the lesson code:

```bash
git diff <previous-tag> <tag> -- app/models.py app/schemas.py app/routes.py
```

To compare your live code with a checkpoint (comment differences are fine):

```bash
git diff <tag> -- app/models.py          # or app/schemas.py, app/routes.py
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
- Flask-Migrate, with the `users` table migration already in `migrations/versions/`.
- `seed.py` and the tests for every checkpoint; `--checkpoint 0` runs only the starter's share.

**Files:** `app/__init__.py`, `app/models.py`, `app/routes.py`, `app/schemas.py`, `migrations/`, `run.py`, `seed.py`, `tests/`, `requirements.txt`, `pytest.ini`, all documentation.

**Important code:**

```python
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
```

**Verify:**

```bash
flask --app run db upgrade
python seed.py --checkpoint 0 && pytest -q --checkpoint 0
```

**Expected output:**

```
Seeded 2 users.
2 passed
```

**Likely live-demo failure:** the virtual environment isn't active, so `flask` or `python seed.py` fails with `ModuleNotFoundError: No module named 'flask'`.

**Fastest recovery:** `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`), then rerun.
If packages are missing: `pip install -r requirements.txt`.

**Next:** INSTRUCTOR_SCRIPT step 3.
Add `User.documents` and the `Document` class to `app/models.py`.

---

## 01-one-to-many

**Script step:** 3 (minute 18).

**What should currently exist:** everything from 00, plus a `Document` model that belongs to a `User`.

**Files changed:** `app/models.py`, plus a new migration in `migrations/versions/`.
**Tests switched on:** `tests/test_01_one_to_many.py`.

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
flask --app run db migrate -m "Create documents table"
flask --app run db upgrade
python seed.py --checkpoint 1 && pytest -q --checkpoint 1
```

**Expected output:**

```
Seeded 2 users, 3 documents.
6 passed
```

**Likely live-demo failure:** `db.ForeignKey("user.id")` instead of `"users.id"`.
Error: `NoReferencedTableError: ... could not find table 'user'`.

**Fastest recovery:** fix the string and rerun `flask --app run db migrate` (the broken model stops `migrate` before it writes a file).
Or `git checkout 01-one-to-many -- app/models.py`, then migrate, upgrade, and `python seed.py --checkpoint 1`.

**Next:** INSTRUCTOR_SCRIPT step 4.
Add `User.profile` and the `Profile` class.

---

## 02-one-to-one

**Script step:** 4 (minute 25).

**What should currently exist:** everything from 01, plus a `Profile` model with exactly one per user.

**Files changed:** `app/models.py`, plus a new migration in `migrations/versions/`.
**Tests switched on:** `tests/test_02_one_to_one.py`.

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
flask --app run db migrate -m "Create profiles table"
flask --app run db upgrade
python seed.py --checkpoint 2 && pytest -q --checkpoint 2
```

**Expected output:**

```
Seeded 2 users, 3 documents, 2 profiles.
8 passed
```

**Likely live-demo failure:** the shell shows `PendingRollbackError` after the duplicate-profile demo.

**Fastest recovery:** type `db.session.rollback()` in the shell.
If the model is broken: `git checkout 02-one-to-one -- app/models.py`, then migrate, upgrade, and `python seed.py --checkpoint 2`.

**Next:** INSTRUCTOR_SCRIPT step 5.
Add `document_tags`, `Document.tags`, and the `Tag` class.

---

## 03-many-to-many

**Script step:** 5 (minute 32).

**What should currently exist:** everything from 02, plus `Tag` and the `document_tags` association table.

**Files changed:** `app/models.py`, plus a new migration in `migrations/versions/`.
**Tests switched on:** `tests/test_03_many_to_many.py`.

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
flask --app run db migrate -m "Create tags and document_tags tables"
flask --app run db upgrade
python seed.py --checkpoint 3 && pytest -q --checkpoint 3
```

**Expected output:**

```
Seeded 2 users, 3 documents, 2 profiles, 3 tags.
10 passed
```

**Likely live-demo failure:** `NameError: name 'document_tags' is not defined`, because the table was typed below `Document`.

**Fastest recovery:** move the `document_tags = db.Table(...)` block to just below `from app import db`.
Or `git checkout 03-many-to-many -- app/models.py`, then migrate, upgrade, and `python seed.py --checkpoint 3`.

**Next:** INSTRUCTOR_SCRIPT step 7 (scenario), then step 8.
Add `Document.chunks` and the `Chunk` class.

---

## 04-document-chunks

**Script step:** 8 (minute 43).

**What should currently exist:** the complete model layer.
The database schema does not change after this checkpoint, so this is the last migration.

**Files changed:** `app/models.py`, plus a new migration in `migrations/versions/`.
**Tests switched on:** `tests/test_04_document_chunks.py` (and the `sample_document` fixture in `tests/conftest.py` now works).

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
flask --app run db migrate -m "Create chunks table"
flask --app run db upgrade
python seed.py --checkpoint 4 && pytest -q --checkpoint 4
```

**Expected output:**

```
Seeded 2 users, 3 documents, 2 profiles, 3 tags, 5 chunks.
13 passed
```

**Likely live-demo failure:** forgetting to migrate after adding `Chunk`.
Error: `no such table: chunks` from `python seed.py`, and a failing `test_migrations_build_the_same_schema_as_the_models`.

**Fastest recovery:** `flask --app run db migrate -m "Create chunks table" && flask --app run db upgrade`, then seed again.
If the model is broken: `git checkout 04-document-chunks -- app/models.py`, then migrate, upgrade, and `python seed.py --checkpoint 4`.

**Next:** INSTRUCTOR_SCRIPT step 9 (constraint demo in the shell), then step 10.
Replace `app/schemas.py` with the output-only schemas.

---

## 05-serialization

**Script steps:** 10 and 11 (minutes 52 to 61).

**What should currently exist:** Marshmallow schemas that `dump()` nested tags and chunks, plus `GET /documents` and `GET /documents/<id>`.
Schemas have **no validation rules yet**.

**Files changed:** `app/schemas.py`, `app/routes.py`.
**Tests switched on:** `tests/test_05_serialization.py`.

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
pytest -q --checkpoint 5
python run.py                                  # Terminal 1
curl http://127.0.0.1:5555/documents/1         # Terminal 3
```

**Expected output:** `21 passed`, and the curl returns `{"data": {"id": 1, "title": "Flask Relationships", ... "tags": [...], "chunks": [...]}}`.

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

**Files changed:** `app/schemas.py`.
**Tests switched on:** `tests/test_06_deserialization_validation.py`.

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
pytest -q --checkpoint 6
```

**Expected output:** `32 passed`.

**Likely live-demo failure:** `NameError: name 'ValidationError' is not defined` (import line not updated), or the shell still using old schema code.

**Fastest recovery:** `git checkout 06-deserialization-validation -- app/schemas.py`, then `exit()` and reopen `flask --app run shell`.

**Next:** INSTRUCTOR_SCRIPT step 13.
Add `POST /documents` to `app/routes.py`, first without `try`/`except`.

---

## 07-api-responses

**Script steps:** 13 and 14 (minutes 68 to 78).

**What should currently exist:** `POST /documents` that returns 201 on success and a 400 `validation_error` envelope on bad input.

**Files changed:** `app/routes.py`.
**Tests switched on:** `tests/test_07_api_responses.py`.

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
pytest -q --checkpoint 7
curl -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "", "source_url": "not-a-url"}'
```

**Expected output:** `35 passed`, and the curl returns 400 with `title`, `source_url`, and `owner_id` in `details`.

**Likely live-demo failure:** curl returns an HTML page.
Either the `Content-Type` header is missing (415), or `ValidationError` isn't caught yet (500).

**Fastest recovery:** add `-H "Content-Type: application/json"` to curl.
For the route: `git checkout 07-api-responses -- app/routes.py`.

**Next:** INSTRUCTOR_SCRIPT step 15.
Commit the live work and pull the finished routes file from `main` (you stay on your branch):

```bash
git add -A && git commit -m "Live session through checkpoint 07"
git checkout main -- app/routes.py
```

---

## 08-final

**Script steps:** 15 to 18 (minutes 78 to 90), plus extension activities.

**What should currently exist:** the complete solution.
`POST /documents/<id>/chunks`, `POST /tags`, `POST /documents/<id>/tags/<tag_id>`, and `POST /users`, each with `IntegrityError` handling that returns a 409 `integrity_error` envelope where a UNIQUE constraint applies.

**Files changed:** `app/routes.py` (pulled from `main`, not typed).
**Tests switched on:** `tests/test_08_integrity_errors.py`.

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

**Expected output:** `45 passed` (no `--checkpoint` needed now), and the curl returns 409 with `{"error": "integrity_error", "details": {"name": ["Tag 'flask' already exists."]}}`.

**Likely live-demo failure:** `git checkout main -- app/routes.py` fails with `pathspec 'main' did not match`, because this clone has no local `main`.

**Fastest recovery:** `git fetch origin && git checkout origin/main -- app/routes.py`.
If the server stopped, `python run.py`.

**Next:** INSTRUCTOR_SCRIPT step 16 (API design discussion), then the exit check.
