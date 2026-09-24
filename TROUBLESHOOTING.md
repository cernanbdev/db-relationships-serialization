# Troubleshooting

Concise fixes for common classroom-demo problems.
Commands assume you are in the repository root.

If a fix takes longer than 30 seconds during class, use a checkpoint reset instead (see [LIVE_CODING_CHECKPOINTS.md](LIVE_CODING_CHECKPOINTS.md)):

```bash
git reset --hard <tag>
python seed.py
```

---

## Virtual environment not active

**Symptom:** `ModuleNotFoundError: No module named 'flask'`, or `flask: command not found`, or `pytest` runs with the wrong Python.

**Check:**

```bash
which python        # macOS / Linux: should end in .venv/bin/python
where python        # Windows: the first line should be inside .venv\Scripts
```

**Fix:**

```bash
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\Activate.ps1         # Windows PowerShell
.venv\Scripts\activate.bat         # Windows Command Prompt
```

Your prompt should now start with `(.venv)`.
Every new terminal needs this again.

If `.venv` doesn't exist yet: `python3 -m venv .venv` (Windows: `py -m venv .venv`).

## Missing dependency

**Symptom:** `ModuleNotFoundError: No module named 'flask_sqlalchemy'` (or `marshmallow`, or `pytest`) even though the virtual environment is active.

**Fix:**

```bash
pip install -r requirements.txt
```

Note the import names differ from the package names: the package `Flask-SQLAlchemy` is imported as `flask_sqlalchemy`.

## Database file contains an old schema

**Symptom:** after changing `models.py`, errors like:

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: chunks
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: documents.source_url
```

**Cause:** `db.create_all()` creates missing tables but never alters existing ones.
The SQLite file still has the old shape.

**Fix:**

```bash
python seed.py
```

`seed.py` drops every table in the database file (even tables from a different checkpoint) and then calls `db.create_all()`, so it always rebuilds from the current models.
If that fails too, delete the file and reseed:

```bash
rm instance/knowledge_base.db      # Windows: del instance\knowledge_base.db
python seed.py
```

Restart `flask --app run shell` afterward; the shell keeps the old models loaded.

## Circular import

**Symptom:**

```
ImportError: cannot import name 'db' from partially initialized module 'app' (most likely due to a circular import)
```

**Cause:** `app/__init__.py` imports `models` or `routes` at the top of the file, before `db` is defined.
Those modules do `from app import db`, which isn't ready yet.

**Fix:** keep the order in `app/__init__.py` exactly as the starter has it:
1. `db = SQLAlchemy()` near the top.
2. `from app import models` and `from app.routes import api` **inside** `create_app()`.

Also make sure `models.py` never imports from `routes.py` or `schemas.py`.
The direction is: `routes` → `schemas` and `models` → `db`.

To restore the file: `git checkout 00-starter -- app/__init__.py`.

## "Working outside of application context"

**Symptom:**

```
RuntimeError: Working outside of application context.
```

**Cause:** you used `db.session` or `Model.query` in plain `python` (or a script) without an app context.
Flask-SQLAlchemy needs to know which app's database to use.

**Fix:** use the Flask shell, which sets up the context for you:

```bash
flask --app run shell
```

Or, in a script, wrap the code the way `seed.py` does:

```python
from app import create_app, db

app = create_app()
with app.app_context():
    ...
```

## Foreign-key naming mistake

**Symptom:**

```
sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'documents.owner_id' could not find table 'user' with which to generate a foreign key to target column 'id'
```

**Cause:** `db.ForeignKey()` takes the **table name** and column (`"users.id"`), not the class name (`"User.id"`) and not a singular (`"user.id"`).

**Fix:** match the `__tablename__` exactly:

| Model      | `__tablename__` | Foreign key string   |
| ---------- | --------------- | -------------------- |
| `User`     | `users`         | `"users.id"`         |
| `Document` | `documents`     | `"documents.id"`     |
| `Tag`      | `tags`          | `"tags.id"`          |

Then `python seed.py`.

Rule of thumb: `db.ForeignKey(...)` talks to the database, so it uses table names.
`db.relationship(...)` talks to Python, so it uses class names.

## back_populates names do not match

**Symptom:**

```
sqlalchemy.exc.InvalidRequestError: Mapper 'Mapper[User(users)]' has no property 'document'.
```

**Cause:** each side's `back_populates` must be the **exact attribute name** on the other class.

```python
class User(db.Model):
    documents = db.relationship("Document", back_populates="owner")      # points at Document.owner

class Document(db.Model):
    owner = db.relationship("User", back_populates="documents")          # points at User.documents
```

**Fix:** read the error: "Mapper User has no property 'document'" means some relationship says `back_populates="document"` but `User` calls it `documents`.
Correct the spelling on whichever side is wrong, then `python seed.py`.

## Serialization unexpectedly recurses

**Symptom:** `RecursionError: maximum recursion depth exceeded` when calling `dump()`, or responses that are enormous.

**Cause:** two schemas nest each other.
For example, `DocumentSchema` nests `TagSchema`, and someone added `documents = fields.List(fields.Nested(...DocumentSchema...))` to `TagSchema`.
Document → tags → documents → tags → ... never ends.

**Fix:** pick one direction for nesting and remove the other.
In this project, documents nest tags and chunks; tags and chunks do not nest documents.

If you truly need the reverse direction, nest a trimmed version that can't recurse:

```python
documents = fields.List(fields.Nested(lambda: DocumentSchema(only=("id", "title"))))
```

## Marshmallow ValidationError

**Symptom (in the shell or a script):**

```
marshmallow.exceptions.ValidationError: {'title': ['Length must be between 3 and 120.'], ...}
```

This is **expected** when input is invalid.
It means validation worked.

**Symptom (from an endpoint):** curl returns status 500 and an HTML debug page, and the server terminal shows `ValidationError`.

**Cause:** the route calls `schema.load()` without catching the error.

**Fix:** wrap `load()` and return the error envelope:

```python
try:
    data = document_schema.load(request.get_json(silent=True) or {})
except ValidationError as err:
    return error_response("validation_error", err.messages, 400)
```

Related messages and what they mean:

| Message                             | Meaning                                                                 |
| ----------------------------------- | ----------------------------------------------------------------------- |
| `Missing data for required field.`  | a `required=True` field was not sent                                    |
| `Unknown field.`                    | the client sent a key the schema doesn't accept (including `dump_only` fields like `id`) |
| `Not a valid integer.`              | wrong type, for example `"position": "first"`                           |
| `Field may not be null.`            | the client sent `null` for a field without `allow_none=True`            |

## IntegrityError after duplicate unique value

**Symptom:**

```
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: tags.name
```

Also possible: `UNIQUE constraint failed: users.email`, `UNIQUE constraint failed: profiles.user_id`, `UNIQUE constraint failed: chunks.document_id, chunks.position`, `CHECK constraint failed: ck_chunks_position_non_negative`, `FOREIGN KEY constraint failed`, or `NOT NULL constraint failed: ...`.

This is **expected** when the data breaks a database rule.
It means the constraint worked.

**After it happens in the shell**, the session is stuck until you roll back.
The next command fails with `PendingRollbackError`.

```python
>>> db.session.rollback()
```

**In a route**, catch it, roll back, and return a 409:

```python
try:
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    return error_response("integrity_error", {"name": [f"Tag '{data['name']}' already exists."]}, 409)
```

**If the seed data is now in a weird state:** `python seed.py`.

## Port already in use

**Symptom:**

```
Address already in use
Port 5555 is in use by another program.
```

**Cause:** an older `python run.py` is still running (often in another terminal tab), or something else owns the port.

**Fix (macOS / Linux):**

```bash
lsof -i :5555          # find the PID
kill <PID>             # stop it
python run.py
```

**Fix (Windows PowerShell):**

```powershell
netstat -ano | findstr :5555        # last column is the PID
taskkill /PID <PID> /F
python run.py
```

**Quick workaround:** change the port in `run.py` (for example `port=5556`) and use that port in your curl commands.

On macOS, avoid port 5000: AirPlay Receiver often uses it, which is why this project uses 5555.

## Other quick fixes

| Symptom                                                         | Fix                                                                                     |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| curl returns an HTML `415 Unsupported Media Type` page          | add `-H "Content-Type: application/json"`                                               |
| Shell shows old behavior after editing a file                   | `exit()` and reopen `flask --app run shell`                                             |
| `NameError: name 'document_tags' is not defined`                | define `document_tags` above the `Document` class                                       |
| `user.profile` is a list                                        | add `uselist=False` to `User.profile`                                                   |
| `pytest` can't import `app`                                     | run `pytest` from the repository root (where `pytest.ini` is)                           |
| PowerShell won't run `Activate.ps1`                             | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`                                   |
| Windows curl JSON quoting errors                                | use Git Bash, or `curl.exe ... -d '{\"name\": \"flask\"}'` in PowerShell                |
| `git checkout <tag>` refuses because of local changes           | `git stash -u`, then check out again                                                    |
