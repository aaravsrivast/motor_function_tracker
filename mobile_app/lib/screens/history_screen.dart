import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/analysis_session.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'analysis_screen.dart';
import 'report_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final _api = ApiService();
  List<AnalysisSession> _sessions = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      _sessions = await _api.getHistory();
    } catch (e) {
      _error = e.toString();
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Session History'),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppTheme.danger)))
              : _sessions.isEmpty
                  ? const Center(child: Text('No sessions yet'))
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _sessions.length,
                        itemBuilder: (context, i) => _SessionTile(
                          session: _sessions[i],
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => AnalysisScreen(session: _sessions[i])),
                          ),
                          onReport: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => ReportScreen(sessionId: _sessions[i].id)),
                          ),
                        ),
                      ),
                    ),
    );
  }
}

class _SessionTile extends StatelessWidget {
  final AnalysisSession session;
  final VoidCallback onTap;
  final VoidCallback onReport;

  const _SessionTile({required this.session, required this.onTap, required this.onReport});

  @override
  Widget build(BuildContext context) {
    final date = session.createdAt != null
        ? DateFormat('MMM d, HH:mm').format(session.createdAt!)
        : '—';
    final score = session.motorFunctionScore;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: AppTheme.scoreColor(score).withOpacity(0.15),
          child: Text(
            score != null ? score.toStringAsFixed(0) : '—',
            style: TextStyle(color: AppTheme.scoreColor(score), fontWeight: FontWeight.bold, fontSize: 13),
          ),
        ),
        title: Text('Session #${session.id} • ${session.activityLabel ?? session.sourceType}'),
        subtitle: Text('$date • ${session.repetitionCount} reps'),
        trailing: PopupMenuButton(
          itemBuilder: (_) => [
            const PopupMenuItem(value: 'view', child: Text('View Analysis')),
            const PopupMenuItem(value: 'report', child: Text('Full Report')),
          ],
          onSelected: (v) {
            if (v == 'view') onTap();
            if (v == 'report') onReport();
          },
        ),
        onTap: onTap,
      ),
    );
  }
}
