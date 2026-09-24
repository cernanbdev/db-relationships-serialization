from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from flask_migrate import upgrade

from app import create_app, db

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def test_migrations_build_the_same_schema_as_the_models(tmp_path):
    # Run every migration against an empty database file...
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'migrated.db'}"})
    with app.app_context():
        upgrade(directory=str(MIGRATIONS_DIR))

        # ...then ask Alembic what `flask db migrate` would still want to change.
        with db.engine.connect() as connection:
            differences = compare_metadata(MigrationContext.configure(connection), db.metadata)

    # A difference here means a model changed without `flask db migrate` + `flask db upgrade`.
    assert differences == []
