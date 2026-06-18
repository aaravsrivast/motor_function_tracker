"""Motor function composite scoring."""

class ScoringService:
    """
    Generates motor function score (0-100) from posture, ROM,
    symmetry, and movement quality metrics.
    """

    def compute_motor_function_score(
        self,
        posture_score: float,
        rom: dict,
        joint_angles_avg: dict,
        repetition_count: int,
        deviations: list[str],
    ) -> float:
        weights = {
            "posture": 0.35,
            "rom": 0.25,
            "symmetry": 0.25,
            "movement": 0.15,
        }

        posture_component = posture_score or 70

        # ROM component: average normalized ROM across major joints
        rom_values = [v for v in rom.values() if v is not None and v > 0]
        if rom_values:
            avg_rom = sum(rom_values) / len(rom_values)
            rom_component = min(100, avg_rom * 1.5)  # 67° avg ROM ≈ 100
        else:
            rom_component = 50

        # Symmetry: compare left/right joint pairs
        pairs = [
            ("shoulder_left", "shoulder_right"),
            ("elbow_left", "elbow_right"),
            ("hip_left", "hip_right"),
            ("knee_left", "knee_right"),
            ("ankle_left", "ankle_right"),
        ]
        sym_scores = []
        for left, right in pairs:
            lv = joint_angles_avg.get(left)
            rv = joint_angles_avg.get(right)
            if lv is not None and rv is not None:
                diff = abs(lv - rv)
                sym_scores.append(max(0, 100 - diff * 3))
        symmetry_component = sum(sym_scores) / len(sym_scores) if sym_scores else 75

        # Movement quality: repetitions indicate controlled movement
        movement_component = min(100, 50 + repetition_count * 10)

        # Penalty for deviations
        deviation_penalty = min(30, len(deviations) * 5)

        raw_score = (
            posture_component * weights["posture"]
            + rom_component * weights["rom"]
            + symmetry_component * weights["symmetry"]
            + movement_component * weights["movement"]
        )
        final = max(0, min(100, round(raw_score - deviation_penalty, 2)))
        return final

    def build_summary(
        self,
        motor_function_score: float,
        activity: str,
        repetition_count: int,
        posture_score: float,
        deviations: list[str],
    ) -> dict:
        return {
            "motor_function_score": motor_function_score,
            "activity_detected": activity,
            "total_repetitions": repetition_count,
            "posture_score": posture_score,
            "deviation_count": len(deviations),
            "status": "healthy" if motor_function_score >= 70 else "monitor",
        }
