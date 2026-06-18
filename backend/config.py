"""Application configuration for Motor Function Tracker backend."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB max upload
    UPLOAD_DIR = UPLOAD_DIR

    # Database: SQLite by default, PostgreSQL via DATABASE_URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'database' / 'motor_tracker.db'}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pose estimation settings
    POSE_MODEL = os.getenv("POSE_MODEL", "mediapipe")  # mediapipe | movenet | yolo
    POSE_MIN_DETECTION_CONFIDENCE = float(os.getenv("POSE_MIN_DETECTION_CONFIDENCE", "0.5"))
    POSE_MIN_TRACKING_CONFIDENCE = float(os.getenv("POSE_MIN_TRACKING_CONFIDENCE", "0.5"))
    VIDEO_SAMPLE_RATE = int(os.getenv("VIDEO_SAMPLE_RATE", "2"))  # process every Nth frame

    # Scoring thresholds
    POSTURE_DEVIATION_THRESHOLD = float(os.getenv("POSTURE_DEVIATION_THRESHOLD", "15.0"))
    ROM_RESTRICTED_THRESHOLD = float(os.getenv("ROM_RESTRICTED_THRESHOLD", "0.6"))
