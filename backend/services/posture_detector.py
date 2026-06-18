"""Posture deviation detection and posture scoring."""

from backend.utils.constants import (
    LEFT_ANKLE,
    LEFT_HIP,
    LEFT_KNEE,
    LEFT_SHOULDER,
    NEUTRAL_ANGLES,
    RIGHT_ANKLE,
    RIGHT_HIP,
    RIGHT_KNEE,
    RIGHT_SHOULDER,
)


class PostureDetector:
    """Detects abnormal posture and computes posture alignment score."""

    def __init__(self, deviation_threshold: float = 15.0):
        self.deviation_threshold = deviation_threshold
        self._deviations_seen: set[str] = set()

    def analyze(self, landmarks, joint_angles: dict, image_width: int, image_height: int) -> dict:
        """Return posture score (0-100) and list of detected deviations."""
        deviations = []
        score_components = []

        # Shoulder level check
        ls_y = landmarks[LEFT_SHOULDER].y * image_height
        rs_y = landmarks[RIGHT_SHOULDER].y * image_height
        shoulder_tilt = abs(ls_y - rs_y)
        if shoulder_tilt > image_height * 0.03:
            deviations.append("Uneven shoulders")
            score_components.append(max(0, 100 - shoulder_tilt / image_height * 500))
        else:
            score_components.append(100)

        # Forward head / spine alignment via shoulder-hip vertical offset
        hip_mid_x = (landmarks[LEFT_HIP].x + landmarks[RIGHT_HIP].x) / 2 * image_width
        shoulder_mid_x = (landmarks[LEFT_SHOULDER].x + landmarks[RIGHT_SHOULDER].x) / 2 * image_width
        lateral_offset = abs(hip_mid_x - shoulder_mid_x)
        if lateral_offset > image_width * 0.05:
            deviations.append("Lateral spine misalignment")
            score_components.append(max(0, 100 - lateral_offset / image_width * 300))
        else:
            score_components.append(95)

        # Knee hyperextension or excessive flexion
        for side, key in [("left", "knee_left"), ("right", "knee_right")]:
            angle = joint_angles.get(key)
            if angle is not None:
                if angle > 185:
                    deviations.append(f"{side.capitalize()} knee hyperextension")
                    score_components.append(70)
                elif angle < 160 and angle > 90:
                    deviations.append(f"{side.capitalize()} knee excessive flexion while standing")
                    score_components.append(75)
                else:
                    score_components.append(90)

        # Hip angle asymmetry
        hip_l = joint_angles.get("hip_left")
        hip_r = joint_angles.get("hip_right")
        if hip_l is not None and hip_r is not None:
            asymmetry = abs(hip_l - hip_r)
            if asymmetry > self.deviation_threshold:
                deviations.append("Hip angle asymmetry")
                score_components.append(max(0, 100 - asymmetry * 2))
            else:
                score_components.append(92)

        # Joint angle deviation from neutral reference
        for joint_type, neutral in NEUTRAL_ANGLES.items():
            for key in joint_angles:
                if key.startswith(joint_type):
                    dev = abs(joint_angles[key] - neutral)
                    if dev > self.deviation_threshold * 2:
                        label = f"{key.replace('_', ' ')} deviation"
                        if label not in deviations:
                            deviations.append(label)

        posture_score = round(sum(score_components) / max(len(score_components), 1), 2)
        posture_score = min(100, max(0, posture_score))

        for d in deviations:
            self._deviations_seen.add(d)

        return {
            "posture_score": posture_score,
            "posture_deviations": deviations,
        }

    def get_session_deviations(self) -> list[str]:
        return sorted(self._deviations_seen)

    def reset(self):
        self._deviations_seen = set()
