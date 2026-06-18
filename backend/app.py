"""
Motor Function Tracker — Flask API entry point.

Run from project root:
    python -m backend.app

Or:
    flask --app backend.app run --debug
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is on PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / "backend" / ".env")

from flask import Flask
from flask_cors import CORS

from backend.config import Config
from backend.database import init_db
from backend.routes import analyze_bp, sessions_bp
from backend.utils.errors import register_error_handlers


def create_app(config_class=Config) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["UPLOAD_DIR"] = Config.UPLOAD_DIR

    CORS(app, resources={r"/*": {"origins": "*"}})
    register_error_handlers(app)
    init_db(app)

    app.register_blueprint(analyze_bp, url_prefix="/api")
    app.register_blueprint(sessions_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return {
            "service": "Motor Function Tracker API",
            "version": "1.0.0",
            "endpoints": {
                "analyze_video": "POST /api/analyze-video",
                "analyze_frame": "POST /api/analyze-frame",
                "session": "GET /api/session/{id}",
                "history": "GET /api/history",
                "report": "GET /api/report/{id}",
                "health": "GET /api/health",
            },
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
