import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/analysis_session.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/joint_angle_chart.dart';
import '../widgets/score_ring.dart';
import '../widgets/score_trend_chart.dart';

class ReportScreen extends StatefulWidget {
  final int sessionId;

  const ReportScreen({super.key, required this.sessionId});

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  final _api = ApiService();
  AnalysisSession? _session;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      _session = await _api.getReport(widget.sessionId);
    } catch (e) {
      _error = e.toString();
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Report #${widget.sessionId}')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : _buildReport(_session!),
    );
  }

  Widget _buildReport(AnalysisSession session) {
    final report = session.report ?? {};
    final assessment = report['overall_assessment'] ?? 'N/A';
    final recommendations = List<String>.from(report['recommendations'] ?? []);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          color: AppTheme.primary.withOpacity(0.08),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                Text(
                  assessment,
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.scoreColor(session.motorFunctionScore),
                  ),
                ),
                const SizedBox(height: 4),
                const Text('Overall Assessment', style: TextStyle(color: AppTheme.textSecondary)),
                if (session.createdAt != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      DateFormat('MMMM d, yyyy').format(session.createdAt!),
                      style: const TextStyle(fontSize: 13, color: AppTheme.textSecondary),
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            ScoreRing(score: session.motorFunctionScore, label: 'Motor Function', size: 100),
            ScoreRing(score: session.postureScore, label: 'Posture', size: 100),
          ],
        ),
        const SizedBox(height: 20),
        JointAngleChart(angles: session.jointAnglesAvg.toChartMap(), title: 'Average Joint Angles'),
        if (session.frameMetrics != null)
          ScoreTrendChart(frames: session.frameMetrics!),
        const SizedBox(height: 16),
        _sectionTitle('Range of Motion'),
        ...session.rangeOfMotion.entries.map(
          (e) => ListTile(
            title: Text(e.key.replaceAll('_', ' ')),
            trailing: Text('${e.value?.toStringAsFixed(1) ?? '—'}°'),
          ),
        ),
        const SizedBox(height: 16),
        _sectionTitle('Recommendations'),
        ...recommendations.map(
          (r) => Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: const Icon(Icons.lightbulb_outline, color: AppTheme.secondary),
              title: Text(r),
            ),
          ),
        ),
        if (session.postureDeviations.isNotEmpty) ...[
          const SizedBox(height: 16),
          _sectionTitle('Detected Issues'),
          ...session.postureDeviations.map(
            (d) => ListTile(
              leading: const Icon(Icons.warning_amber, color: AppTheme.warning),
              title: Text(d),
            ),
          ),
        ],
      ],
    );
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
    );
  }
}
