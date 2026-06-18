"""SQLAlchemy models for analysis sessions and frame-level metrics."""

import json
from datetime import datetime, timezone

from backend.database import db


class AnalysisSession(db.Model):
    """Stores a complete motor function analysis session."""

    __tablename__ = "analysis_sessions"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source_type = db.Column(db.String(20), nullable=False)  # video | frame | live
    source_filename = db.Column(db.String(255), nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)
    frame_count = db.Column(db.Integer, default=0)
    activity_label = db.Column(db.String(50), nullable=True)

    # Aggregate metrics (JSON for flexibility)
    joint_angles_avg = db.Column(db.Text, nullable=True)
    joint_angles_max = db.Column(db.Text, nullable=True)
    joint_angles_min = db.Column(db.Text, nullable=True)
    range_of_motion = db.Column(db.Text, nullable=True)
    repetition_count = db.Column(db.Integer, default=0)
    movement_speed_avg = db.Column(db.Float, nullable=True)
    posture_score = db.Column(db.Float, nullable=True)
    motor_function_score = db.Column(db.Float, nullable=True)
    posture_deviations = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    overlay_video_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default="completed")  # processing | completed | failed
    error_message = db.Column(db.Text, nullable=True)

    frame_metrics = db.relationship(
        "FrameMetric", backref="session", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_json_field(self, field_name: str, data: dict | list):
        setattr(self, field_name, json.dumps(data))

    def get_json_field(self, field_name: str):
        raw = getattr(self, field_name)
        if raw is None:
            return None
        return json.loads(raw)

    def to_dict(self, include_frames: bool = False) -> dict:
        """Serialize session to API response dict."""
        result = {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "source_type": self.source_type,
            "source_filename": self.source_filename,
            "duration_seconds": self.duration_seconds,
            "frame_count": self.frame_count,
            "activity_label": self.activity_label,
            "joint_angles_avg": self.get_json_field("joint_angles_avg"),
            "joint_angles_max": self.get_json_field("joint_angles_max"),
            "joint_angles_min": self.get_json_field("joint_angles_min"),
            "range_of_motion": self.get_json_field("range_of_motion"),
            "repetition_count": self.repetition_count,
            "movement_speed_avg": self.movement_speed_avg,
            "posture_score": self.posture_score,
            "motor_function_score": self.motor_function_score,
            "posture_deviations": self.get_json_field("posture_deviations"),
            "summary": self.get_json_field("summary"),
            "overlay_video_path": self.overlay_video_path,
            "status": self.status,
            "error_message": self.error_message,
        }
        if include_frames:
            result["frame_metrics"] = [f.to_dict() for f in self.frame_metrics.order_by(FrameMetric.frame_index)]
        return result

    def to_report_dict(self) -> dict:
        """Extended report format with recommendations."""
        base = self.to_dict(include_frames=True)
        base["report"] = {
            "overall_assessment": self._assessment_label(),
            "recommendations": self._generate_recommendations(),
        }
        return base

    def _assessment_label(self) -> str:
        score = self.motor_function_score or 0
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Good"
        if score >= 50:
            return "Fair"
        return "Needs Attention"

    def _generate_recommendations(self) -> list[str]:
        recs = []
        deviations = self.get_json_field("posture_deviations") or []
        rom = self.get_json_field("range_of_motion") or {}

        if deviations:
            recs.append(f"Address posture deviations: {', '.join(deviations[:3])}")
        for joint, value in rom.items():
            if isinstance(value, (int, float)) and value < 45:
                recs.append(f"Consider exercises to improve {joint.replace('_', ' ')} range of motion")
        if (self.posture_score or 100) < 70:
            recs.append("Focus on core strengthening and posture alignment exercises")
        if not recs:
            recs.append("Maintain current activity level with regular monitoring")
        return recs


class FrameMetric(db.Model):
    """Per-frame metrics captured during analysis."""

    __tablename__ = "frame_metrics"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("analysis_sessions.id"), nullable=False)
    frame_index = db.Column(db.Integer, nullable=False)
    timestamp_seconds = db.Column(db.Float, nullable=True)

    shoulder_angle_left = db.Column(db.Float, nullable=True)
    shoulder_angle_right = db.Column(db.Float, nullable=True)
    elbow_angle_left = db.Column(db.Float, nullable=True)
    elbow_angle_right = db.Column(db.Float, nullable=True)
    hip_angle_left = db.Column(db.Float, nullable=True)
    hip_angle_right = db.Column(db.Float, nullable=True)
    knee_angle_left = db.Column(db.Float, nullable=True)
    knee_angle_right = db.Column(db.Float, nullable=True)
    ankle_angle_left = db.Column(db.Float, nullable=True)
    ankle_angle_right = db.Column(db.Float, nullable=True)
    movement_speed = db.Column(db.Float, nullable=True)
    posture_score = db.Column(db.Float, nullable=True)
    landmarks = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        landmarks = None
        if self.landmarks:
            landmarks = json.loads(self.landmarks)
        return {
            "frame_index": self.frame_index,
            "timestamp_seconds": self.timestamp_seconds,
            "joint_angles": {
                "shoulder_left": self.shoulder_angle_left,
                "shoulder_right": self.shoulder_angle_right,
                "elbow_left": self.elbow_angle_left,
                "elbow_right": self.elbow_angle_right,
                "hip_left": self.hip_angle_left,
                "hip_right": self.hip_angle_right,
                "knee_left": self.knee_angle_left,
                "knee_right": self.knee_angle_right,
                "ankle_left": self.ankle_angle_left,
                "ankle_right": self.ankle_angle_right,
            },
            "movement_speed": self.movement_speed,
            "posture_score": self.posture_score,
            "landmarks": landmarks,
        }
