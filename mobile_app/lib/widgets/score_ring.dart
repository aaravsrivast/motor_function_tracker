import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class ScoreRing extends StatelessWidget {
  final double? score;
  final String label;
  final double size;

  const ScoreRing({super.key, required this.score, required this.label, this.size = 120});

  @override
  Widget build(BuildContext context) {
    final value = score ?? 0;
    final color = AppTheme.scoreColor(score);
    return Column(
      children: [
        SizedBox(
          width: size,
          height: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: size,
                height: size,
                child: CircularProgressIndicator(
                  value: value / 100,
                  strokeWidth: 10,
                  backgroundColor: color.withOpacity(0.15),
                  color: color,
                ),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    score != null ? value.toStringAsFixed(0) : '—',
                    style: TextStyle(fontSize: size * 0.28, fontWeight: FontWeight.bold, color: color),
                  ),
                  const Text('%', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
      ],
    );
  }
}
