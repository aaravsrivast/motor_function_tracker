import 'joint_angles.dart';

class AnalysisSession {
  final int id;
  final DateTime? createdAt;
  final String sourceType;
  final String? sourceFilename;
  final double? durationSeconds;
  final int frameCount;
  final String? activityLabel;
  final JointAngles jointAnglesAvg;
  final JointAngles jointAnglesMax;
  final JointAngles jointAnglesMin;
  final Map<String, double?> rangeOfMotion;
  final int repetitionCount;
  final double? movementSpeedAvg;
  final double? postureScore;
  final double? motorFunctionScore;
  final List<String> postureDeviations;
  final Map<String, dynamic>? summary;
  final String status;
  final List<FrameMetric>? frameMetrics;
  final Map<String, dynamic>? report;

  AnalysisSession({
    required this.id,
    this.createdAt,
    required this.sourceType,
    this.sourceFilename,
    this.durationSeconds,
    this.frameCount = 0,
    this.activityLabel,
    required this.jointAnglesAvg,
    required this.jointAnglesMax,
    required this.jointAnglesMin,
    this.rangeOfMotion = const {},
    this.repetitionCount = 0,
    this.movementSpeedAvg,
    this.postureScore,
    this.motorFunctionScore,
    this.postureDeviations = const [],
    this.summary,
    this.status = 'completed',
    this.frameMetrics,
    this.report,
  });

  factory AnalysisSession.fromJson(Map<String, dynamic> json) {
    return AnalysisSession(
      id: json['id'] as int,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
      sourceType: json['source_type'] ?? 'unknown',
      sourceFilename: json['source_filename'],
      durationSeconds: (json['duration_seconds'] as num?)?.toDouble(),
      frameCount: json['frame_count'] ?? 0,
      activityLabel: json['activity_label'],
      jointAnglesAvg: JointAngles.fromJson(json['joint_angles_avg']),
      jointAnglesMax: JointAngles.fromJson(json['joint_angles_max']),
      jointAnglesMin: JointAngles.fromJson(json['joint_angles_min']),
      rangeOfMotion: _parseRom(json['range_of_motion']),
      repetitionCount: json['repetition_count'] ?? 0,
      movementSpeedAvg: (json['movement_speed_avg'] as num?)?.toDouble(),
      postureScore: (json['posture_score'] as num?)?.toDouble(),
      motorFunctionScore: (json['motor_function_score'] as num?)?.toDouble(),
      postureDeviations: List<String>.from(json['posture_deviations'] ?? []),
      summary: json['summary'] as Map<String, dynamic>?,
      status: json['status'] ?? 'completed',
      frameMetrics: (json['frame_metrics'] as List?)
          ?.map((e) => FrameMetric.fromJson(e as Map<String, dynamic>))
          .toList(),
      report: json['report'] as Map<String, dynamic>?,
    );
  }
}

class FrameMetric {
  final int frameIndex;
  final double? timestampSeconds;
  final JointAngles jointAngles;
  final double? movementSpeed;
  final double? postureScore;

  FrameMetric({
    required this.frameIndex,
    this.timestampSeconds,
    required this.jointAngles,
    this.movementSpeed,
    this.postureScore,
  });

  factory FrameMetric.fromJson(Map<String, dynamic> json) {
    return FrameMetric(
      frameIndex: json['frame_index'] ?? 0,
      timestampSeconds: (json['timestamp_seconds'] as num?)?.toDouble(),
      jointAngles: JointAngles.fromJson(json['joint_angles']),
      movementSpeed: (json['movement_speed'] as num?)?.toDouble(),
      postureScore: (json['posture_score'] as num?)?.toDouble(),
    );
  }
}

Map<String, double?> _parseRom(dynamic raw) {
  if (raw is! Map) return {};
  return raw.map((k, v) => MapEntry(k.toString(), (v as num?)?.toDouble()));
}
