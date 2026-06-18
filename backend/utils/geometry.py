"""Utility helpers for geometry, serialization, and file handling."""

import base64
import json
import os
import uuid
from pathlib import Path

import cv2
import numpy as np


def calculate_angle(point_a: tuple, point_b: tuple, point_c: tuple) -> float:
    """
    Calculate the angle at point_b formed by segments ba and bc.
    Returns angle in degrees (0-180).
    """
    a = np.array(point_a[:2], dtype=np.float64)
    b = np.array(point_b[:2], dtype=np.float64)
    c = np.array(point_c[:2], dtype=np.float64)

    ba = a - b
    bc = c - b

    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def calculate_distance(point_a: tuple, point_b: tuple) -> float:
    """Euclidean distance between two 2D points."""
    return float(np.linalg.norm(np.array(point_a[:2]) - np.array(point_b[:2])))


def landmarks_to_dict(landmarks, image_width: int, image_height: int) -> list[dict]:
    """Convert MediaPipe landmarks to normalized pixel coordinates."""
    result = []
    for idx, lm in enumerate(landmarks):
        result.append({
            "index": idx,
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": getattr(lm, "visibility", 1.0),
            "pixel_x": int(lm.x * image_width),
            "pixel_y": int(lm.y * image_height),
        })
    return result


def decode_base64_image(data: str) -> np.ndarray:
    """Decode base64 image string to OpenCV BGR array."""
    if "," in data:
        data = data.split(",", 1)[1]
    img_bytes = base64.b64decode(data)
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def encode_image_base64(image: np.ndarray, fmt: str = ".jpg") -> str:
    """Encode OpenCV image to base64 data URI."""
    _, buffer = cv2.imencode(fmt, image)
    b64 = base64.b64encode(buffer).decode("utf-8")
    mime = "image/jpeg" if fmt == ".jpg" else "image/png"
    return f"data:{mime};base64,{b64}"


def save_upload(file_storage, upload_dir: Path) -> Path:
    """Save uploaded file with unique name, return path."""
    ext = Path(file_storage.filename or "upload.bin").suffix or ".bin"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = upload_dir / filename
    file_storage.save(str(path))
    return path


def aggregate_metrics(frame_metrics: list[dict]) -> dict:
    """Compute min/max/avg across frame-level joint angles."""
    if not frame_metrics:
        return {"avg": {}, "min": {}, "max": {}, "rom": {}}

    joint_keys = [
        "shoulder_left", "shoulder_right",
        "elbow_left", "elbow_right",
        "hip_left", "hip_right",
        "knee_left", "knee_right",
        "ankle_left", "ankle_right",
    ]

    collected = {k: [] for k in joint_keys}
    speeds = []
    posture_scores = []

    for fm in frame_metrics:
        angles = fm.get("joint_angles", {})
        for k in joint_keys:
            v = angles.get(k)
            if v is not None:
                collected[k].append(v)
        if fm.get("movement_speed") is not None:
            speeds.append(fm["movement_speed"])
        if fm.get("posture_score") is not None:
            posture_scores.append(fm["posture_score"])

    avg = {k: round(float(np.mean(v)), 2) if v else None for k, v in collected.items()}
    min_v = {k: round(float(np.min(v)), 2) if v else None for k, v in collected.items()}
    max_v = {k: round(float(np.max(v)), 2) if v else None for k, v in collected.items()}
    rom = {k: round(float(np.max(v) - np.min(v)), 2) if v else None for k, v in collected.items()}

    return {
        "avg": avg,
        "min": min_v,
        "max": max_v,
        "rom": rom,
        "movement_speed_avg": round(float(np.mean(speeds)), 4) if speeds else 0.0,
        "posture_score_avg": round(float(np.mean(posture_scores)), 2) if posture_scores else None,
    }


def safe_json_dumps(obj) -> str:
    return json.dumps(obj, default=str)
