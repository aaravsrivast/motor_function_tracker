"""Database initialization and session management."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app and create tables."""
    db.init_app(app)
    db_path = app.config["SQLALCHEMY_DATABASE_URI"]
    if db_path.startswith("sqlite:///"):
        db_dir = db_path.replace("sqlite:///", "")
        from pathlib import Path
        Path(db_dir).parent.mkdir(parents=True, exist_ok=True)

    with app.app_context():
        db.create_all()
