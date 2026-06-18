import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/analysis_session.dart';
import '../models/joint_angles.dart';
import '../theme/app_theme.dart';
import '../widgets/base64_image.dart';
import '../widgets/joint_angle_chart.dart';
import '../widgets/metric_card.dart';
import '../widgets/score_ring.dart';
import '../widgets/score_trend_chart.dart';
import 'report_screen.dart';

class AnalysisScreen extends StatelessWidget {
  final AnalysisSession session;
  final Map<String, dynamic>? frameOverlay;

  const AnalysisScreen({super.key, required this.session, this.frameOverlay});

  factory AnalysisScreen.fromFrameResult(Map<String, dynamic> result) {
    final data = result['data'] as Map<String, dynamic>? ?? {};
    final summary = data['session_summary'] as Map<String, dynamic>?;
    if (summary != null) {
      return AnalysisScreen(
        session: AnalysisSession.fromJson(summary),
        frameOverlay: data,
      );
    }
    return AnalysisScreen(
      session: AnalysisSession(
        id: result['session_id'] ?? 0,
        sourceType: 'frame',
        jointAnglesAvg: JointAngles.fromJson(data['joint_angles']),
        jointAnglesMax: JointAngles.fromJson(data['joint_angles']),
        jointAnglesMin: JointAngles.fromJson(data['joint_angles']),
        postureScore: (data['posture_score'] as num?)?.toDouble(),
        motorFunctionScore: (data['posture_score'] as num?)?.toDouble(),
        repetitionCount: data['repetition_count'] ?? 0,
        postureDeviations: List<String>.from(data['posture_deviations'] ?? []),
      ),
      frameOverlay: data,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis Results'),
        actions: [
          if (session.id > 0)
            IconButton(
              icon: const Icon(Icons.summarize),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => ReportScreen(sessionId: session.id)),
              ),
            ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (frameOverlay?['overlay_image'] != null) ...[
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Base64Image(
                dataUri: frameOverlay!['overlay_image'] as String,
                height: 240,
              ),
            ),
            const SizedBox(height: 16),
          ],
          _buildHeader(),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              ScoreRing(score: session.motorFunctionScore, label: 'Motor Score'),
              ScoreRing(score: session.postureScore, label: 'Posture'),
            ],
          ),
          const SizedBox(height: 24),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.3,
            children: [
              MetricCard(
                title: 'Repetitions',
                value: '${session.repetitionCount}',
                icon: Icons.repeat,
                color: AppTheme.accent,
              ),
              MetricCard(
                title: 'Activity',
                value: session.activityLabel ?? '—',
                icon: Icons.directions_run,
                color: AppTheme.secondary,
              ),
              MetricCard(
                title: 'Frames',
                value: '${session.frameCount}',
                icon: Icons.movie,
                color: AppTheme.primary,
              ),
              MetricCard(
                title: 'Speed (avg)',
                value: session.movementSpeedAvg?.toStringAsFixed(2) ?? '—',
                icon: Icons.speed,
                color: AppTheme.warning,
              ),
            ],
          ),
          const SizedBox(height: 16),
          JointAngleChart(angles: session.jointAnglesAvg.toChartMap()),
          if (session.frameMetrics != null && session.frameMetrics!.isNotEmpty)
            ScoreTrendChart(frames: session.frameMetrics!),
          if (session.postureDeviations.isNotEmpty) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Posture Deviations', style: TextStyle(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    ...session.postureDeviations.map(
                      (d) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          children: [
                            const Icon(Icons.warning_amber, size: 18, color: AppTheme.warning),
                            const SizedBox(width: 8),
                            Expanded(child: Text(d)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildHeader() {
    final dateStr = session.createdAt != null
        ? DateFormat('MMM d, yyyy • HH:mm').format(session.createdAt!)
        : 'Just now';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Session #${session.id}',
          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(dateStr, style: const TextStyle(color: AppTheme.textSecondary)),
        if (session.durationSeconds != null && session.durationSeconds! > 0)
          Text(
            'Duration: ${session.durationSeconds!.toStringAsFixed(1)}s',
            style: const TextStyle(color: AppTheme.textSecondary),
          ),
      ],
    );
  }
}
