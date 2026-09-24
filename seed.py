from sqlalchemy import MetaData

from app import create_app, db
from app.models import Chunk, Document, Profile, Tag, User

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

    # One-to-one: each user gets exactly one profile.
    ada.profile = Profile(display_name="Ada L.")
    grace.profile = Profile(display_name="Grace H.")

    # Many-to-many: tags are shared across documents.
    flask_tag = Tag(name="flask")
    sqlalchemy_tag = Tag(name="sqlalchemy")
    retrieval_tag = Tag(name="retrieval")

    # One-to-many: a user owns documents.
    relationships_doc = Document(
        title="Flask Relationships",
        source_url="https://example.com/flask",
        owner=ada,
        tags=[flask_tag, sqlalchemy_tag],
    )
    marshmallow_doc = Document(
        title="Marshmallow Basics",
        source_url="https://example.com/marshmallow",
        owner=ada,
        tags=[flask_tag],
    )
    chunking_doc = Document(
        title="Chunking for Retrieval",
        source_url=None,
        owner=grace,
        tags=[retrieval_tag],
    )

    # One-to-many: a document is split into ordered chunks.
    relationships_doc.chunks = [
        Chunk(position=0, content="SQLAlchemy relationships connect Python objects through foreign keys."),
        Chunk(position=1, content="back_populates keeps both sides of a relationship in sync."),
    ]
    marshmallow_doc.chunks = [
        Chunk(position=0, content="dump() turns objects into JSON-ready data; load() validates incoming data."),
    ]
    chunking_doc.chunks = [
        Chunk(position=0, content="Retrieval systems search small chunks instead of whole documents."),
        Chunk(position=1, content="Each chunk keeps a position so the original order can be rebuilt."),
    ]

    db.session.add_all([ada, grace, relationships_doc, marshmallow_doc, chunking_doc])
    db.session.commit()

    print(f"Seeded {User.query.count()} users, {Profile.query.count()} profiles, {Document.query.count()} documents, "
          f"{Chunk.query.count()} chunks, {Tag.query.count()} tags.")
