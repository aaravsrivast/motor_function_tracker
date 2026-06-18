import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/metric_card.dart';
import '../widgets/score_ring.dart';
import 'history_screen.dart';
import 'upload_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _api = ApiService();
  bool _loading = true;
  bool _apiOnline = false;
  double _avgMotorScore = 0;
  double _avgPostureScore = 0;
  int _totalSessions = 0;
  int _totalReps = 0;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() => _loading = true);
    try {
      _apiOnline = await _api.healthCheck();
      final sessions = await _api.getHistory(limit: 20);
      if (sessions.isNotEmpty) {
        final motorScores = sessions.where((s) => s.motorFunctionScore != null).map((s) => s.motorFunctionScore!);
        final postureScores = sessions.where((s) => s.postureScore != null).map((s) => s.postureScore!);
        _avgMotorScore = motorScores.isEmpty ? 0 : motorScores.reduce((a, b) => a + b) / motorScores.length;
        _avgPostureScore = postureScores.isEmpty ? 0 : postureScores.reduce((a, b) => a + b) / postureScores.length;
        _totalReps = sessions.fold(0, (sum, s) => sum + s.repetitionCount);
      }
      _totalSessions = sessions.length;
    } catch (_) {
      _apiOnline = false;
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Motor Function Tracker'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadDashboard),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadDashboard,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _buildStatusBanner(),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ScoreRing(score: _avgMotorScore, label: 'Avg Motor Score'),
                      ScoreRing(score: _avgPostureScore, label: 'Avg Posture'),
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
                        title: 'Sessions',
                        value: '$_totalSessions',
                        icon: Icons.video_library_outlined,
                        color: AppTheme.primary,
                      ),
                      MetricCard(
                        title: 'Repetitions',
                        value: '$_totalReps',
                        icon: Icons.repeat,
                        color: AppTheme.accent,
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  _buildQuickActions(context),
                ],
              ),
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const UploadScreen()),
        ).then((_) => _loadDashboard()),
        icon: const Icon(Icons.add_a_photo),
        label: const Text('New Analysis'),
      ),
    );
  }

  Widget _buildStatusBanner() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: _apiOnline ? AppTheme.success.withOpacity(0.12) : AppTheme.warning.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(_apiOnline ? Icons.cloud_done : Icons.cloud_off, color: _apiOnline ? AppTheme.success : AppTheme.warning),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _apiOnline ? 'API connected' : 'API offline — start backend server',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Quick Actions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
        const SizedBox(height: 12),
        _actionTile(context, 'Upload Video / Photo', Icons.upload_file, () {
          Navigator.push(context, MaterialPageRoute(builder: (_) => const UploadScreen()));
        }),
        _actionTile(context, 'Session History', Icons.history, () {
          Navigator.push(context, MaterialPageRoute(builder: (_) => const HistoryScreen()));
        }),
      ],
    );
  }

  Widget _actionTile(BuildContext context, String title, IconData icon, VoidCallback onTap) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: AppTheme.primary),
        title: Text(title),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
