"""Video and frame processing pipeline orchestration."""

import os
from pathlib import Path

import cv2
import numpy as np

from backend.services.activity_classifier import ActivityClassifier
from backend.services.angle_calculator import calculate_joint_angles
from backend.services.motion_analyzer import MotionAnalyzer
from backend.services.pose_estimator import create_pose_estimator
from backend.services.posture_detector import PostureDetector
from backend.services.scoring_service import ScoringService
from backend.utils.geometry import aggregate_metrics, encode_image_base64, landmarks_to_dict


class VideoProcessor:
    """Processes video files and individual frames through the CV pipeline."""

    def __init__(self, config: dict):
        self.config = config
        self.pose_estimator = create_pose_estimator(
            model_name=config.get("POSE_MODEL", "mediapipe"),
            min_detection_confidence=config.get("POSE_MIN_DETECTION_CONFIDENCE", 0.5),
            min_tracking_confidence=config.get("POSE_MIN_TRACKING_CONFIDENCE", 0.5),
        )
        self.motion_analyzer = MotionAnalyzer()
        self.posture_detector = PostureDetector(
            deviation_threshold=config.get("POSTURE_DEVIATION_THRESHOLD", 15.0)
        )
        self.activity_classifier = ActivityClassifier()
        self.scoring_service = ScoringService()
        self.sample_rate = config.get("VIDEO_SAMPLE_RATE", 2)

    def process_frame(
        self,
        image: np.ndarray,
        frame_index: int = 0,
        timestamp: float = 0.0,
        include_overlay: bool = True,
        include_landmarks: bool = True,
    ) -> dict:
        """Analyze a single frame and return metrics + optional overlay."""
        h, w = image.shape[:2]
        landmarks, _ = self.pose_estimator.detect(image)

        if landmarks is None:
            return {
                "frame_index": frame_index,
                "timestamp_seconds": timestamp,
                "pose_detected": False,
                "error": "No pose detected in frame",
            }

        joint_angles = calculate_joint_angles(landmarks, w, h)
        motion = self.motion_analyzer.analyze_frame(landmarks, joint_angles, w, h, timestamp)
        posture = self.posture_detector.analyze(landmarks, joint_angles, w, h)

        result = {
            "frame_index": frame_index,
            "timestamp_seconds": timestamp,
            "pose_detected": True,
            "joint_angles": joint_angles,
            "movement_speed": motion["movement_speed"],
            "repetition_count": motion["repetition_count"],
            "posture_score": posture["posture_score"],
            "posture_deviations": posture["posture_deviations"],
        }

        if include_landmarks:
            result["landmarks"] = landmarks_to_dict(landmarks, w, h)

        if include_overlay:
            overlay = self.pose_estimator.draw_skeleton(image, landmarks)
            self._draw_metrics_overlay(overlay, joint_angles, posture["posture_score"])
            result["overlay_image"] = encode_image_base64(overlay)

        return result

    def process_video(
        self,
        video_path: str | Path,
        save_overlay: bool = True,
        upload_dir: Path | None = None,
    ) -> dict:
        """Process entire video file and return session-level results."""
        video_path = str(video_path)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        self.motion_analyzer.reset()
        self.posture_detector.reset()

        frame_metrics = []
        frame_idx = 0
        processed = 0
        overlay_writer = None
        overlay_path = None

        if save_overlay and upload_dir:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            overlay_path = upload_dir / f"overlay_{os.path.basename(video_path)}"
            ret, sample = cap.read()
            if ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                h, w = sample.shape[:2]
                overlay_writer = cv2.VideoWriter(str(overlay_path), fourcc, fps, (w, h))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self.sample_rate != 0:
                frame_idx += 1
                if overlay_writer:
                    overlay_writer.write(frame)
                continue

            timestamp = frame_idx / fps
            fm = self.process_frame(
                frame,
                frame_index=processed,
                timestamp=timestamp,
                include_overlay=False,
                include_landmarks=True,
            )

            if fm.get("pose_detected"):
                frame_metrics.append(fm)

            if overlay_writer and fm.get("pose_detected"):
                annotated = self.pose_estimator.draw_skeleton(frame, self.pose_estimator.detect(frame)[0])
                self._draw_metrics_overlay(annotated, fm["joint_angles"], fm["posture_score"])
                overlay_writer.write(annotated)
            elif overlay_writer:
                overlay_writer.write(frame)

            processed += 1
            frame_idx += 1

        cap.release()
        if overlay_writer:
            overlay_writer.release()

        return self._build_session_result(
            frame_metrics=frame_metrics,
            duration_seconds=duration,
            frame_count=processed,
            overlay_path=str(overlay_path) if overlay_path else None,
        )

    def _build_session_result(
        self,
        frame_metrics: list[dict],
        duration_seconds: float,
        frame_count: int,
        overlay_path: str | None,
    ) -> dict:
        """Aggregate frame metrics into session-level output."""
        aggregated = aggregate_metrics(frame_metrics)
        deviations = self.posture_detector.get_session_deviations()
        rom = aggregated["rom"]

        activity = self.activity_classifier.classify(
            rom=rom,
            repetition_count=self.motion_analyzer.repetition_count,
            avg_speed=aggregated["movement_speed_avg"],
        )

        motor_score = self.scoring_service.compute_motor_function_score(
            posture_score=aggregated["posture_score_avg"] or 70,
            rom=rom,
            joint_angles_avg=aggregated["avg"],
            repetition_count=self.motion_analyzer.repetition_count,
            deviations=deviations,
        )

        summary = self.scoring_service.build_summary(
            motor_function_score=motor_score,
            activity=activity,
            repetition_count=self.motion_analyzer.repetition_count,
            posture_score=aggregated["posture_score_avg"] or 0,
            deviations=deviations,
        )

        return {
            "duration_seconds": round(duration_seconds, 2),
            "frame_count": frame_count,
            "activity_label": activity,
            "joint_angles_avg": aggregated["avg"],
            "joint_angles_max": aggregated["max"],
            "joint_angles_min": aggregated["min"],
            "range_of_motion": rom,
            "repetition_count": self.motion_analyzer.repetition_count,
            "movement_speed_avg": aggregated["movement_speed_avg"],
            "posture_score": aggregated["posture_score_avg"],
            "motor_function_score": motor_score,
            "posture_deviations": deviations,
            "summary": summary,
            "frame_metrics": frame_metrics,
            "overlay_video_path": overlay_path,
        }

    def _draw_metrics_overlay(self, image: np.ndarray, angles: dict, posture_score: float):
        """Draw key metrics on frame for visualization."""
        y = 30
        cv2.putText(image, f"Posture: {posture_score:.0f}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 25
        for key in ["knee_left", "elbow_left", "hip_left"]:
            if key in angles:
                cv2.putText(
                    image,
                    f"{key}: {angles[key]:.0f}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 255, 200),
                    1,
                )
                y += 20

    def close(self):
        self.pose_estimator.close()
