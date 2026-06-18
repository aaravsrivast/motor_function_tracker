import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/loading_overlay.dart';
import 'analysis_screen.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final _picker = ImagePicker();
  final _api = ApiService();
  File? _selectedFile;
  bool _isVideo = false;
  bool _analyzing = false;
  String? _error;

  Future<void> _pickImage(ImageSource source) async {
    final file = await _picker.pickImage(source: source, imageQuality: 85);
    if (file != null) {
      setState(() {
        _selectedFile = File(file.path);
        _isVideo = false;
        _error = null;
      });
    }
  }

  Future<void> _pickVideo(ImageSource source) async {
    final file = await _picker.pickVideo(source: source);
    if (file != null) {
      setState(() {
        _selectedFile = File(file.path);
        _isVideo = true;
        _error = null;
      });
    }
  }

  Future<void> _analyze() async {
    if (_selectedFile == null) return;
    setState(() {
      _analyzing = true;
      _error = null;
    });

    try {
      if (_isVideo) {
        final session = await _api.analyzeVideo(_selectedFile!);
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => AnalysisScreen(session: session)),
        );
      } else {
        final result = await _api.analyzeFrame(_selectedFile!);
        if (!mounted) return;
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => AnalysisScreen.fromFrameResult(result),
          ),
        );
      }
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _analyzing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload & Analyze')),
      body: Stack(
        children: [
          ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text(
                'Select a video or photo for pose analysis',
                style: TextStyle(fontSize: 16, color: AppTheme.textSecondary),
              ),
              const SizedBox(height: 24),
              if (_selectedFile != null) ...[
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: _isVideo
                      ? Container(
                          height: 200,
                          color: Colors.black87,
                          child: const Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.videocam, color: Colors.white, size: 48),
                                SizedBox(height: 8),
                                Text('Video selected', style: TextStyle(color: Colors.white)),
                              ],
                            ),
                          ),
                        )
                      : Image.file(_selectedFile!, height: 280, width: double.infinity, fit: BoxFit.cover),
                ),
                const SizedBox(height: 16),
              ],
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _pickImage(ImageSource.gallery),
                      icon: const Icon(Icons.photo),
                      label: const Text('Photo'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _pickVideo(ImageSource.gallery),
                      icon: const Icon(Icons.video_library),
                      label: const Text('Video'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _pickImage(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt),
                      label: const Text('Camera'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _pickVideo(ImageSource.camera),
                      icon: const Icon(Icons.videocam),
                      label: const Text('Record'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Text(_error!, style: const TextStyle(color: AppTheme.danger)),
                ),
              ElevatedButton(
                onPressed: _selectedFile != null && !_analyzing ? _analyze : null,
                child: Text(_isVideo ? 'Analyze Video' : 'Analyze Frame'),
              ),
            ],
          ),
          if (_analyzing) const LoadingOverlay(message: 'Processing pose data...'),
        ],
      ),
    );
  }
}
