"""Session persistence and retrieval service."""

import json

from backend.database import db
from backend.models.session import AnalysisSession, FrameMetric


class SessionService:
    """CRUD operations for analysis sessions."""

    def create_from_analysis(
        self,
        analysis_result: dict,
        source_type: str,
        source_filename: str | None = None,
    ) -> AnalysisSession:
        """Persist analysis results to database."""
        session = AnalysisSession(
            source_type=source_type,
            source_filename=source_filename,
            duration_seconds=analysis_result.get("duration_seconds"),
            frame_count=analysis_result.get("frame_count", 0),
            activity_label=analysis_result.get("activity_label"),
            repetition_count=analysis_result.get("repetition_count", 0),
            movement_speed_avg=analysis_result.get("movement_speed_avg"),
            posture_score=analysis_result.get("posture_score"),
            motor_function_score=analysis_result.get("motor_function_score"),
            overlay_video_path=analysis_result.get("overlay_video_path"),
            status="completed",
        )
        session.set_json_field("joint_angles_avg", analysis_result.get("joint_angles_avg") or {})
        session.set_json_field("joint_angles_max", analysis_result.get("joint_angles_max") or {})
        session.set_json_field("joint_angles_min", analysis_result.get("joint_angles_min") or {})
        session.set_json_field("range_of_motion", analysis_result.get("range_of_motion") or {})
        session.set_json_field("posture_deviations", analysis_result.get("posture_deviations") or [])
        session.set_json_field("summary", analysis_result.get("summary") or {})

        db.session.add(session)
        db.session.flush()

        for fm in analysis_result.get("frame_metrics", []):
            angles = fm.get("joint_angles", {})
            frame = FrameMetric(
                session_id=session.id,
                frame_index=fm.get("frame_index", 0),
                timestamp_seconds=fm.get("timestamp_seconds"),
                shoulder_angle_left=angles.get("shoulder_left"),
                shoulder_angle_right=angles.get("shoulder_right"),
                elbow_angle_left=angles.get("elbow_left"),
                elbow_angle_right=angles.get("elbow_right"),
                hip_angle_left=angles.get("hip_left"),
                hip_angle_right=angles.get("hip_right"),
                knee_angle_left=angles.get("knee_left"),
                knee_angle_right=angles.get("knee_right"),
                ankle_angle_left=angles.get("ankle_left"),
                ankle_angle_right=angles.get("ankle_right"),
                movement_speed=fm.get("movement_speed"),
                posture_score=fm.get("posture_score"),
                landmarks=json.dumps(fm.get("landmarks")) if fm.get("landmarks") else None,
            )
            db.session.add(frame)

        db.session.commit()
        return session

    def create_from_frame(self, frame_result: dict, source_filename: str | None = None) -> AnalysisSession:
        """Persist single-frame analysis as a session."""
        if not frame_result.get("pose_detected"):
            session = AnalysisSession(
                source_type="frame",
                source_filename=source_filename,
                frame_count=0,
                status="failed",
                error_message=frame_result.get("error", "No pose detected"),
            )
            db.session.add(session)
            db.session.commit()
            return session

        analysis = {
            "duration_seconds": 0,
            "frame_count": 1,
            "activity_label": "standing",
            "joint_angles_avg": frame_result.get("joint_angles", {}),
            "joint_angles_max": frame_result.get("joint_angles", {}),
            "joint_angles_min": frame_result.get("joint_angles", {}),
            "range_of_motion": {k: 0 for k in frame_result.get("joint_angles", {})},
            "repetition_count": frame_result.get("repetition_count", 0),
            "movement_speed_avg": frame_result.get("movement_speed", 0),
            "posture_score": frame_result.get("posture_score"),
            "motor_function_score": frame_result.get("posture_score"),
            "posture_deviations": frame_result.get("posture_deviations", []),
            "summary": {
                "motor_function_score": frame_result.get("posture_score"),
                "activity_detected": "standing",
                "status": "single_frame",
            },
            "frame_metrics": [frame_result],
        }
        return self.create_from_analysis(analysis, "frame", source_filename)

    def get_by_id(self, session_id: int) -> AnalysisSession | None:
        return AnalysisSession.query.get(session_id)

    def get_history(self, limit: int = 50, offset: int = 0) -> list[AnalysisSession]:
        return (
            AnalysisSession.query
            .order_by(AnalysisSession.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_sessions(self) -> int:
        return AnalysisSession.query.count()
