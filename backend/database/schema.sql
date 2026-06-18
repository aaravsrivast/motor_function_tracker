"""Database schema SQL reference.

Tables are auto-created by SQLAlchemy on startup.
This file documents the schema for manual migrations or PostgreSQL setup.
"""

SCHEMA_SQL = """
-- Analysis sessions table
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_type VARCHAR(20) NOT NULL,
    source_filename VARCHAR(255),
    duration_seconds FLOAT,
    frame_count INTEGER DEFAULT 0,
    activity_label VARCHAR(50),
    joint_angles_avg TEXT,
    joint_angles_max TEXT,
    joint_angles_min TEXT,
    range_of_motion TEXT,
    repetition_count INTEGER DEFAULT 0,
    movement_speed_avg FLOAT,
    posture_score FLOAT,
    motor_function_score FLOAT,
    posture_deviations TEXT,
    summary TEXT,
    overlay_video_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT
);

-- Per-frame metrics table
CREATE TABLE IF NOT EXISTS frame_metrics (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    frame_index INTEGER NOT NULL,
    timestamp_seconds FLOAT,
    shoulder_angle_left FLOAT,
    shoulder_angle_right FLOAT,
    elbow_angle_left FLOAT,
    elbow_angle_right FLOAT,
    hip_angle_left FLOAT,
    hip_angle_right FLOAT,
    knee_angle_left FLOAT,
    knee_angle_right FLOAT,
    ankle_angle_left FLOAT,
    ankle_angle_right FLOAT,
    movement_speed FLOAT,
    posture_score FLOAT,
    landmarks TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON analysis_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_frame_metrics_session_id ON frame_metrics(session_id);
"""
