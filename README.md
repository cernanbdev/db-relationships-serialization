# AI Knowledge Base API

A small Flask API used to teach Flask-SQLAlchemy relationships, Marshmallow serialization and deserialization, and the difference between schema validation and database constraints.

Users own documents.
Documents are split into chunks that another system could retrieve later.
Tags categorize documents.

There is no LLM, embeddings API, vector database, authentication, or frontend.
Those would distract from the lesson.

## Data model

```
User ──1:1── Profile          (profiles.user_id is a UNIQUE foreign key)
User ──1:M── Document         (documents.owner_id is a foreign key)
Document ──1:M── Chunk        (chunks.document_id is a foreign key)
Document ──M:M── Tag          (through the document_tags association table)
```

| Table           | Columns                                            | Constraints worth noticing                                                  |
| --------------- | -------------------------------------------------- | --------------------------------------------------------------------------- |
| `users`         | `id`, `email`                                      | `email` is NOT NULL and UNIQUE                                              |
| `profiles`      | `id`, `display_name`, `user_id`                    | `user_id` is a NOT NULL, UNIQUE foreign key (this makes it one-to-one)      |
| `documents`     | `id`, `title`, `source_url`, `owner_id`            | `title` and `owner_id` are NOT NULL; `source_url` may be NULL               |
| `chunks`        | `id`, `document_id`, `position`, `content`         | CHECK `position >= 0`; UNIQUE (`document_id`, `position`)                   |
| `tags`          | `id`, `name`                                       | `name` is NOT NULL and UNIQUE                                               |
| `document_tags` | `document_id`, `tag_id`                            | composite primary key, so a tag can be attached to a document only once    |

## Requirements

- Python 3.10 or newer
- Git (to move between the live-coding checkpoints)

Nothing else.
The database is a SQLite file that is created for you.

## Setup from a clean clone

macOS / Linux:

```bash
git clone <this-repo-url> ai-knowledge-base
cd ai-knowledge-base
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
python run.py
```

Windows (PowerShell):

```powershell
git clone <this-repo-url> ai-knowledge-base
cd ai-knowledge-base
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
python run.py
```

Windows (Command Prompt): activate with `.venv\Scripts\activate.bat` instead.

If PowerShell refuses to run the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

`python seed.py` should print:

```
Seeded 2 users, 2 profiles, 3 documents, 5 chunks, 3 tags.
```

`python run.py` starts the API at <http://127.0.0.1:5555>.
The app uses port 5555 because macOS often reserves port 5000 for AirPlay.

The SQLite file lives at `instance/knowledge_base.db`.
Running `python seed.py` again deletes all tables and recreates them with fresh data.

## Run the tests

```bash
pytest -q
```

Expected on the final checkpoint:

```
44 passed
```

The tests are written to be read.
`tests/test_models.py` covers relationships and database constraints, `tests/test_schemas.py` covers `dump()` and `load()`, and `tests/test_routes.py` covers the HTTP endpoints.

## Endpoints

| Method | Path                                   | What it does                                    | Success | Errors             |
| ------ | -------------------------------------- | ----------------------------------------------- | ------- | ------------------ |
| GET    | `/health`                              | Liveness check                                  | 200     |                    |
| GET    | `/documents`                           | List documents with tags (no chunks)            | 200     |                    |
| GET    | `/documents/<id>`                      | One document with nested tags and chunks        | 200     | 404                |
| POST   | `/documents`                           | Create a document                               | 201     | 400                |
| POST   | `/documents/<id>/chunks`               | Add a chunk to a document                       | 201     | 400, 404, 409      |
| POST   | `/tags`                                | Create a tag                                    | 201     | 400, 409           |
| POST   | `/documents/<id>/tags/<tag_id>`        | Attach an existing tag to a document            | 200     | 404                |
| POST   | `/users`                               | Create a user (used to demo email validation)   | 201     | 400, 409           |

### Response envelope

Every success response looks like this:

```json
{ "data": { "...": "..." } }
```

Every error response looks like this:

```json
{ "error": "validation_error", "details": { "title": ["Length must be between 3 and 120."] } }
```

| `error` value      | Status | Meaning                                                      |
| ------------------ | ------ | ------------------------------------------------------------ |
| `validation_error` | 400    | Marshmallow (or a simple lookup) rejected the request body   |
| `not_found`        | 404    | The document or tag in the URL does not exist                |
| `integrity_error`  | 409    | The database rejected the write (a UNIQUE constraint)        |

### Try it with curl

With the server running and freshly seeded:

```bash
curl http://127.0.0.1:5555/health
curl http://127.0.0.1:5555/documents
curl http://127.0.0.1:5555/documents/1

# Valid document -> 201
curl -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "Vector Search Notes", "source_url": "https://example.com/vectors", "owner_id": 1}'

# Invalid document -> 400 validation_error
curl -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "", "source_url": "not-a-url"}'

# Add a chunk -> 201
curl -X POST http://127.0.0.1:5555/documents/1/chunks \
  -H "Content-Type: application/json" \
  -d '{"position": 2, "content": "Association tables store many-to-many links."}'

# Duplicate tag -> 409 integrity_error (the seed already created "flask")
curl -X POST http://127.0.0.1:5555/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "flask"}'

# Attach tag 3 ("retrieval") to document 1 -> 200
curl -X POST http://127.0.0.1:5555/documents/1/tags/3
```

On Windows, use Git Bash for these commands, or type `curl.exe` in PowerShell and swap the single quotes for escaped double quotes.

## Project layout

```
app/
  __init__.py     create_app(), the db object, SQLite foreign-key switch
  models.py       User, Profile, Document, Chunk, Tag, document_tags
  schemas.py      Marshmallow schemas (serialization + validation)
  routes.py       the API endpoints and the response envelope helpers
tests/            pytest suite (in-memory database per test)
seed.py           drops, recreates, and fills the SQLite database
run.py            starts the development server on port 5555
```

## Live-coding checkpoints

The git history is a sequence of tagged checkpoints.
Each tag is a working state: `python seed.py && pytest -q` passes on every one.

| Tag                              | Adds                                                              |
| -------------------------------- | ----------------------------------------------------------------- |
| `00-starter`                     | Flask app, `db`, `User` model, `/health`, response helpers        |
| `01-one-to-many`                 | `Document`, `User.documents` / `Document.owner`                   |
| `02-one-to-one`                  | `Profile`, `uselist=False`, UNIQUE `user_id`                      |
| `03-many-to-many`                | `Tag`, `document_tags` association table                          |
| `04-document-chunks`             | `Chunk`, CHECK and UNIQUE constraints                             |
| `05-serialization`               | Marshmallow schemas for `dump()`, GET endpoints                   |
| `06-deserialization-validation`  | required fields and validators for `load()`                       |
| `07-api-responses`               | `POST /documents` with `ValidationError` handling                 |
| `08-final`                       | chunk, tag, and user endpoints, `IntegrityError` handling         |

To start a live session from the starter:

```bash
git checkout -b live-session 00-starter
python seed.py
```

To jump to any checkpoint (this discards uncommitted edits on your branch):

```bash
git reset --hard 04-document-chunks
python seed.py
```

To see exactly what a checkpoint adds:

```bash
git diff 03-many-to-many 04-document-chunks
```

## Teaching materials

- [SESSION_AGENDA.md](SESSION_AGENDA.md): the 90-minute plan at a glance
- [INSTRUCTOR_SCRIPT.md](INSTRUCTOR_SCRIPT.md): the minute-by-minute script to keep open while teaching
- [LIVE_CODING_CHECKPOINTS.md](LIVE_CODING_CHECKPOINTS.md): how to verify and recover each checkpoint in under a minute
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md): fixes for common classroom-demo failures

## Two layers of protection

Marshmallow validation gives API consumers useful feedback before invalid input reaches persistence logic.
Database constraints protect persistent data integrity even when data enters through some path other than the normal API schema, such as a seed script, a shell session, a migration, or a second service.
These layers complement each other: the schema explains problems to the client, and the database refuses to store bad data no matter where it came from.

Some rules can only live in the database.
Marshmallow sees one request at a time, so it cannot know whether the tag name `"flask"` already exists in the `tags` table.
The UNIQUE constraint can.
