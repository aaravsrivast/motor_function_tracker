# API Documentation — Motor Function Tracker

Base URL: `http://localhost:5000/api`

All responses use JSON. Successful responses include `"success": true`.

---

## Error Handling

| Status | Meaning |
|--------|---------|
| 400    | Validation error (missing file, bad format) |
| 404    | Session not found |
| 413    | File too large (>100MB) |
| 422    | Frame processed but no pose detected |
| 500    | Internal server error |

Error response format:

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

---

## POST /analyze-video

Upload a video file for full session analysis.

**Content-Type:** `multipart/form-data`

**Fields:**
| Field  | Type | Required | Description |
|--------|------|----------|-------------|
| video  | file | Yes*     | Video file |
| file   | file | Yes*     | Alias for video |

*One of `video` or `file` is required.

**Supported formats:** `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

### Sample Request (curl)

```bash
curl -X POST http://localhost:5000/api/analyze-video \
  -F "video=@sample_squat.mp4"
```

### Sample Response (201)

```json
{
  "success": true,
  "session_id": 1,
  "data": {
    "id": 1,
    "created_at": "2026-06-18T12:30:00+00:00",
    "source_type": "video",
    "source_filename": "sample_squat.mp4",
    "duration_seconds": 12.5,
    "frame_count": 150,
    "activity_label": "squatting",
    "joint_angles_avg": {
      "shoulder_left": 92.4,
      "shoulder_right": 91.8,
      "elbow_left": 168.2,
      "elbow_right": 167.5,
      "hip_left": 145.3,
      "hip_right": 144.9,
      "knee_left": 128.6,
      "knee_right": 127.2,
      "ankle_left": 88.1,
      "ankle_right": 87.5
    },
    "joint_angles_max": { "...": "..." },
    "joint_angles_min": { "...": "..." },
    "range_of_motion": {
      "knee_left": 68.4,
      "hip_left": 52.1
    },
    "repetition_count": 5,
    "movement_speed_avg": 12.34,
    "posture_score": 82.5,
    "motor_function_score": 78.2,
    "posture_deviations": ["Hip angle asymmetry"],
    "summary": {
      "motor_function_score": 78.2,
      "activity_detected": "squatting",
      "total_repetitions": 5,
      "posture_score": 82.5,
      "deviation_count": 1,
      "status": "healthy"
    },
    "status": "completed"
  }
}
```

---

## POST /analyze-frame

Analyze a single image frame.

**Option A — Multipart upload**

```bash
curl -X POST http://localhost:5000/api/analyze-frame \
  -F "image=@pose_photo.jpg"
```

**Option B — JSON with base64**

```bash
curl -X POST http://localhost:5000/api/analyze-frame \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "data:image/jpeg;base64,/9j/4AAQ..."}'
```

### Sample Response (201)

```json
{
  "success": true,
  "session_id": 2,
  "data": {
    "frame_index": 0,
    "timestamp_seconds": 0.0,
    "pose_detected": true,
    "joint_angles": {
      "shoulder_left": 95.2,
      "elbow_left": 172.1,
      "hip_left": 168.4,
      "knee_left": 176.3,
      "ankle_left": 91.0
    },
    "movement_speed": 0.0,
    "repetition_count": 0,
    "posture_score": 88.5,
    "posture_deviations": [],
    "overlay_image": "data:image/jpeg;base64,...",
    "session_summary": { "...": "full session object" }
  }
}
```

### No Pose Detected (422)

```json
{
  "success": false,
  "session_id": 3,
  "data": {
    "error": "No pose detected in frame"
  }
}
```

---

## GET /session/{id}

Retrieve a session with per-frame metrics.

### Sample Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "motor_function_score": 78.2,
    "frame_metrics": [
      {
        "frame_index": 0,
        "timestamp_seconds": 0.0,
        "joint_angles": {
          "knee_left": 175.2,
          "elbow_left": 168.0
        },
        "movement_speed": 0.0,
        "posture_score": 85.0
      }
    ]
  }
}
```

---

## GET /history

Paginated session list.

**Query parameters:**
| Param  | Default | Max | Description |
|--------|---------|-----|-------------|
| limit  | 50      | 100 | Page size   |
| offset | 0       | —   | Skip count  |

### Sample Response

```json
{
  "success": true,
  "total": 12,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": 12,
      "created_at": "2026-06-18T14:00:00+00:00",
      "activity_label": "walking",
      "motor_function_score": 81.0,
      "posture_score": 86.2,
      "repetition_count": 0
    }
  ]
}
```

---

## GET /report/{id}

Detailed report with assessment and recommendations.

### Sample Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "motor_function_score": 78.2,
    "posture_score": 82.5,
    "frame_metrics": [ "..." ],
    "report": {
      "overall_assessment": "Good",
      "recommendations": [
        "Address posture deviations: Hip angle asymmetry",
        "Maintain current activity level with regular monitoring"
      ]
    }
  }
}
```

---

## GET /health

```json
{
  "success": true,
  "status": "healthy",
  "service": "motor-function-tracker"
}
```

---

## Calculated Metrics Reference

| Metric | Description |
|--------|-------------|
| shoulder_angle | Angle at shoulder (hip-shoulder-elbow) |
| elbow_angle | Angle at elbow (shoulder-elbow-wrist) |
| hip_angle | Angle at hip (shoulder-hip-knee) |
| knee_angle | Angle at knee (hip-knee-ankle) |
| ankle_angle | Angle at ankle (knee-ankle-foot) |
| movement_speed | Hip center displacement per second (pixels/s) |
| range_of_motion | Max − min angle per joint over session |
| repetition_count | Peak-valley cycles on primary joint |
| posture_score | 0–100 alignment score |
| motor_function_score | Weighted composite of posture, ROM, symmetry, movement |
