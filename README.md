# Motor Function Tracker

> AI-powered computer vision for real-time human movement, posture, and motor function analysis.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flutter](https://img.shields.io/badge/Flutter-3.16+-blue.svg)](https://flutter.dev)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)

## What It Does

Motor Function Tracker uses computer vision to analyze video and images of human movement. It detects body landmarks, calculates joint angles, counts repetitions, scores posture, and generates motor function reports — all viewable in a Flutter mobile dashboard.

## Project Structure

```
motor_function_tracker/
├── backend/
│   ├── app.py                 # Flask entry point
│   ├── config.py              # Configuration
│   ├── routes/                # API endpoints
│   ├── services/                # CV pipeline + business logic
│   ├── models/                # SQLAlchemy models
│   ├── utils/                 # Geometry, errors, constants
│   ├── database/              # DB init + schema
│   └── requirements.txt
├── mobile_app/
│   └── lib/
│       ├── screens/           # Dashboard, upload, history, report
│       ├── widgets/           # Charts, cards, score rings
│       ├── services/          # API client
│       └── models/            # Data models
├── docs/
│   ├── README.md
│   ├── API_DOCUMENTATION.md
│   └── SYSTEM_DESIGN.md
└── requirements.txt
```

## Quick Start

```bash
# Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m backend.app

# Mobile (separate terminal)
cd mobile_app && flutter pub get && flutter run
```

## Documentation

- [Setup & Overview](docs/README.md)
- [API Reference](docs/API_DOCUMENTATION.md)
- [System Design](docs/SYSTEM_DESIGN.md)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| Computer Vision | OpenCV, MediaPipe Pose |
| Database | SQLite / PostgreSQL |
| Mobile | Flutter, fl_chart |
| Optional ML | TensorFlow / PyTorch (activity classification) |

## License

MIT
