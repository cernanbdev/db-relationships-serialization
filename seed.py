"""Fill the database with sample data.

The tables come from migrations, so run `flask --app run db upgrade` first.

While building the app live, pass the checkpoint you have reached so the seed only
uses models that exist so far:

    python seed.py --checkpoint 2

With no flag it seeds everything, which is what the finished app needs.
"""

import argparse
import sys

from sqlalchemy.exc import OperationalError

from app import create_app, db

LAST_CHECKPOINT = 8


# Each seed step imports only the models it needs, so the earlier steps still work
# before the later models have been written. `sample` carries objects between steps.

def seed_users(sample):
    from app.models import User

    sample["ada"] = User(email="ada@example.com")
    sample["grace"] = User(email="grace@example.com")
    db.session.add_all([sample["ada"], sample["grace"]])
    return "users", User


def seed_documents(sample):
    from app.models import Document

    # One-to-many: a user owns documents.
    sample["relationships_doc"] = Document(
        title="Flask Relationships",
        source_url="https://example.com/flask",
        owner=sample["ada"],
    )
    sample["marshmallow_doc"] = Document(
        title="Marshmallow Basics",
        source_url="https://example.com/marshmallow",
        owner=sample["ada"],
    )
    sample["chunking_doc"] = Document(
        title="Chunking for Retrieval",
        source_url=None,
        owner=sample["grace"],
    )
    # Setting owner= does not add a document to the session, so add them explicitly.
    db.session.add_all([sample["relationships_doc"], sample["marshmallow_doc"], sample["chunking_doc"]])
    return "documents", Document


def seed_profiles(sample):
    from app.models import Profile

    # One-to-one: each user gets exactly one profile.
    sample["ada"].profile = Profile(display_name="Ada L.")
    sample["grace"].profile = Profile(display_name="Grace H.")
    return "profiles", Profile


def seed_tags(sample):
    from app.models import Tag

    # Many-to-many: tags are shared across documents.
    flask_tag = Tag(name="flask")
    sqlalchemy_tag = Tag(name="sqlalchemy")
    retrieval_tag = Tag(name="retrieval")

    sample["relationships_doc"].tags = [flask_tag, sqlalchemy_tag]
    sample["marshmallow_doc"].tags = [flask_tag]
    sample["chunking_doc"].tags = [retrieval_tag]
    return "tags", Tag


def seed_chunks(sample):
    from app.models import Chunk

    # One-to-many: a document is split into ordered chunks.
    sample["relationships_doc"].chunks = [
        Chunk(position=0, content="SQLAlchemy relationships connect Python objects through foreign keys."),
        Chunk(position=1, content="back_populates keeps both sides of a relationship in sync."),
    ]
    sample["marshmallow_doc"].chunks = [
        Chunk(position=0, content="dump() turns objects into JSON-ready data; load() validates incoming data."),
    ]
    sample["chunking_doc"].chunks = [
        Chunk(position=0, content="Retrieval systems search small chunks instead of whole documents."),
        Chunk(position=1, content="Each chunk keeps a position so the original order can be rebuilt."),
    ]
    return "chunks", Chunk


# (checkpoint that adds the model, seed step). The model layer is complete at 04.
SEED_STEPS = [
    (0, seed_users),
    (1, seed_documents),
    (2, seed_profiles),
    (3, seed_tags),
    (4, seed_chunks),
]


def parse_args():
    parser = argparse.ArgumentParser(description="Reset the database rows and fill them with sample data.")
    parser.add_argument(
        "--checkpoint",
        type=int,
        choices=range(LAST_CHECKPOINT + 1),
        default=LAST_CHECKPOINT,
        metavar="N",
        help=f"seed only the models that exist at checkpoint N (0-{LAST_CHECKPOINT}, default {LAST_CHECKPOINT})",
    )
    return parser.parse_args()


def main():
    checkpoint = parse_args().checkpoint
    app = create_app()

    with app.app_context():
        try:
            # Start fresh every time: delete every row, children before parents.
            # The tables themselves stay; only migrations create or change tables.
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())

            sample = {}
            seeded = [step(sample) for step_checkpoint, step in SEED_STEPS if step_checkpoint <= checkpoint]
            db.session.commit()
        except OperationalError as error:
            db.session.rollback()
            sys.exit(
                f"{error.orig}\n\n"
                "The database is missing a table the models expect.\n"
                "Run `flask --app run db migrate -m \"...\"` if you changed a model, "
                "then `flask --app run db upgrade`, and seed again."
            )

        counts = ", ".join(f"{model.query.count()} {label}" for label, model in seeded)
        print(f"Seeded {counts}.")


if __name__ == "__main__":
    main()
