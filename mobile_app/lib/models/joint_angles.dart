class JointAngles {
  final double? shoulderLeft;
  final double? shoulderRight;
  final double? elbowLeft;
  final double? elbowRight;
  final double? hipLeft;
  final double? hipRight;
  final double? kneeLeft;
  final double? kneeRight;
  final double? ankleLeft;
  final double? ankleRight;

  const JointAngles({
    this.shoulderLeft,
    this.shoulderRight,
    this.elbowLeft,
    this.elbowRight,
    this.hipLeft,
    this.hipRight,
    this.kneeLeft,
    this.kneeRight,
    this.ankleLeft,
    this.ankleRight,
  });

  factory JointAngles.fromJson(Map<String, dynamic>? json) {
    if (json == null) return const JointAngles();
    return JointAngles(
      shoulderLeft: _toDouble(json['shoulder_left']),
      shoulderRight: _toDouble(json['shoulder_right']),
      elbowLeft: _toDouble(json['elbow_left']),
      elbowRight: _toDouble(json['elbow_right']),
      hipLeft: _toDouble(json['hip_left']),
      hipRight: _toDouble(json['hip_right']),
      kneeLeft: _toDouble(json['knee_left']),
      kneeRight: _toDouble(json['knee_right']),
      ankleLeft: _toDouble(json['ankle_left']),
      ankleRight: _toDouble(json['ankle_right']),
    );
  }

  static double? _toDouble(dynamic v) =>
      v == null ? null : (v is num ? v.toDouble() : double.tryParse(v.toString()));

  Map<String, double> toChartMap() {
    final map = <String, double>{};
    void add(String key, double? val) {
      if (val != null) map[key] = val;
    }
    add('Shoulder L', shoulderLeft);
    add('Shoulder R', shoulderRight);
    add('Elbow L', elbowLeft);
    add('Elbow R', elbowRight);
    add('Hip L', hipLeft);
    add('Hip R', hipRight);
    add('Knee L', kneeLeft);
    add('Knee R', kneeRight);
    add('Ankle L', ankleLeft);
    add('Ankle R', ankleRight);
    return map;
  }
}
