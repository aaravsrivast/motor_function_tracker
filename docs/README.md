# Motor Function Tracker

AI-powered computer vision system for monitoring human movement, motor function, posture, and physical activity in real time.

## Overview

Motor Function Tracker is a full-stack application that:

- Detects human pose landmarks using **MediaPipe Pose**
- Calculates joint angles (shoulder, elbow, hip, knee, ankle)
- Tracks movement speed, repetitions, and range of motion
- Classifies activities and generates motor function scores
- Stores session history in **SQLite** or **PostgreSQL**
- Displays results in a **Flutter** mobile dashboard

## Architecture

```
motor_function_tracker/
├── backend/           # Flask API + computer vision pipeline
├── mobile_app/        # Flutter frontend
├── docs/              # Documentation
└── requirements.txt
```

## Quick Start

### Prerequisites

- Python 3.10+
- Flutter 3.16+ (for mobile app)
- Webcam or sample video for testing

### Backend Setup

```bash
cd motor_function_tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: copy and edit environment config
cp backend/.env.example backend/.env

# Run API server
python -m backend.app
```

API runs at `http://127.0.0.1:5000`

### Flutter App Setup

```bash
cd mobile_app
flutter pub get
flutter run
```

**API URL configuration:** Edit `lib/services/api_service.dart`:

| Platform        | Base URL                    |
|----------------|-----------------------------|
| iOS Simulator  | `http://127.0.0.1:5000/api` |
| Android Emulator | `http://10.0.2.2:5000/api` |
| Physical device | `http://<your-ip>:5000/api` |

### PostgreSQL (Optional)

```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/motor_tracker
python -m backend.app
```

## API Endpoints

| Method | Endpoint              | Description                |
|--------|-----------------------|----------------------------|
| POST   | `/api/analyze-video`  | Upload and analyze video   |
| POST   | `/api/analyze-frame`  | Analyze single image/frame |
| GET    | `/api/session/{id}`   | Get session details        |
| GET    | `/api/history`        | List past sessions         |
| GET    | `/api/report/{id}`    | Detailed report            |
| GET    | `/api/health`         | Health check               |

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for full details and sample responses.

## Features

1. Real-time human pose detection
2. Body landmark tracking
3. Joint angle calculation
4. Movement repetition counting
5. Activity classification
6. Motor function score generation
7. Posture deviation detection
8. Range of motion analysis
9. Session history tracking
10. Flutter dashboard with charts and reports

## Computer Vision Pipeline

```
Video/Frame → MediaPipe Pose → Landmarks → Angle Calculator
                                        → Motion Analyzer
                                        → Posture Detector
                                        → Activity Classifier
                                        → Scoring Service → JSON + DB
```

## Documentation

- [API Documentation](API_DOCUMENTATION.md)
- [System Design](SYSTEM_DESIGN.md)

## License

MIT
