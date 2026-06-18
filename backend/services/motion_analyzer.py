"""Movement speed, repetition counting, and range-of-motion tracking."""

from backend.utils.constants import LEFT_HIP, LEFT_WRIST, RIGHT_HIP, RIGHT_WRIST
from backend.utils.geometry import calculate_distance


class MotionAnalyzer:
    """Tracks movement over time for speed and repetition detection."""

    def __init__(self, repetition_joint: str = "knee_left"):
        self.repetition_joint = repetition_joint
        self._prev_landmarks = None
        self._prev_timestamp = None
        self._prev_joint_angle = None
        self._rep_phase = "down"  # down | up
        self.repetition_count = 0
        self._angle_history: list[float] = []

    def analyze_frame(
        self,
        landmarks,
        joint_angles: dict,
        image_width: int,
        image_height: int,
        timestamp: float,
    ) -> dict:
        """Compute per-frame movement speed and update repetition count."""
        speed = 0.0

        if self._prev_landmarks is not None and self._prev_timestamp is not None:
            dt = max(timestamp - self._prev_timestamp, 1e-6)
            # Use hip center displacement as proxy for body movement speed
            prev_hip = (
                (self._prev_landmarks[LEFT_HIP].x + self._prev_landmarks[RIGHT_HIP].x) / 2 * image_width,
                (self._prev_landmarks[LEFT_HIP].y + self._prev_landmarks[RIGHT_HIP].y) / 2 * image_height,
            )
            curr_hip = (
                (landmarks[LEFT_HIP].x + landmarks[RIGHT_HIP].x) / 2 * image_width,
                (landmarks[LEFT_HIP].y + landmarks[RIGHT_HIP].y) / 2 * image_height,
            )
            displacement = calculate_distance(prev_hip, curr_hip)
            speed = round(displacement / dt, 4)

        # Repetition counting via knee angle peaks (squat/curl pattern)
        joint_angle = joint_angles.get(self.repetition_joint)
        if joint_angle is not None:
            self._angle_history.append(joint_angle)
            self._update_repetitions(joint_angle)

        self._prev_landmarks = landmarks
        self._prev_timestamp = timestamp

        return {
            "movement_speed": speed,
            "repetition_count": self.repetition_count,
        }

    def _update_repetitions(self, angle: float):
        """Count repetitions using peak-valley detection on knee angle."""
        if self._prev_joint_angle is None:
            self._prev_joint_angle = angle
            return

        # Squat pattern: angle decreases (down) then increases (up) past threshold
        going_down = angle < self._prev_joint_angle - 5
        going_up = angle > self._prev_joint_angle + 5

        if self._rep_phase == "up" and going_down and angle < 120:
            self._rep_phase = "down"
        elif self._rep_phase == "down" and going_up and angle > 150:
            self._rep_phase = "up"
            self.repetition_count += 1

        self._prev_joint_angle = angle

    def get_range_of_motion(self) -> dict:
        """Return ROM per tracked joint from angle history."""
        if len(self._angle_history) < 2:
            return {self.repetition_joint: 0.0}
        return {self.repetition_joint: round(max(self._angle_history) - min(self._angle_history), 2)}

    def reset(self):
        self._prev_landmarks = None
        self._prev_timestamp = None
        self._prev_joint_angle = None
        self._rep_phase = "down"
        self.repetition_count = 0
        self._angle_history = []
