"""Pose estimation using MediaPipe (with MoveNet/YOLO stubs for extension)."""

from abc import ABC, abstractmethod

import cv2
import mediapipe as mp
import numpy as np

from backend.utils.constants import POSE_CONNECTIONS


class BasePoseEstimator(ABC):
    """Abstract pose estimator interface."""

    @abstractmethod
    def detect(self, image: np.ndarray) -> tuple[list | None, object | None]:
        """Return (landmarks_list, raw_results) or (None, None) if no pose detected."""
        pass

    @abstractmethod
    def draw_skeleton(self, image: np.ndarray, landmarks) -> np.ndarray:
        pass

    @abstractmethod
    def close(self):
        pass


class MediaPipePoseEstimator(BasePoseEstimator):
    """MediaPipe Pose landmark detector."""

    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        self._mp_pose = mp.solutions.pose
        self._pose = self._mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._mp_draw = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles

    def detect(self, image: np.ndarray) -> tuple[list | None, object | None]:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self._pose.process(rgb)
        if not results.pose_landmarks:
            return None, None
        return results.pose_landmarks.landmark, results

    def draw_skeleton(self, image: np.ndarray, landmarks) -> np.ndarray:
        annotated = image.copy()
        if landmarks is None:
            return annotated

        h, w = annotated.shape[:2]

        # Draw connections
        for start_idx, end_idx in POSE_CONNECTIONS:
            if start_idx >= len(landmarks) or end_idx >= len(landmarks):
                continue
            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]
            if getattr(p1, "visibility", 1) < 0.5 or getattr(p2, "visibility", 1) < 0.5:
                continue
            cv2.line(
                annotated,
                (int(p1.x * w), int(p1.y * h)),
                (int(p2.x * w), int(p2.y * h)),
                (0, 255, 128),
                2,
            )

        # Draw joints
        for lm in landmarks:
            if getattr(lm, "visibility", 1) < 0.5:
                continue
            cv2.circle(annotated, (int(lm.x * w), int(lm.y * h)), 4, (0, 200, 255), -1)

        return annotated

    def close(self):
        self._pose.close()


class MoveNetPoseEstimator(BasePoseEstimator):
    """
    MoveNet stub — swap in tensorflow-hub MoveNet for production.
    Falls back to MediaPipe internally for demo compatibility.
    """

    def __init__(self, **kwargs):
        self._fallback = MediaPipePoseEstimator(**kwargs)

    def detect(self, image: np.ndarray):
        return self._fallback.detect(image)

    def draw_skeleton(self, image: np.ndarray, landmarks):
        return self._fallback.draw_skeleton(image, landmarks)

    def close(self):
        self._fallback.close()


def create_pose_estimator(model_name: str = "mediapipe", **kwargs) -> BasePoseEstimator:
    """Factory for pose estimation backends."""
    model_name = (model_name or "mediapipe").lower()
    if model_name == "mediapipe":
        return MediaPipePoseEstimator(**kwargs)
    if model_name in ("movenet", "yolo"):
        return MoveNetPoseEstimator(**kwargs)
    return MediaPipePoseEstimator(**kwargs)
