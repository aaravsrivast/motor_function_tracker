import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';

class Base64Image extends StatelessWidget {
  final String dataUri;
  final double? height;
  final BoxFit fit;

  const Base64Image({
    super.key,
    required this.dataUri,
    this.height,
    this.fit = BoxFit.cover,
  });

  Uint8List? _decode() {
    try {
      var raw = dataUri;
      if (raw.contains(',')) {
        raw = raw.split(',').last;
      }
      return base64Decode(raw);
    } catch (_) {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    final bytes = _decode();
    if (bytes == null) return const SizedBox.shrink();
    return Image.memory(bytes, height: height, width: double.infinity, fit: fit);
  }
}
