from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
migrate = Migrate()


# SQLite ignores FOREIGN KEY constraints unless we turn them on for every
# connection. Without this, a Document could point at a user that doesn't exist.
@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_app(test_config=None):
    app = Flask(__name__)

    # The database file is created at instance/knowledge_base.db
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///knowledge_base.db"
    app.json.sort_keys = False

    # Tests pass in their own settings (for example, an in-memory database).
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    # Adds the `flask db` commands. SQLite can't ALTER most things in place, so
    # batch mode makes Alembic copy the table instead when a column changes.
    migrate.init_app(app, db, render_as_batch=True)

    # Imported here so the models are registered before migrations or tables are created.
    from app import models  # noqa: F401
    from app.routes import api

    app.register_blueprint(api)

    return app
