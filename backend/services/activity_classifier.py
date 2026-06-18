"""Rule-based activity classification from motion patterns."""

from backend.utils.constants import ACTIVITY_PATTERNS


class ActivityClassifier:
    """Classifies activity type from aggregated session metrics."""

    def classify(self, rom: dict, repetition_count: int, avg_speed: float) -> str:
        """
        Classify activity based on range of motion and movement characteristics.
        Returns one of: standing, walking, squatting, arm_raise, general_exercise
        """
        knee_rom = max(
            rom.get("knee_left") or 0,
            rom.get("knee_right") or 0,
        )
        hip_rom = max(
            rom.get("hip_left") or 0,
            rom.get("hip_right") or 0,
        )
        shoulder_rom = max(
            rom.get("shoulder_left") or 0,
            rom.get("shoulder_right") or 0,
        )

        if repetition_count >= 3 and knee_rom >= 60:
            return "squatting"
        if shoulder_rom >= 50 and knee_rom < 30:
            return "arm_raise"
        if 25 <= knee_rom <= 70 and avg_speed > 5:
            return "walking"
        if knee_rom < 20 and hip_rom < 25 and avg_speed < 2:
            return "standing"
        if repetition_count >= 2:
            return "general_exercise"
        return "general_exercise"

    def confidence(self, activity: str, rom: dict) -> float:
        """Heuristic confidence score for classification."""
        return 0.75 if activity != "general_exercise" else 0.55
