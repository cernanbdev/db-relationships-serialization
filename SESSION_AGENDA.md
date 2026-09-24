# Session Agenda: Relationships, Serialization, and Validation

**Length:** 90 minutes
**Audience:** beginner software-engineering students who have completed Modules 21 (relationships), 22 (serialization), and 23 (constraints and validations)
**Project:** AI Knowledge Base API (this repository)

The detailed, word-for-word plan is in [INSTRUCTOR_SCRIPT.md](INSTRUCTOR_SCRIPT.md).
Recovery steps for every checkpoint are in [LIVE_CODING_CHECKPOINTS.md](LIVE_CODING_CHECKPOINTS.md).

## Learning goals

By the end of the session, students can:

1. Explain the difference between a foreign key and `db.relationship()`.
2. Explain why `uselist=False` and `unique=True` are both needed for a true one-to-one relationship.
3. Explain why many-to-many needs an association table.
4. Use `back_populates` to keep both sides of a relationship explicit and in sync.
5. Use Marshmallow `dump()` to serialize nested relationships without circular output.
6. Use Marshmallow `load()` to validate and deserialize request JSON.
7. Return consistent JSON success and validation-error responses.
8. Explain why schema validation and database constraints complement each other.

## High-level allocation

| Time      | Segment                                        |
| --------- | ---------------------------------------------- |
| 0 to 15   | Technical Q&A                                  |
| 15 to 40  | Concept Review                                 |
| 40 to 85  | Real-World Application / Live Coding           |
| 85 to 90  | Assessment Bridge / Exit Check                 |

## Detailed plan

### 0 to 15: Technical Q&A

| Minute | Activity                                                                                   |
| ------ | ------------------------------------------------------------------------------------------ |
| 0      | Welcome, state the session goal, open the floor for questions                              |
| 1 to 13 | Student questions; use the backup questions in the script if the room is quiet            |
| 13 to 15 | Park unanswered questions that later segments will cover; transition                     |

### 15 to 40: Concept Review

Code is typed live on the `live-session` branch, starting from `00-starter`.

| Minute   | Level        | Topic                                                           | Checkpoint reached   |
| -------- | ------------ | --------------------------------------------------------------- | -------------------- |
| 15 to 18 |              | Mental model: JSON to database and back                         |                      |
| 18 to 25 | Easy         | One-to-many: User to Documents                                  | `01-one-to-many`     |
| 25 to 32 | Intermediate | One-to-one: User to Profile (`uselist=False` vs `unique=True`)  | `02-one-to-one`      |
| 32 to 37 | Complex      | Many-to-many: Document and Tag                                  | `03-many-to-many`    |
| 37 to 40 | Complex      | Preview: Document to Chunk plus nested serialization and validation (whiteboard, no code) | |

### 40 to 85: Real-World Application / Live Coding

| Minute   | Topic                                                              | Checkpoint reached                |
| -------- | ------------------------------------------------------------------ | --------------------------------- |
| 40 to 43 | Scenario and cardinality prediction                                |                                   |
| 43 to 49 | Chunk model, CHECK and UNIQUE constraints                          | `04-document-chunks`              |
| 49 to 52 | Database constraint demo in `flask shell`                          |                                   |
| 52 to 57 | Serialization schemas and nested `dump()`                          |                                   |
| 57 to 61 | GET `/documents` and GET `/documents/<id>`                         | `05-serialization`                |
| 61 to 68 | Validation rules and `load()`                                      | `06-deserialization-validation`   |
| 68 to 73 | POST `/documents`: valid request                                   |                                   |
| 73 to 78 | POST `/documents`: invalid request, `ValidationError`, 400 response | `07-api-responses`               |
| 78 to 82 | Why UNIQUE in the database? Duplicate tag demo                     | `08-final` (checked out, not typed) |
| 82 to 85 | API response design for retrieval and AI features                  |                                   |

### 85 to 90: Assessment Bridge / Exit Check

| Minute   | Activity                                                                                 |
| -------- | ---------------------------------------------------------------------------------------- |
| 85 to 88 | Trace one POST `/documents` request through the complete stack                           |
| 88 to 90 | Five rapid exit questions                                                                |

The exit check is a synthesis of the relational-database skills practiced today.
It makes no claims about the content of the Module 24 assessment.

## If the class is moving faster than planned

Do not end early.
Use these activities, in this order, to fill the remaining time.
Each one reinforces a session goal.
Details and code are in the "Extension activities" section of [INSTRUCTOR_SCRIPT.md](INSTRUCTOR_SCRIPT.md).

| #  | Activity                                                            | Time   | Reinforces                        |
| -- | ------------------------------------------------------------------- | ------ | --------------------------------- |
| E1 | Bug hunt: break a `back_populates` name and read the error together | 3 min  | Goal 4                            |
| E2 | Students dictate a new test: a 121-character title is rejected      | 4 min  | Goal 6                            |
| E3 | Live-code POST `/documents/<id>/chunks`, then compare with `08-final` | 8 min | Goals 6, 7, 8                     |
| E4 | Send `"id": 99` and `"chunks": []` in a POST body; predict the error | 2 min  | Goal 5 (`dump_only`)              |
| E5 | Turn off the SQLite foreign-key PRAGMA and insert an orphan document | 4 min  | Goal 8                            |
| E6 | Design discussion: should `"Flask"` and `"flask"` be different tags? | 4 min  | Goal 8                            |
| E7 | Design a "retrieval chunk" response that includes the document title | 5 min  | Goal 5                            |
| E8 | Discussion: what should happen to chunks when a document is deleted? | 3 min  | Goals 1, 8                        |

## If the class is moving slower than planned

Protect the 85 to 90 exit check.
Cut in this order:

1. Skip the step 9 shell demo; point to `test_database_rejects_negative_chunk_position` instead.
2. At checkpoint 05, `git reset --hard 05-serialization` and walk through the diff instead of typing.
3. At checkpoint 06, `git reset --hard 06-deserialization-validation` and demo `load()` in the shell.
4. Shorten the API design discussion (step 16) to the single question and a one-sentence answer.

## Before class checklist

- [ ] Clone, create `.venv`, `pip install -r requirements.txt`
- [ ] `git checkout -b live-session 00-starter`
- [ ] `python seed.py` prints `Seeded 2 users.`
- [ ] `pytest -q` prints `1 passed`
- [ ] Editor font size large enough for the back row
- [ ] Three terminals open: server, shell/tests, curl
- [ ] `INSTRUCTOR_SCRIPT.md` open beside the editor
- [ ] `LIVE_CODING_CHECKPOINTS.md` open in a second tab
