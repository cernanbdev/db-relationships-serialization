# Instructor Script: AI Knowledge Base API

Keep this file open beside your editor for the whole session.
Every step is keyed to the number of minutes since class started.

- Quick agenda: [SESSION_AGENDA.md](SESSION_AGENDA.md)
- Recovery for every checkpoint: [LIVE_CODING_CHECKPOINTS.md](LIVE_CODING_CHECKPOINTS.md)
- Error fixes: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## How to use this script

Each live-coding step has the same parts:

- **TIME**: when the step starts.
- **INSTRUCTOR SAYS**: words you can say aloud.
- **ASK STUDENTS**: ask this *before* you type or run anything.
  Wait at least five seconds.
  "Listen for" is the answer you want.
- **CODE**: exactly what to type or run.
- **EXPLAIN**: talking points after the code is on screen.
- **EXPECTED RESULT**: what you should see.
- **COMMON MISTAKE**: the most likely beginner (or live-demo) error.
- **RECOVERY**: how to get back on track in under a minute.
- **TRANSITION**: a sentence that leads into the next step.

Two answer keys are at the bottom of this file so you do not reveal them by accident: the cardinality answers (Answer Key A) and the exit-question answers (Answer Key B).

### The live-coding rhythm

You only type the lesson code: models, schemas, and routes.
You do **not** type seed data or tests, and you never switch branches.
The `starter` branch already holds the seed data and the tests for every checkpoint.
You switch them on by telling them which checkpoint you have reached.

After each **model** step, create the table with a migration, then seed and test:

```bash
flask --app run db migrate -m "Create <table> table"
flask --app run db upgrade
python seed.py --checkpoint N
pytest -q --checkpoint N
```

After each **schema or route** step, only the `pytest` line is needed.

`N` is the checkpoint number: `1` for `01-one-to-many`, `2` for `02-one-to-one`, and so on.
`seed.py` then seeds only the models that exist so far, and `pytest` runs only the test files numbered `00` through `N`.
Without `--checkpoint`, both run everything, which only works once the whole app exists.

Then compare your typed code with the reference, for example `git diff 01-one-to-many -- app/models.py`.
This only reads the tag; it does not move your branch.
Differences in comments are fine.
Any other difference is a typo worth fixing before you move on.

If something breaks and you cannot fix it in about 30 seconds, restore that one file from the checkpoint and rerun the commands above:

```bash
git checkout <tag> -- app/models.py      # or app/schemas.py, app/routes.py
```

You stay on your branch, and your other files are untouched.
If a migration itself went wrong, see "A migration went wrong" in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

This file, the agenda, and the recovery guides are the same on `starter` and `main`.

### Terminal layout

- **Terminal 1 (server):** `python run.py`.
  Not needed until step 11.
- **Terminal 2 (shell, migrations, and tests):** `flask --app run shell`, `flask --app run db ...`, `python seed.py --checkpoint N`, `pytest -q --checkpoint N`.
- **Terminal 3 (requests):** `curl` commands.

All three need the virtual environment activated (`source .venv/bin/activate`).

`flask shell` does not reload code.
After you change `models.py` or `schemas.py`, type `exit()` and start `flask --app run shell` again.

## Before class (10 minutes before the session)

```bash
cd ai-knowledge-base
source .venv/bin/activate
git status                                # clean working tree
git checkout -b live-session starter      # if the branch already exists: see below
pip install -r requirements.txt           # picks up Flask-Migrate
rm -f instance/knowledge_base.db          # start from an empty database
flask --app run db upgrade                # creates the users table
python seed.py --checkpoint 0             # Seeded 2 users.
pytest -q --checkpoint 0                  # 2 passed
```

If `live-session` already exists from a rehearsal, reset it instead of creating it.
`git clean` removes migration files you generated but never committed:

```bash
git checkout live-session
git reset --hard starter
git clean -fd migrations/
```

Open these files in the editor as tabs: `app/models.py`, `app/schemas.py`, `app/routes.py`, `app/__init__.py`.

Increase the editor and terminal font size.

---

# Segment 1: Technical Q&A (minutes 0 to 15)

## Step 1: Open the floor

**TIME:** Minute 0

**INSTRUCTOR SAYS:**
"Welcome back.
Today we're going to connect three modules into one working API: relationships from Module 21, serialization from Module 22, and constraints and validations from Module 23.
By the end, you'll trace a single request from raw JSON all the way into the database and back out again.
Before we write any code, this is your time.
What's been confusing, surprising, or just annoying in the last three modules?
Nothing is too small."

**ASK STUDENTS:**
"What's one thing from relationships, serialization, or validation you'd like to see working live today?"

**CODE:** None.
Keep the starter repository on screen so students can see the project shape.

**EXPLAIN:**
- Write every student question on a visible "parking lot" (a text file or whiteboard).
- If a question will be answered by a later step, say "Great question, we'll build exactly that at minute X" and park it.
- Answer anything else now, briefly.

**EXPECTED RESULT:** A short list of student questions, some answered, some parked.

**COMMON MISTAKE:** Answering one question for ten minutes.
Cap each answer at about two minutes.

**RECOVERY:** If you are running long, say "Let's hold the rest for the parking lot; I'll come back to it during the live coding."

**TRANSITION:** Use the backup questions below if the room is quiet, then move to step 2 at minute 15.

### Backup questions (use if students are quiet)

Ask one, give students 10 to 20 seconds, take one or two answers, then give the short answer.

**1. "What is the difference between a foreign key and `db.relationship()`?"**

Short answer:
"The foreign key is a real column in the database, like `owner_id` on documents.
It's the actual link and the database enforces it.
`db.relationship()` doesn't create any column.
It's a Python convenience that lets me write `document.owner` instead of querying the users table by hand.
You can have a foreign key without a relationship.
You can't have a working relationship without a foreign key underneath it."

**2. "What makes one-to-one different from one-to-many?"**

Short answer:
"In the database, almost nothing, and that's the surprise.
Both use a foreign key.
One-to-one adds a UNIQUE constraint on that foreign key so the same user can't appear twice.
On the Python side, we add `uselist=False` so we get one object instead of a list."

**3. "Why does many-to-many need another table?"**

Short answer:
"A column holds one value.
If a document could have many tags, which column on `documents` would hold all the tag ids?
And tags have many documents too, so we can't put it on `tags` either.
So we make a third table where each row is one pairing: this document, this tag."

**4. "What is the difference between Marshmallow `dump()` and `load()`?"**

Short answer:
"`dump()` goes out: Python objects to plain dictionaries that become JSON.
`load()` comes in: raw input to validated Python data, and it raises a `ValidationError` if the input breaks our rules.
Memory trick: you *load* a truck coming into the warehouse and you *dump* it going out."

**5. "Why use a database constraint if Marshmallow already validates input?"**

Short answer:
"Marshmallow only guards the front door, the API.
Data can also arrive through a seed script, a shell session, a migration, or another service.
Also, some rules need the whole table to check.
Marshmallow can't know that the email already exists.
The database can."

**6. "What does `back_populates` actually do?"**

Short answer:
"It tells SQLAlchemy that two relationship attributes are two views of the same link.
When I set `document.owner = ada`, SQLAlchemy also puts the document into `ada.documents` right away, before anything is saved."

**7. "What does `nullable=False` protect against?"**

Short answer:
"It makes the database refuse a row with a missing value in that column.
For `owner_id`, that means no document without an owner."

**8. "When you get an `IntegrityError`, what state is the session in?"**

Short answer:
"The failed transaction is still pending in the session.
You have to call `db.session.rollback()` before you can use the session again."

---

# Segment 2: Concept Review (minutes 15 to 40)

## Step 2: The mental model

**TIME:** Minute 15

**INSTRUCTOR SAYS:**
"Here's the map for today.
Everything we build fits somewhere on this path.
Let's read it top to bottom once, then keep coming back to it."

Put this on screen or on the whiteboard, and leave it visible all session:

```
Incoming JSON
      ↓
Marshmallow validation / deserialization      schema.load()
      ↓
Python data                                    a plain dict
      ↓
SQLAlchemy objects                             Document(...), Chunk(...)
      ↓
Relationships and database constraints         FOREIGN KEY, UNIQUE, CHECK, NOT NULL
      ↓
Database                                       SQLite file
      ↓
SQLAlchemy objects                             queried back out
      ↓
Marshmallow serialization                      schema.dump()
      ↓
JSON response                                  {"data": ...} or {"error": ...}
```

**ASK STUDENTS:**
"Which of these arrows can reject bad data?"

Listen for: `load()` (Marshmallow validation) and the database constraints.
Bonus: the route itself can reject data too, for example when a referenced user doesn't exist.

**CODE:** None.

**EXPLAIN:**
- "There are two guards on this path: Marshmallow near the top and the database near the bottom.
  Today is about why we want both."
- "`load()` gives us a dictionary, not a model.
  Turning that dictionary into a `Document` is our job, in the route."
- "`dump()` doesn't have to output every column or relationship.
  We decide what the API shows."

**EXPECTED RESULT:** Students can point to where validation happens and where persistence happens.

**COMMON MISTAKE:** Students think `load()` saves to the database.
It does not; it only validates and returns Python data.

**RECOVERY:** If that misconception comes up, say "`load()` never touches the database.
We'll prove that in step 12 when we load data with no server and no commit."

**TRANSITION:**
"Let's build the bottom half of this diagram first, starting with the simplest relationship there is."

## Step 3: Easy example, one-to-many (User to Documents)

**TIME:** Minute 18
**Checkpoint reached:** `01-one-to-many`

**INSTRUCTOR SAYS:**
"Open `app/models.py`.
We already have a `User` with an `email` that's `unique=True`.
Now: a user can own many documents, and each document belongs to exactly one user.
That's one-to-many."

**ASK STUDENTS:**
"Before I type anything: which table gets the foreign key, `users` or `documents`?
Why?"

Listen for: `documents`, because each document points at one user.
If students say `users`: "If `users` held the foreign key, one user row could only point at one document.
Where would the second document's id go?"

**CODE:** In `app/models.py`, add the `documents` line to `User`, then add the `Document` class below it.

```python
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    # unique=True creates a UNIQUE constraint in the database itself.
    email = db.Column(db.String(255), nullable=False, unique=True)

    # One-to-many: user.documents is a list of Document objects.
    documents = db.relationship("Document", back_populates="owner")

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    source_url = db.Column(db.String(500), nullable=True)

    # The foreign key lives on the "many" side: many documents -> one user.
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document id={self.id} title={self.title!r}>"
```

Then create the table with a migration, seed it, and verify:

```bash
flask --app run db migrate -m "Create documents table"
flask --app run db upgrade
python seed.py --checkpoint 1
pytest -q --checkpoint 1
git diff 01-one-to-many -- app/models.py
```

**EXPLAIN (migrations, the first time only):**
- "Writing a class doesn't create a table.
  `flask db migrate` compares our models with the database and writes the difference down as a migration file.
  `flask db upgrade` runs that file against the database."
- Open the new file in `migrations/versions/` and point at `op.create_table('documents', ...)` and `sa.ForeignKeyConstraint(['owner_id'], ['users.id'])`.
  "That's our foreign key, written in the database's own terms.
  Always read a generated migration before you run it."
- "Every model change from here on is the same three moves: migrate, read, upgrade."

**EXPLAIN:**
- "Notice that `owner_id` is the database-level connection.
  The relationship property does something different: it gives us convenient Python-object navigation.
  If I delete `db.relationship()`, the foreign key does not magically disappear.
  The link is still in the table; I just lose `document.owner`."
- "`db.ForeignKey("users.id")` uses the **table name**, `users`, lowercase and plural, because it's talking to the database.
  `db.relationship("User", ...)` uses the **class name**, because it's talking to Python."
- "`back_populates` pairs the two attributes.
  `User.documents` says its partner is `owner`.
  `Document.owner` says its partner is `documents`.
  Both names must match exactly."
- "`nullable=False` on `owner_id` is a database rule: no orphan documents.
  `nullable=True` on `source_url` means the URL is optional."

**ASK STUDENTS (predict before running):**
"When I run `ada.documents`, what type of thing comes back: one document, a list, or an error?"

Listen for: a list, because it's the "many" side.

Then open the shell:

```bash
flask --app run shell
```

```python
>>> from app import db
>>> from app.models import User, Document
>>> ada = db.session.get(User, 1)
>>> ada.documents
>>> doc = db.session.get(Document, 3)
>>> doc.owner
>>> doc.owner_id
```

Now show `back_populates` keeping both sides in sync before anything is saved:

"If I create a new document and set its owner to Ada, but **don't commit**, will it show up in `ada.documents`?"

```python
>>> draft = Document(title="Draft", owner=ada)
>>> draft in ada.documents
>>> db.session.rollback()
>>> exit()
```

**EXPECTED RESULT:**

- `flask db migrate` prints `Detected added table 'documents'`.
- `python seed.py --checkpoint 1` prints `Seeded 2 users, 3 documents.`
- `pytest -q --checkpoint 1` prints `6 passed`.
- `git diff 01-one-to-many -- app/models.py` shows nothing, or only comment differences.
- Shell:

```
>>> ada.documents
[<Document id=1 title='Flask Relationships'>, <Document id=2 title='Marshmallow Basics'>]
>>> doc.owner
<User id=2 email='grace@example.com'>
>>> doc.owner_id
2
>>> draft in ada.documents
True
```

**COMMON MISTAKE:** `db.ForeignKey("user.id")` (singular) or `db.ForeignKey("User.id")` (class name).
The error is `NoReferencedTableError: Foreign key associated with column 'documents.owner_id' could not find table 'user'`.

**RECOVERY:** Fix the string to `"users.id"` and rerun `flask --app run db migrate`.
The broken model stops `migrate` before it writes a file, so there is nothing to clean up.
If you are still stuck after 30 seconds: `git checkout 01-one-to-many -- app/models.py`, then rerun the migrate, upgrade, and seed commands.

**TRANSITION:**
"One user, many documents: the foreign key goes on the many side.
Now what if I want each user to have exactly *one* of something?"

## Step 4: Intermediate example, one-to-one (User to Profile)

**TIME:** Minute 25
**Checkpoint reached:** `02-one-to-one`

**INSTRUCTOR SAYS:**
"Every user gets one profile with a display name.
Not zero-or-many.
One.
Here's the surprise: in the database, one-to-one is built exactly like one-to-many, a foreign key on the child table.
Two small additions make it one-to-one."

**ASK STUDENTS:**
"I'm going to add two things: `uselist=False` and `unique=True`.
One of them controls how Python behaves.
The other protects the data in the database.
Which is which?"

Listen for: `uselist=False` controls the ORM (you get an object instead of a list).
`unique=True` on `user_id` protects the database (no two profiles for one user).

**CODE:** In `app/models.py`, add the `profile` line to `User`, and add the `Profile` class between `User` and `Document`.

```python
    # One-to-one: uselist=False makes user.profile a single object, not a list.
    profile = db.relationship("Profile", back_populates="user", uselist=False)
```

```python
class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(80), nullable=False)

    # unique=True is what makes this one-to-one IN THE DATABASE:
    # no two profiles can point at the same user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    user = db.relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<Profile id={self.id} display_name={self.display_name!r}>"
```

```bash
flask --app run db migrate -m "Create profiles table"
flask --app run db upgrade
python seed.py --checkpoint 2
pytest -q --checkpoint 2
git diff 02-one-to-one -- app/models.py
```

**EXPLAIN:**
- "`uselist=False` is purely Python.
  It changes `user.profile` from a list to a single object.
  It adds nothing to the database."
- "`unique=True` on `user_id` is purely database.
  It creates a UNIQUE constraint.
  It's what actually *guarantees* one-to-one."
- "If I only had `uselist=False`, the database would happily store two profiles for Ada, and SQLAlchemy would give me one of them and warn about the other.
  If I only had `unique=True`, the data would be safe, but `user.profile` would be a list with one item in it.
  We want both."
- "Where does the foreign key go in one-to-one?
  On whichever side is 'owned'.
  A profile can't exist without a user, so the profile holds `user_id`."

**ASK STUDENTS (predict before running):**
"If I bypass the relationship and insert a second profile directly with `user_id=1`, what happens on commit?"

Listen for: an `IntegrityError` from the UNIQUE constraint.

```bash
flask --app run shell
```

```python
>>> from app import db
>>> from app.models import User, Profile
>>> ada = db.session.get(User, 1)
>>> ada.profile
>>> ada.profile.user
>>> db.session.add(Profile(display_name="Second Ada", user_id=1))
>>> db.session.commit()
>>> db.session.rollback()
>>> exit()
```

**EXPECTED RESULT:**

- `flask db migrate` prints `Detected added table 'profiles'`.
- `python seed.py --checkpoint 2` prints `Seeded 2 users, 3 documents, 2 profiles.`
- `pytest -q --checkpoint 2` prints `8 passed`.
- Shell:

```
>>> ada.profile
<Profile id=1 display_name='Ada L.'>
>>> ada.profile.user
<User id=1 email='ada@example.com'>
>>> db.session.commit()
Traceback (most recent call last):
  ...
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: profiles.user_id
```

Scroll to the **last line** of the traceback and read it aloud.

**COMMON MISTAKE:** Putting `uselist=False` on the `Profile.user` side instead of `User.profile`.
`Profile.user` is already a single object, because the foreign key is on `profiles`.
`uselist=False` belongs on the side that would otherwise be a list.

**RECOVERY:** If the shell is stuck with `PendingRollbackError`, type `db.session.rollback()`.
If the model is broken: `git checkout 02-one-to-one -- app/models.py`, then rerun the migrate, upgrade, and seed commands.

**TRANSITION:**
"So far each foreign key has pointed in one direction.
What happens when *both* sides can have many?"

## Step 5: Complex example, many-to-many (Document and Tag)

**TIME:** Minute 32
**Checkpoint reached:** `03-many-to-many`

**INSTRUCTOR SAYS:**
"A document can have many tags: 'flask', 'sqlalchemy'.
A tag can label many documents.
Neither table can hold the foreign key alone."

**ASK STUDENTS:**
"If I tried to put a `tag_id` column on `documents`, what would break?"

Listen for: a document could then have only one tag.
And putting `document_id` on `tags` means a tag could only label one document.

**CODE:** In `app/models.py`, add the association table at the **top** of the file (below the import), add the `tags` line to `Document`, and add the `Tag` class at the bottom.

```python
# Association table for the Document <-> Tag many-to-many relationship.
# It has no model class: each row just says "this document has this tag".
# The composite primary key stops the same tag being attached twice.
document_tags = db.Table(
    "document_tags",
    db.Column("document_id", db.Integer, db.ForeignKey("documents.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)
```

```python
    # inside class Document, below owner
    tags = db.relationship("Tag", secondary=document_tags, back_populates="documents", order_by="Tag.name")
```

```python
class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    documents = db.relationship("Document", secondary=document_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag id={self.id} name={self.name!r}>"
```

```bash
flask --app run db migrate -m "Create tags and document_tags tables"
flask --app run db upgrade
python seed.py --checkpoint 3
pytest -q --checkpoint 3
git diff 03-many-to-many -- app/models.py
```

**EXPLAIN:**
- "`document_tags` is a plain table, not a model.
  It has two foreign keys and nothing else.
  Each row is one pairing."
- "Both columns together form the primary key.
  So the pair (document 1, tag 1) can exist only once.
  That's another database constraint doing work for us."
- "`secondary=document_tags` tells SQLAlchemy to walk through the association table.
  I never insert rows into it by hand.
  I append to `document.tags` and SQLAlchemy writes the row."
- "It has to be defined *above* `Document` because `Document` refers to the Python variable `document_tags` directly."
- "`order_by="Tag.name"` just makes the tag list come back alphabetically so our API output is predictable."
- "`Tag.name` is `unique=True`.
  Keep that in mind; it's going to matter at minute 78."

**ASK STUDENTS (predict before running):**
"The seed tags two documents with 'flask'.
How many documents will `flask_tag.documents` return, and how many rows are in `document_tags` in total?"

Listen for: 2 documents.
4 rows in total (document 1 has two tags, documents 2 and 3 have one each).

```bash
flask --app run shell
```

```python
>>> from app import db
>>> from app.models import Document, Tag, document_tags
>>> doc = db.session.get(Document, 1)
>>> doc.tags
>>> flask_tag = Tag.query.filter_by(name="flask").first()
>>> flask_tag.documents
>>> db.session.execute(db.select(document_tags)).all()
>>> exit()
```

**EXPECTED RESULT:**

- `flask db migrate` prints `Detected added table 'tags'` and `Detected added table 'document_tags'`.
- `python seed.py --checkpoint 3` prints `Seeded 2 users, 3 documents, 2 profiles, 3 tags.`
- `pytest -q --checkpoint 3` prints `10 passed`.
- Shell:

```
>>> doc.tags
[<Tag id=1 name='flask'>, <Tag id=2 name='sqlalchemy'>]
>>> flask_tag.documents
[<Document id=2 title='Marshmallow Basics'>, <Document id=1 title='Flask Relationships'>]   (order may vary)
>>> db.session.execute(db.select(document_tags)).all()
[(2, 1), (3, 3), (1, 1), (1, 2)]   (order may vary)
```

**COMMON MISTAKE:** Defining `document_tags` *below* the `Document` class.
Python raises `NameError: name 'document_tags' is not defined` when it reads `secondary=document_tags`.

**RECOVERY:** Move the `document_tags = db.Table(...)` block to the top of the file.
Or: `git checkout 03-many-to-many -- app/models.py`, then rerun the migrate, upgrade, and seed commands.

**TRANSITION:**
"We now have all three relationship types.
Before we move to the real application, let's think about how these relationships should show up in JSON."

## Step 6: Preview of Chunks, nested serialization, and validation

**TIME:** Minute 37
**No code is committed in this step.** This is a whiteboard step.

**INSTRUCTOR SAYS:**
"In a knowledge base, a long document gets split into small pieces called chunks, so a retrieval system can later find the one paragraph that answers a question.
That's one more one-to-many: document to chunks.
Let's look at what an API consumer would want back when they ask for one document."

Put this on screen:

```json
{
  "data": {
    "id": 1,
    "title": "Flask Relationships",
    "source_url": "https://example.com/flask",
    "tags": [{ "id": 1, "name": "flask" }],
    "chunks": [{ "id": 1, "position": 0, "content": "SQLAlchemy relationships connect..." }]
  }
}
```

**ASK STUDENTS:**
"Our tag objects have a `documents` relationship.
If the tags inside this document also listed *their* documents, and those documents listed their tags, what would happen?"

Listen for: it would go on forever (infinite recursion), or at least become enormous.

**CODE:** Show this shape only; don't type it yet.
We type it for real in step 10.

```python
class TagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    # no "documents" field on purpose


class DocumentSchema(Schema):
    ...
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)
    chunks = fields.List(fields.Nested(ChunkSchema), dump_only=True)
```

**EXPLAIN:**
- "The database relationship goes both ways.
  The API response does not have to."
- "We decide the direction: a document shows its tags; a tag inside a document does not show its documents."
- "Notice what's missing from the JSON: the owner's email and profile.
  The database has them.
  This response doesn't need them."
- "And when a client *sends* us a document, we'll want rules: title required, 3 to 120 characters; URL must be a real URL; chunk positions can't be negative.
  That's validation, and we'll build it next."

**EXPECTED RESULT:** Students can say which side of each relationship appears in the JSON and why.

**COMMON MISTAKE:** Students assume the API must mirror the database exactly.

**RECOVERY:** Ask "Would a mobile app listing ten documents want every chunk of every document?" and let them reason it out.

**TRANSITION:**
"That's the concept review.
Now let's build something real."

---

# Segment 3: Real-World Application / Live Coding (minutes 40 to 85)

## Step 7: The scenario and cardinality

**TIME:** Minute 40

**INSTRUCTOR SAYS:**
"We're building the backend of a knowledge-base application.
Users upload documents.
Documents are broken into chunks that another system could retrieve later.
Documents can also have tags.
We are *not* building the AI part.
We're building the data layer an AI feature would stand on."

**ASK STUDENTS:**
"Before I show you the model, work with a neighbor for 60 seconds.
What's the cardinality of each of these?"

Write this on the board and wait:

```
User     → Profile    ?
User     → Document   ?
Document → Chunk      ?
Document → Tag        ?
```

Then, for each one: "Where does the foreign key go?"

Take answers from different students.
**Only then** check [Answer Key A](#answer-key-a-cardinality) at the bottom of this file.

**CODE:** None yet.

**EXPLAIN:**
- "Three of these four are already in `models.py` from the concept review.
  The one we haven't built is Document to Chunk."
- "Chunks are the retrieval-specific piece: they're what a search or AI system would actually read."

**EXPECTED RESULT:** Students agree on all four cardinalities and foreign-key locations.

**COMMON MISTAKE:** Saying Document to Tag is one-to-many.
Ask: "Can the tag 'flask' be on two documents at once?"

**RECOVERY:** If the class is split, draw two documents and one tag with arrows; the second arrow settles it.

**TRANSITION:**
"Let's add the missing relationship, and this time we'll put real rules into the database."

## Step 8: The Chunk model with CHECK and UNIQUE constraints

**TIME:** Minute 43
**Checkpoint reached:** `04-document-chunks`

**INSTRUCTOR SAYS:**
"Each chunk belongs to one document and has a `position`: 0 for the first piece, 1 for the second, and so on.
Two rules make sense for position.
It can't be negative.
And one document can't have two chunks at the same position."

**ASK STUDENTS:**
"Where does the foreign key go for Document to Chunk?
And which of those two rules could a single column's `unique=True` handle?"

Listen for: `document_id` on `chunks`.
Neither rule works with `unique=True` on one column: position 0 must be allowed in *every* document, so uniqueness must be on the *pair* (`document_id`, `position`).

**CODE:** In `app/models.py`, add the `chunks` line to `Document` (below `owner`), and add the `Chunk` class between `Document` and `Tag`.

```python
    # inside class Document, below owner
    chunks = db.relationship("Chunk", back_populates="document", order_by="Chunk.position")
```

```python
class Chunk(db.Model):
    __tablename__ = "chunks"
    __table_args__ = (
        # The database refuses negative positions, no matter who inserts the row.
        db.CheckConstraint("position >= 0", name="ck_chunks_position_non_negative"),
        # A document cannot have two chunks at the same position.
        db.UniqueConstraint("document_id", "position", name="uq_chunks_document_position"),
    )

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)

    document = db.relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk id={self.id} document_id={self.document_id} position={self.position}>"
```

```bash
flask --app run db migrate -m "Create chunks table"
flask --app run db upgrade
python seed.py --checkpoint 4
pytest -q --checkpoint 4
git diff 04-document-chunks -- app/models.py
```

**EXPLAIN:**
- "`__table_args__` is where table-level constraints go, the ones that aren't about a single column."
- "`CheckConstraint("position >= 0")` is SQL that the database runs on every insert and update."
- "`UniqueConstraint("document_id", "position")` is a composite unique: position 0 can appear once *per document*."
- "Naming the constraints makes errors readable.
  You'll see that name in the error message in a minute."
- "`order_by="Chunk.position"` means `document.chunks` always comes back in reading order.
  That matters for retrieval: you want to reconstruct the original text in order."
- "`content` is `db.Text`, not `String(...)`, because chunks can be long."

**EXPECTED RESULT:**

- `flask db migrate` prints `Detected added table 'chunks'`.
  The migration file lists `sa.CheckConstraint('position >= 0', ...)` and `sa.UniqueConstraint('document_id', 'position', ...)`.
- `python seed.py --checkpoint 4` prints `Seeded 2 users, 3 documents, 2 profiles, 3 tags, 5 chunks.`
- `pytest -q --checkpoint 4` prints `13 passed`.
- **This is the last migration: the database schema never changes again.**
  From here on, plain `python seed.py` works too.

**COMMON MISTAKE:** Writing `__table_args__ = (db.CheckConstraint(...))` with one constraint and no trailing comma.
That's not a tuple.
With two constraints (as here) it's fine; with one you need `(constraint,)`.

**RECOVERY:** `git checkout 04-document-chunks -- app/models.py`, then rerun the migrate, upgrade, and seed commands.

**TRANSITION:**
"Our schema won't validate position yet, because we haven't written schemas at all.
So what happens if some code tries to insert a negative position right now?"

## Step 9: Database constraints in action

**TIME:** Minute 49

**INSTRUCTOR SAYS:**
"There's no API and no Marshmallow involved here.
This is like a teammate writing a quick script, or a bug in some other part of the system."

**ASK STUDENTS:**
"I'm going to insert a chunk with `position=-1` directly through SQLAlchemy.
Will it save?"

Listen for: no, the CHECK constraint rejects it with an `IntegrityError`.

**CODE:**

```bash
flask --app run shell
```

```python
>>> from app import db
>>> from app.models import Chunk, Document
>>> doc = db.session.get(Document, 1)
>>> doc.chunks
>>> db.session.add(Chunk(document_id=1, position=-1, content="Oops"))
>>> db.session.commit()
>>> db.session.rollback()
```

"Now position 0 again for document 1.
Position 0 already exists for this document.
Prediction?"

```python
>>> db.session.add(Chunk(document_id=1, position=0, content="Duplicate"))
>>> db.session.commit()
>>> db.session.rollback()
>>> exit()
```

**EXPLAIN:**
- "No Marshmallow ran here.
  The database protected itself."
- "This is why database constraints matter even when the API has validation: not every write comes through the API."
- "After an `IntegrityError`, the session is in a failed state.
  `rollback()` resets it.
  Our routes will need to do the same thing."

**EXPECTED RESULT:**

```
>>> doc.chunks
[<Chunk id=1 document_id=1 position=0>, <Chunk id=2 document_id=1 position=1>]
...
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) CHECK constraint failed: ck_chunks_position_non_negative
...
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: chunks.document_id, chunks.position
```

**COMMON MISTAKE:** Forgetting `db.session.rollback()` and getting `PendingRollbackError` on the next command.

**RECOVERY:** Type `db.session.rollback()`.
If the shell is hopelessly confused, `exit()` and restart `flask --app run shell`.

**TRANSITION:**
"The database can say 'no'.
But look at that error: a Python traceback with SQL in it.
An API consumer can't use that.
Let's work on the other end of the pipeline: turning objects into clean JSON."

## Step 10: Serialization with Marshmallow schemas

**TIME:** Minute 52

**INSTRUCTOR SAYS:**
"Open `app/schemas.py`.
A schema is a description of what the JSON looks like.
We'll start with output only, `dump()`, and add validation rules after."

**ASK STUDENTS:**
"Our `Document` model has `id`, `title`, `source_url`, `owner_id`, `owner`, `chunks`, and `tags`.
Which of those should a client *never* send us when creating a document?"

Listen for: `id` (the database assigns it).
Also `chunks` and `tags`: in our API, those are added through their own endpoints.

**CODE:** Replace the contents of `app/schemas.py`:

```python
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
```

If short on time, type `TagSchema`, `ChunkSchema`, and `DocumentSchema`, then run `git checkout 05-serialization -- app/schemas.py` for the rest.

**ASK STUDENTS (predict before running):**
"What Python type does `document_schema.dump(doc)` return: a `Document`, a JSON string, or something else?"

Listen for: a plain `dict`.
Flask turns the dict into a JSON string when we return it from a route.

```bash
flask --app run shell
```

```python
>>> from app import db
>>> from app.models import Document
>>> from app.schemas import document_schema, document_list_schema
>>> doc = db.session.get(Document, 1)
>>> result = document_schema.dump(doc)
>>> type(result)
>>> result
>>> document_list_schema.dump([doc])
>>> exit()
```

**EXPLAIN:**
- "`dump_only=True` means 'show this in output, reject it in input'.
  The client never gets to choose an `id`."
- "`fields.Nested(TagSchema)` means 'for each tag, use `TagSchema` to turn it into a dict'.
  That's where the relationship turns into nested JSON."
- "`TagSchema` has no `documents` field.
  That's the decision that prevents circular output."
- "`UserSchema` nests the profile (one-to-one, small) but not the documents (one-to-many, could be huge)."
- "`document_list_schema` reuses the same schema, with `many=True` for a list and `exclude=("chunks",)` to leave the heavy part out."

**EXPECTED RESULT:**

```
>>> type(result)
<class 'dict'>
>>> result
{'id': 1, 'title': 'Flask Relationships', 'source_url': 'https://example.com/flask', 'owner_id': 1, 'tags': [{'id': 1, 'name': 'flask'}, {'id': 2, 'name': 'sqlalchemy'}], 'chunks': [{'id': 1, 'position': 0, 'content': 'SQLAlchemy relationships connect Python objects through foreign keys.'}, {'id': 2, 'position': 1, 'content': 'back_populates keeps both sides of a relationship in sync.'}]}
>>> document_list_schema.dump([doc])
[{'id': 1, 'title': 'Flask Relationships', 'source_url': 'https://example.com/flask', 'owner_id': 1, 'tags': [{'id': 1, 'name': 'flask'}, {'id': 2, 'name': 'sqlalchemy'}]}]
```

**COMMON MISTAKE:** `fields.Nested(TagSchema)` without `fields.List(...)` around it for a list relationship.
Marshmallow then tries to read `name` from the list itself and the tags come out wrong.
(`fields.Nested(TagSchema, many=True)` is an equivalent alternative.)

**RECOVERY:** `git checkout 05-serialization -- app/schemas.py`, then restart the shell.

**TRANSITION:**
"We can turn objects into dicts.
Let's put that behind real URLs."

## Step 11: GET endpoints

**TIME:** Minute 57
**Checkpoint reached:** `05-serialization`

**INSTRUCTOR SAYS:**
"Open `app/routes.py`.
The starter already gave us two helpers, `success_response` and `error_response`.
Every response in this API is either `{"data": ...}` or `{"error": ..., "details": ...}`.
Consistent shapes mean a client can handle every response with the same code."

**ASK STUDENTS:**
"If someone asks for document 999 and it doesn't exist, what status code should we return, and what should the body look like?"

Listen for: 404, with the error envelope.

**CODE:** Update the imports at the top of `app/routes.py`, and add two routes below `health`:

```python
from flask import Blueprint

from app import db
from app.models import Document
from app.schemas import document_list_schema, document_schema
```

```python
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
```

```bash
pytest -q --checkpoint 5
git diff 05-serialization -- app/schemas.py app/routes.py
```

Start the server in Terminal 1 (leave it running for the rest of class):

```bash
python run.py
```

In Terminal 3:

```bash
curl http://127.0.0.1:5555/documents
curl http://127.0.0.1:5555/documents/1
curl http://127.0.0.1:5555/documents/999
```

**EXPLAIN:**
- "The route's job is small: find the object, pick the schema, wrap the result in the envelope."
- "`/documents` shows tags but no chunks.
  `/documents/1` shows both.
  Same database, same model, two different API representations, on purpose."
- "`<int:document_id>` means Flask only matches integers.
  `/documents/abc` is a 404 before our code even runs."

**EXPECTED RESULT:**

- `pytest -q --checkpoint 5` prints `21 passed`.
- `curl .../documents/1` returns `{"data": {"id": 1, "title": "Flask Relationships", ... "tags": [...], "chunks": [...]}}`.
- `curl .../documents` returns three documents, each **without** a `chunks` key.
- `curl .../documents/999` returns:

```json
{
  "error": "not_found",
  "details": {
    "document_id": ["Document 999 does not exist."]
  }
}
```

**COMMON MISTAKE:** Returning `document_schema.dump(documents)` (the single-object schema) for a list.
You get a dict of empty or wrong values instead of a list.

**RECOVERY:** Use `document_list_schema` for lists.
If the server won't start: check Terminal 1 for the error, then `git checkout 05-serialization -- app/schemas.py app/routes.py` and restart `python run.py`.

**TRANSITION:**
"Data can come out.
Now let's let data come *in*, and that's where things get dangerous."

## Step 12: Deserialization and validation

**TIME:** Minute 61
**Checkpoint reached:** `06-deserialization-validation`

**INSTRUCTOR SAYS:**
"`load()` is the other direction: raw input in, clean Python data out.
But right now our schema has no rules at all."

**ASK STUDENTS:**
"With the schema as it is right now, what will `document_schema.load({"title": "", "source_url": "not-a-url"})` return?"

Listen for: it returns the data unchanged.
There are no rules yet, so everything is accepted.

**CODE:** Demonstrate the problem **before** adding rules:

```bash
flask --app run shell
```

```python
>>> from app.schemas import document_schema
>>> document_schema.load({"title": "", "source_url": "not-a-url"})
{'title': '', 'source_url': 'not-a-url'}
>>> exit()
```

"No owner, empty title, garbage URL, and Marshmallow said 'looks good'.
Let's fix that."

Update `app/schemas.py`.
Change the import and add `not_blank` above the schemas:

```python
from marshmallow import Schema, ValidationError, fields, validate


def not_blank(value):
    """Custom validator: reject strings that are empty or only whitespace."""
    if not value.strip():
        raise ValidationError("Cannot be blank.")
```

Then change these field lines:

```python
# TagSchema
    name = fields.Str(required=True, validate=validate.Length(min=2, max=50))

# ChunkSchema
    position = fields.Int(required=True, validate=validate.Range(min=0))
    content = fields.Str(required=True, validate=not_blank)

# DocumentSchema
    title = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    # Optional: may be left out or sent as null, but if present it must be a URL.
    source_url = fields.Url(allow_none=True)
    owner_id = fields.Int(required=True)

# UserSchema
    email = fields.Email(required=True)
```

```bash
pytest -q --checkpoint 6
git diff 06-deserialization-validation -- app/schemas.py
```

**ASK STUDENTS (predict before each line):**
Run these one at a time, and ask "what comes back?" before each one.

```bash
flask --app run shell
```

```python
>>> from app.schemas import document_schema, chunk_schema, user_schema
>>> document_schema.load({"title": "Vector Search Notes", "owner_id": 1})
>>> document_schema.load({"title": "", "source_url": "not-a-url"})
>>> chunk_schema.load({"position": -1, "content": "   "})
>>> user_schema.load({"email": "not-an-email"})
>>> document_schema.load({"id": 99, "title": "Vector Search Notes", "owner_id": 1})
>>> exit()
```

**EXPLAIN:**
- "`required=True`: the key must be present.
  The error is 'Missing data for required field.'"
- "`validate.Length(min=3, max=120)`: string length.
  The database column says `String(120)`, but **SQLite does not enforce string length**.
  This validator is the only thing actually enforcing it here."
- "`fields.Url` and `fields.Email` are field *types* that validate format.
  `allow_none=True` lets a client send `null` for the URL, which matches `nullable=True` on the column."
- "`validate.Range(min=0)` is the schema-level twin of our CHECK constraint.
  Same rule, two layers."
- "`not_blank` is a custom validator: any function that raises `ValidationError`.
  `Length(min=1)` would accept three spaces; `not_blank` doesn't."
- "`ValidationError.messages` is a dict of field name to list of messages.
  Marshmallow collects *all* the errors at once instead of stopping at the first one.
  That's great for API consumers."
- "The first `load()` returned a **dict**, not a `Document`.
  And nothing touched the database.
  `load()` validates; it doesn't save."
- "Sending `id` fails with 'Unknown field.' That's `dump_only=True` protecting us: clients can't choose their own ids."

**EXPECTED RESULT:**

- `pytest -q --checkpoint 6` prints `32 passed`.
- Shell:

```
>>> document_schema.load({"title": "Vector Search Notes", "owner_id": 1})
{'title': 'Vector Search Notes', 'owner_id': 1}
>>> document_schema.load({"title": "", "source_url": "not-a-url"})
marshmallow.exceptions.ValidationError: {'title': ['Length must be between 3 and 120.'], 'source_url': ['Not a valid URL.'], 'owner_id': ['Missing data for required field.']}
>>> chunk_schema.load({"position": -1, "content": "   "})
marshmallow.exceptions.ValidationError: {'position': ['Must be greater than or equal to 0.'], 'content': ['Cannot be blank.']}
>>> user_schema.load({"email": "not-an-email"})
marshmallow.exceptions.ValidationError: {'email': ['Not a valid email address.']}
>>> document_schema.load({"id": 99, "title": "Vector Search Notes", "owner_id": 1})
marshmallow.exceptions.ValidationError: {'id': ['Unknown field.']}
```

**COMMON MISTAKE:** Writing `validate=validate.Length(3, 120)` is fine, but `validate=Length(min=3, max=120)` fails with `NameError` because only the `validate` module was imported.

**RECOVERY:** `git checkout 06-deserialization-validation -- app/schemas.py`, then restart the shell.

**TRANSITION:**
"Our schema can now say 'no' with a useful message.
Let's wire it to a POST endpoint."

## Step 13: POST /documents, the happy path

**TIME:** Minute 68

**INSTRUCTOR SAYS:**
"Here's our pipeline diagram again.
A POST route is exactly those arrows, in order: load, build the model, commit, dump."

**ASK STUDENTS:**
"The schema checked that `owner_id` is an integer.
Can the schema tell us whether user 42 actually exists?"

Listen for: no.
The schema only sees the request, not the database.
The route has to look the user up.

**CODE:** In `app/routes.py`, update the imports:

```python
from flask import Blueprint, request

from app import db
from app.models import Document, User
from app.schemas import document_list_schema, document_schema
```

Add this route at the bottom.
**Type it without try/except on purpose**; we add that in step 14.

```python
@api.post("/documents")
def create_document():
    # 1. Validate and deserialize the incoming JSON.
    data = document_schema.load(request.get_json())

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
```

**ASK STUDENTS (predict before running):**
"What status code, and what `id` will the new document get?"

Listen for: 201 Created, and id 4 (the seed made three documents).

```bash
curl -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "Vector Search Notes", "source_url": "https://example.com/vectors", "owner_id": 1}'
```

**EXPLAIN:**
- "`data` is a plain dict.
  We build the `Document` ourselves, which keeps it explicit what goes into the database."
- "`data.get("source_url")` because it's optional: the key may not be there."
- "Passing `owner=owner` sets `owner_id` for us through the relationship."
- "After `commit()`, the document has an `id`, and `dump()` includes empty `tags` and `chunks` lists.
  Nested output works for new objects too."
- "201 means 'created'.
  200 would work, but 201 tells the client something more specific."

**EXPECTED RESULT:**

```json
{
  "data": {
    "id": 4,
    "title": "Vector Search Notes",
    "source_url": "https://example.com/vectors",
    "owner_id": 1,
    "tags": [],
    "chunks": []
  }
}
```

**COMMON MISTAKE:** Forgetting `-H "Content-Type: application/json"` in curl.
Flask then refuses to parse the body and returns an HTML `415 Unsupported Media Type` page.

**RECOVERY:** Add the header and resend.
If the route itself is broken: `git checkout 07-api-responses -- app/routes.py` (the server reloads by itself).
Then run `python seed.py` if you want document ids to start from 4 again.

**TRANSITION:**
"That's the happy path.
Now let's be a bad client."

## Step 14: POST /documents with invalid data, and handling ValidationError

**TIME:** Minute 73
**Checkpoint reached:** `07-api-responses`

**INSTRUCTOR SAYS:**
"I'm going to send an empty title and a broken URL, and no owner at all."

**ASK STUDENTS:**
"We saw `load()` raise a `ValidationError` in the shell.
Our route doesn't catch it.
What will the client receive?"

Listen for: a 500 Internal Server Error, not a helpful message.

**CODE:** Send the bad request, showing only the status code (the debug error page is long HTML):

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "", "source_url": "not-a-url"}'
```

Point at Terminal 1.
The last line of the traceback is `marshmallow.exceptions.ValidationError: {...}`.

"The validation *worked*.
We just didn't tell the client about it.
A 500 says 'the server broke', which is not true: the client sent bad data."

Now wrap the `load()` call.
Replace step 1 in `create_document` with:

```python
    # 1. Validate and deserialize the incoming JSON.
    try:
        data = document_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("validation_error", err.messages, 400)
```

And add the import at the top:

```python
from marshmallow import ValidationError
```

**ASK STUDENTS (predict before running):**
"Same bad request.
What status code now, and what keys will be in `details`?"

Listen for: 400, with `title`, `source_url`, and `owner_id`.

```bash
curl -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "", "source_url": "not-a-url"}'
```

Then verify the checkpoint:

```bash
pytest -q --checkpoint 7
git diff 07-api-responses -- app/routes.py
```

**EXPLAIN:**
- "`err.messages` is already exactly the shape we want for `details`.
  We just put it in our envelope."
- "400 means 'your request was wrong'.
  500 means 'we broke'.
  The difference matters to whoever calls this API."
- "The error lists every problem at once, so the client can fix everything in one go."
- "`get_json(silent=True)` returns `None` instead of raising when the body isn't valid JSON.
  `or {}` turns `None` into an empty dict, so Marshmallow reports every required field as missing, in our envelope, instead of Flask returning an HTML error page."
- "Nothing was written to the database.
  Validation stopped the request before persistence logic ever ran."

**EXPECTED RESULT:**

- First curl prints `500`.
- Second curl returns status 400 with:

```json
{
  "error": "validation_error",
  "details": {
    "title": ["Length must be between 3 and 120."],
    "source_url": ["Not a valid URL."],
    "owner_id": ["Missing data for required field."]
  }
}
```

- `pytest -q --checkpoint 7` prints `35 passed`.

**COMMON MISTAKE:** Returning `err` or `str(err)` instead of `err.messages`.
You get a flat string instead of a per-field dict.

**RECOVERY:** `git checkout 07-api-responses -- app/routes.py`.
The server reloads automatically.

**TRANSITION:**
"Marshmallow now catches bad *shapes*.
So here's a question that trips up a lot of developers."

## Step 15: Why a UNIQUE constraint if Marshmallow validates?

**TIME:** Minute 78
**Checkpoint used:** `08-final` (the finished `app/routes.py` is pulled from `main`, not typed)

**INSTRUCTOR SAYS:**
"Tag names are unique.
Our `TagSchema` checks that `name` is present and 2 to 50 characters."

**ASK STUDENTS:**
"If Marshmallow validates our request, why bother putting UNIQUE on the database column?"

Give them 20 seconds.
Take two or three answers.

Listen for:
1. Marshmallow can't see the table.
   It doesn't know "flask" already exists.
2. Data can arrive without going through the schema (seed scripts, shell, other services).
3. Two requests at the same moment could both check "does it exist?", both get "no", and both insert.
   Only the database can stop that.

**INSTRUCTOR SAYS (the concise explanation):**
"Marshmallow validation gives API consumers useful feedback before invalid input reaches persistence logic.
Database constraints protect persistent data integrity even when data enters through some path other than the normal API schema.
These layers complement each other.
Marshmallow is the helpful receptionist who tells you your form is incomplete.
The database is the vault door.
You want both."

**CODE:** Save your live work, then bring in the finished routes file from `main`.
You stay on your branch, and only `app/routes.py` changes.
The database schema hasn't changed since checkpoint 04, so no migration or reseed is needed, and the server reloads by itself.

```bash
git add -A && git commit -m "Live session through checkpoint 07"
git checkout main -- app/routes.py
pytest -q
```

`pytest -q` (no flag: every checkpoint) prints `45 passed`.

Open `app/routes.py` and scroll to `create_tag`.
Point at the `try` / `except IntegrityError` / `rollback()` block.

**ASK STUDENTS (predict before running):**
"The seed already created a tag named 'flask'.
This request passes Marshmallow validation.
What will happen?"

```bash
curl -X POST http://127.0.0.1:5555/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "flask"}'

curl -X POST http://127.0.0.1:5555/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "embeddings"}'
```

**EXPLAIN:**
- "The schema said 'yes, this is a valid tag name'.
  The database said 'no, that name is taken'.
  Two different questions, two different layers."
- "We catch `IntegrityError`, roll back the session, and translate it into our error envelope with a 409 Conflict status."
- "409 means 'your request was fine, but it conflicts with what's already stored'.
  That's different from 400."
- "The same pattern protects `users.email` in `POST /users` and the (`document_id`, `position`) pair in `POST /documents/<id>/chunks`."

**EXPECTED RESULT:**

```json
{
  "error": "integrity_error",
  "details": {
    "name": ["Tag 'flask' already exists."]
  }
}
```

The second curl returns 201 with `{"data": {"id": 4, "name": "embeddings"}}`.

**COMMON MISTAKE:** Forgetting `db.session.rollback()` in the `except` block.
The *next* request that uses the session fails with `PendingRollbackError`.

**RECOVERY:** If git says `main` is unknown, run `git fetch origin` and then `git checkout origin/main -- app/routes.py`.
If the server is not responding, restart it with `python run.py`.

**TRANSITION:**
"We've been deciding what goes *into* the database.
Let's finish by deciding what comes *out*."

## Step 16: Intentional API response design

**TIME:** Minute 82

**INSTRUCTOR SAYS:**
"Our database knows every user's email, their profile, every document they own, every chunk, every tag."

**ASK STUDENTS:**
"Just because our database contains something, does every API consumer need to receive it?"

Listen for: no.
Some data is private, some is large, and some is irrelevant to that consumer.

**CODE:** No new code.
Show the difference between the two representations:

```bash
curl http://127.0.0.1:5555/documents
curl http://127.0.0.1:5555/documents/1
```

Point at `app/schemas.py`: `document_list_schema = DocumentSchema(many=True, exclude=("chunks",))`, and the missing `documents` field on `TagSchema`.

**EXPLAIN:**
- "The list endpoint leaves out chunks.
  A real document might have 500 chunks; a list of 50 documents would be 25,000 chunks nobody asked for."
- "No response includes the owner's email.
  The database relationship exists, and we chose not to follow it."
- "No tag includes its documents.
  That avoids circular output and keeps each response a predictable size."
- "Now imagine a retrieval or AI feature consuming this API later.
  It would want chunk content, position, and the document title, so it can quote a source.
  It would *not* want user emails or profiles.
  Sending private data into a prompt or a search index is a real risk, and every extra field costs space and tokens."
- "Designing the response is a decision, separate from designing the tables.
  The database models the truth.
  The schema models what *this* consumer needs."

**EXPECTED RESULT:** Students can name at least one thing the database has that the API deliberately doesn't return, and why.

**COMMON MISTAKE:** Students suggest nesting everything "just in case".
Ask: "What does it cost, and who is the 'case'?"

**RECOVERY:** If the discussion stalls, point at the size difference between the two curl outputs.

**TRANSITION:**
"Let's pull all of it together and follow one request through the whole stack."

If you reach this point before minute 85, use the [extension activities](#extension-activities-if-ahead-of-schedule) until minute 85.
Do not start the wrap-up early.

---

# Segment 4: Assessment Bridge / Exit Check (minutes 85 to 90)

## Step 17: Trace one request through the complete stack

**TIME:** Minute 85

**INSTRUCTOR SAYS:**
"One request, start to finish.
I'll point, you tell me what happens at each arrow."

Put this on screen next to `create_document` in `app/routes.py`:

```
POST /documents
  → JSON                     {"title": "Vector Search Notes", "owner_id": 1}
  → schema.load()            document_schema.load(request.get_json(silent=True) or {})
  → validation               required, Length(3, 120), Url, Int  →  ValidationError → 400
  → SQLAlchemy model         Document(title=..., source_url=..., owner=owner)
  → database constraints     NOT NULL, FOREIGN KEY owner_id → users.id
  → database                 db.session.commit()  → row in documents, id assigned
  → schema.dump()            document_schema.dump(document)
  → JSON response            {"data": {...}}, 201
```

**ASK STUDENTS:** Point at each line and ask:
"What happens here if something is wrong?"

Listen for:
- `load()` / validation: `ValidationError`, caught, 400 `validation_error`.
- Owner lookup: user doesn't exist, 400 `validation_error`.
- Database constraints: `IntegrityError` (for example, on a duplicate tag), rollback, 409 `integrity_error`.
- `dump()`: shapes the output; decides what the client sees.

**CODE:** Optional, if time allows, run the request one last time:

```bash
curl -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "Tracing a Request", "owner_id": 2}'
```

**EXPLAIN:**
- "Every arrow in this diagram is one line or a few lines of code in `create_document`."
- "Two guards: the schema near the top, the database near the bottom."

**EXPECTED RESULT:** A 201 response with a new document owned by user 2.

**COMMON MISTAKE:** Students say "`load()` saves it".
Correct gently: "`load()` validates; `commit()` saves."

**RECOVERY:** If the server is down, skip the curl; the trace works without it.

**TRANSITION:**
"Last thing: five quick questions.
Answer out loud, or in the chat."

## Step 18: Five rapid exit questions

**TIME:** Minute 88

**INSTRUCTOR SAYS:**
"Fast answers, one sentence each.
These are the core relational-database skills we practiced today."

**ASK STUDENTS:**

1. What makes a one-to-one relationship actually one-to-one?
2. Where does the foreign key normally go in one-to-many?
3. Why does many-to-many use an association table?
4. What is the difference between `dump()` and `load()`?
5. Why might we have both Marshmallow validation and a database constraint?

Answers are in [Answer Key B](#answer-key-b-exit-questions).

**CODE:** None.

**EXPLAIN:** Correct any wrong answers in one sentence.
Note which questions got weak answers; those are the topics to revisit.

**EXPECTED RESULT:** Most students can answer each question in a sentence.

**COMMON MISTAKE:** For question 1, answering only "`uselist=False`".
Push for the database half: "And what stops a second profile row?"

**RECOVERY:** If time runs out, post the five questions in the chat for students to answer asynchronously.

**TRANSITION (closing):**
"Everything today was one pipeline: JSON in, validated by Marshmallow, turned into models, protected by constraints, saved, and serialized back out on purpose.
The full working code is on the `main` branch, and the tests are written to be read.
Great work today."

---

# Extension activities (if ahead of schedule)

Use these, in order, whenever you reach a transition early.
Stop when the clock reaches the next scheduled step.
All of them work once step 15 is done, and most also work on earlier checkpoints.

### E1: Bug hunt, mismatched back_populates (3 minutes)

"I'm going to break one word.
Tell me what the error means."
In `app/models.py`, change `Document.owner` to `back_populates="document"` (singular) and run `python seed.py`.

Expected: `InvalidRequestError: Mapper 'Mapper[User(users)]' has no property 'document'.`
Ask: "Which class is it looking at, and what property is it looking for?"
Undo with `git checkout -- app/models.py`.

### E2: Students dictate a test (4 minutes)

"Dictate a test that proves a 121-character title is rejected."
Type it in `tests/test_06_deserialization_validation.py`, following `test_title_must_be_between_3_and_120_characters`:

```python
def test_title_cannot_be_121_characters():
    with pytest.raises(ValidationError) as error:
        document_schema.load({"title": "x" * 121, "owner_id": 1})

    assert error.value.messages == {"title": ["Length must be between 3 and 120."]}
```

Run `pytest -q -k 121`.
Ask: "What's the smallest title length that should pass?
Write that test too."

### E3: Live-code POST /documents/<id>/chunks (8 minutes)

Delete `create_chunk` from `app/routes.py` first.
Ask students to dictate each line, using `create_document` as a model.
Key questions:
- "What do we do if the document doesn't exist?" (404)
- "Which error does the schema catch, and which does the database catch?" (negative position vs duplicate position)

Compare with `git diff main -- app/routes.py` afterwards.

### E4: dump_only in action (2 minutes)

"Predict the response."

```bash
curl -X POST http://127.0.0.1:5555/documents \
  -H "Content-Type: application/json" \
  -d '{"id": 99, "title": "Sneaky", "owner_id": 1, "chunks": []}'
```

Expected: 400 with `"id": ["Unknown field."]` and `"chunks": ["Unknown field."]`.
Point at `dump_only=True` in `DocumentSchema`.

### E5: SQLite foreign keys are off by default (4 minutes)

In `app/__init__.py`, comment out the `@event.listens_for(Engine, "connect")` line.
Restart the shell and run:

```python
>>> from app import db
>>> from app.models import Document
>>> db.session.add(Document(title="Orphan", owner_id=999))
>>> db.session.commit()
```

Ask: "Did it save?
Should it have?"
It saves.
Then restore with `git checkout -- app/__init__.py`, rerun `python seed.py`, and repeat: `IntegrityError: FOREIGN KEY constraint failed`.
Point: "Constraints only protect you if the database actually enforces them."

### E6: Design discussion, "Flask" vs "flask" (4 minutes)

```bash
curl -X POST http://127.0.0.1:5555/tags -H "Content-Type: application/json" -d '{"name": "Flask"}'
```

It succeeds, because the UNIQUE constraint is case-sensitive in SQLite.
Ask: "Is that a bug?
Where would you fix it: in the schema, in the route, or in the database?
What would happen to data that's already stored?"
There is no single right answer; the point is that it's a product decision, not something to invent silently.

### E7: Design a retrieval-friendly chunk response (5 minutes)

"A search system gets back one chunk.
What does it need to show the user where the text came from?"
Sketch on the board (do not commit):

```python
class RetrievalChunkSchema(Schema):
    id = fields.Int()
    position = fields.Int()
    content = fields.Str()
    document = fields.Nested(DocumentSchema(only=("id", "title", "source_url")))
```

Ask: "Why `only=` here?
What would happen if we nested the full `DocumentSchema` with its chunks?"

### E8: What happens to chunks when a document is deleted? (3 minutes)

Ask: "If we deleted document 1, what should happen to its chunks?
What will SQLAlchemy try to do by default?"
By default, SQLAlchemy tries to set `chunks.document_id` to NULL, and `nullable=False` makes that fail.
Mention that `cascade="all, delete-orphan"` on `Document.chunks` is one way to express "chunks die with their document", and that it's a deliberate design choice.

---

# Answer keys

Do not scroll here until you have asked the question.

## Answer Key A: Cardinality

| Relationship         | Cardinality  | Foreign key                                                         |
| -------------------- | ------------ | ------------------------------------------------------------------- |
| User → Profile       | One-to-one   | `profiles.user_id`, NOT NULL and **UNIQUE**                         |
| User → Document      | One-to-many  | `documents.owner_id`, NOT NULL                                      |
| Document → Chunk     | One-to-many  | `chunks.document_id`, NOT NULL                                      |
| Document → Tag       | Many-to-many | neither table; `document_tags.document_id` and `document_tags.tag_id` |

## Answer Key B: Exit questions

1. **What makes a one-to-one relationship actually one-to-one?**
   A UNIQUE constraint on the foreign key (`profiles.user_id`) in the database.
   `uselist=False` only changes how Python presents it (an object instead of a list).
2. **Where does the foreign key normally go in one-to-many?**
   On the "many" side: `documents.owner_id`, `chunks.document_id`.
3. **Why does many-to-many use an association table?**
   A column can hold only one value, and both sides have many, so each pairing gets its own row in a third table.
4. **What is the difference between `dump()` and `load()`?**
   `dump()` serializes objects into dicts for output.
   `load()` validates and deserializes input into Python data, raising `ValidationError` on bad input.
5. **Why might we have both Marshmallow validation and a database constraint?**
   Marshmallow gives API consumers useful, specific feedback before persistence logic runs.
   Database constraints protect the stored data no matter how it arrives, and can enforce rules Marshmallow can't see, like uniqueness across the whole table.
