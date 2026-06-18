"""MediaPipe Pose landmark indices for reference."""

# MediaPipe Pose landmark indices
NOSE = 0
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28
LEFT_HEEL = 29
RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX = 32

# Skeleton connections for drawing
POSE_CONNECTIONS = [
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    (LEFT_SHOULDER, LEFT_ELBOW),
    (LEFT_ELBOW, LEFT_WRIST),
    (RIGHT_SHOULDER, RIGHT_ELBOW),
    (RIGHT_ELBOW, RIGHT_WRIST),
    (LEFT_SHOULDER, LEFT_HIP),
    (RIGHT_SHOULDER, RIGHT_HIP),
    (LEFT_HIP, RIGHT_HIP),
    (LEFT_HIP, LEFT_KNEE),
    (LEFT_KNEE, LEFT_ANKLE),
    (RIGHT_HIP, RIGHT_KNEE),
    (RIGHT_KNEE, RIGHT_ANKLE),
    (LEFT_ANKLE, LEFT_HEEL),
    (LEFT_HEEL, LEFT_FOOT_INDEX),
    (RIGHT_ANKLE, RIGHT_HEEL),
    (RIGHT_HEEL, RIGHT_FOOT_INDEX),
]

# Expected neutral posture reference angles (degrees)
NEUTRAL_ANGLES = {
    "shoulder": 90.0,
    "elbow": 170.0,
    "hip": 170.0,
    "knee": 175.0,
    "ankle": 90.0,
}

# Activity classification thresholds based on joint motion patterns
ACTIVITY_PATTERNS = {
    "standing": {"knee_rom_max": 20, "hip_rom_max": 25},
    "walking": {"knee_rom_min": 25, "knee_rom_max": 70},
    "squatting": {"knee_rom_min": 60, "hip_rom_min": 50},
    "arm_raise": {"shoulder_rom_min": 50, "knee_rom_max": 30},
    "general_exercise": {},
}
