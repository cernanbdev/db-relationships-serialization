from sqlalchemy import MetaData

from app import create_app, db
from app.models import Document, User

app = create_app()

with app.app_context():
    # Start fresh every time. Reflecting reads every table that is actually in the
    # database file, including tables from a later checkpoint that our models don't
    # know about yet, so all of them get dropped before we rebuild from the models.
    existing_tables = MetaData()
    existing_tables.reflect(bind=db.engine)
    existing_tables.drop_all(bind=db.engine)
    db.create_all()

    ada = User(email="ada@example.com")
    grace = User(email="grace@example.com")

    # One-to-many: a user owns documents.
    relationships_doc = Document(
        title="Flask Relationships",
        source_url="https://example.com/flask",
        owner=ada,
    )
    marshmallow_doc = Document(
        title="Marshmallow Basics",
        source_url="https://example.com/marshmallow",
        owner=ada,
    )
    chunking_doc = Document(
        title="Chunking for Retrieval",
        source_url=None,
        owner=grace,
    )

    db.session.add_all([ada, grace, relationships_doc, marshmallow_doc, chunking_doc])
    db.session.commit()

    print(f"Seeded {User.query.count()} users, {Document.query.count()} documents.")
