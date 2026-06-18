"""Joint angle calculation from pose landmarks."""

from backend.utils.constants import (
    LEFT_ANKLE,
    LEFT_ELBOW,
    LEFT_FOOT_INDEX,
    LEFT_HEEL,
    LEFT_HIP,
    LEFT_KNEE,
    LEFT_SHOULDER,
    LEFT_WRIST,
    RIGHT_ANKLE,
    RIGHT_ELBOW,
    RIGHT_FOOT_INDEX,
    RIGHT_HEEL,
    RIGHT_HIP,
    RIGHT_KNEE,
    RIGHT_SHOULDER,
    RIGHT_WRIST,
)
from backend.utils.geometry import calculate_angle


def _lm_point(landmarks, idx: int, width: int, height: int) -> tuple:
    """Extract pixel coordinates from landmark."""
    lm = landmarks[idx]
    return (lm.x * width, lm.y * height)


def _visible(landmarks, idx: int, threshold: float = 0.5) -> bool:
    lm = landmarks[idx]
    return getattr(lm, "visibility", 1.0) >= threshold


def calculate_joint_angles(landmarks, image_width: int, image_height: int) -> dict:
    """
    Calculate all joint angles from pose landmarks.
    Angles are computed at the middle joint of each triplet.
    """
    angles = {}

    # Shoulder: hip-shoulder-elbow
    if _visible(landmarks, LEFT_HIP) and _visible(landmarks, LEFT_SHOULDER) and _visible(landmarks, LEFT_ELBOW):
        angles["shoulder_left"] = round(
            calculate_angle(
                _lm_point(landmarks, LEFT_HIP, image_width, image_height),
                _lm_point(landmarks, LEFT_SHOULDER, image_width, image_height),
                _lm_point(landmarks, LEFT_ELBOW, image_width, image_height),
            ),
            2,
        )
    if _visible(landmarks, RIGHT_HIP) and _visible(landmarks, RIGHT_SHOULDER) and _visible(landmarks, RIGHT_ELBOW):
        angles["shoulder_right"] = round(
            calculate_angle(
                _lm_point(landmarks, RIGHT_HIP, image_width, image_height),
                _lm_point(landmarks, RIGHT_SHOULDER, image_width, image_height),
                _lm_point(landmarks, RIGHT_ELBOW, image_width, image_height),
            ),
            2,
        )

    # Elbow: shoulder-elbow-wrist
    if _visible(landmarks, LEFT_SHOULDER) and _visible(landmarks, LEFT_ELBOW) and _visible(landmarks, LEFT_WRIST):
        angles["elbow_left"] = round(
            calculate_angle(
                _lm_point(landmarks, LEFT_SHOULDER, image_width, image_height),
                _lm_point(landmarks, LEFT_ELBOW, image_width, image_height),
                _lm_point(landmarks, LEFT_WRIST, image_width, image_height),
            ),
            2,
        )
    if _visible(landmarks, RIGHT_SHOULDER) and _visible(landmarks, RIGHT_ELBOW) and _visible(landmarks, RIGHT_WRIST):
        angles["elbow_right"] = round(
            calculate_angle(
                _lm_point(landmarks, RIGHT_SHOULDER, image_width, image_height),
                _lm_point(landmarks, RIGHT_ELBOW, image_width, image_height),
                _lm_point(landmarks, RIGHT_WRIST, image_width, image_height),
            ),
            2,
        )

    # Hip: shoulder-hip-knee
    if _visible(landmarks, LEFT_SHOULDER) and _visible(landmarks, LEFT_HIP) and _visible(landmarks, LEFT_KNEE):
        angles["hip_left"] = round(
            calculate_angle(
                _lm_point(landmarks, LEFT_SHOULDER, image_width, image_height),
                _lm_point(landmarks, LEFT_HIP, image_width, image_height),
                _lm_point(landmarks, LEFT_KNEE, image_width, image_height),
            ),
            2,
        )
    if _visible(landmarks, RIGHT_SHOULDER) and _visible(landmarks, RIGHT_HIP) and _visible(landmarks, RIGHT_KNEE):
        angles["hip_right"] = round(
            calculate_angle(
                _lm_point(landmarks, RIGHT_SHOULDER, image_width, image_height),
                _lm_point(landmarks, RIGHT_HIP, image_width, image_height),
                _lm_point(landmarks, RIGHT_KNEE, image_width, image_height),
            ),
            2,
        )

    # Knee: hip-knee-ankle
    if _visible(landmarks, LEFT_HIP) and _visible(landmarks, LEFT_KNEE) and _visible(landmarks, LEFT_ANKLE):
        angles["knee_left"] = round(
            calculate_angle(
                _lm_point(landmarks, LEFT_HIP, image_width, image_height),
                _lm_point(landmarks, LEFT_KNEE, image_width, image_height),
                _lm_point(landmarks, LEFT_ANKLE, image_width, image_height),
            ),
            2,
        )
    if _visible(landmarks, RIGHT_HIP) and _visible(landmarks, RIGHT_KNEE) and _visible(landmarks, RIGHT_ANKLE):
        angles["knee_right"] = round(
            calculate_angle(
                _lm_point(landmarks, RIGHT_HIP, image_width, image_height),
                _lm_point(landmarks, RIGHT_KNEE, image_width, image_height),
                _lm_point(landmarks, RIGHT_ANKLE, image_width, image_height),
            ),
            2,
        )

    # Ankle: knee-ankle-foot_index
    if _visible(landmarks, LEFT_KNEE) and _visible(landmarks, LEFT_ANKLE) and _visible(landmarks, LEFT_FOOT_INDEX):
        angles["ankle_left"] = round(
            calculate_angle(
                _lm_point(landmarks, LEFT_KNEE, image_width, image_height),
                _lm_point(landmarks, LEFT_ANKLE, image_width, image_height),
                _lm_point(landmarks, LEFT_FOOT_INDEX, image_width, image_height),
            ),
            2,
        )
    if _visible(landmarks, RIGHT_KNEE) and _visible(landmarks, RIGHT_ANKLE) and _visible(landmarks, RIGHT_FOOT_INDEX):
        angles["ankle_right"] = round(
            calculate_angle(
                _lm_point(landmarks, RIGHT_KNEE, image_width, image_height),
                _lm_point(landmarks, RIGHT_ANKLE, image_width, image_height),
                _lm_point(landmarks, RIGHT_FOOT_INDEX, image_width, image_height),
            ),
            2,
        )

    return angles
