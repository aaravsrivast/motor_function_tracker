import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../models/analysis_session.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

class ApiService {
  // Android emulator: 10.0.2.2 | iOS simulator: localhost | device: your machine IP
  static const String defaultBaseUrl = 'http://127.0.0.1:5000/api';

  final String baseUrl;
  final http.Client _client;

  ApiService({String? baseUrl, http.Client? client})
      : baseUrl = baseUrl ?? defaultBaseUrl,
        _client = client ?? http.Client();

  Future<AnalysisSession> analyzeVideo(File videoFile) async {
    final uri = Uri.parse('$baseUrl/analyze-video');
    final request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('video', videoFile.path));
    final streamed = await _client.send(request);
    final response = await http.Response.fromStream(streamed);
    return _parseSessionResponse(response);
  }

  Future<Map<String, dynamic>> analyzeFrame(File imageFile) async {
    final uri = Uri.parse('$baseUrl/analyze-frame');
    final request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
    final streamed = await _client.send(request);
    final response = await http.Response.fromStream(streamed);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw ApiException(body['error']?.toString() ?? 'Frame analysis failed', statusCode: response.statusCode);
    }
    return body;
  }

  Future<AnalysisSession> getSession(int id) async {
    final response = await _client.get(Uri.parse('$baseUrl/session/$id'));
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode == 404) throw ApiException('Session not found', statusCode: 404);
    return AnalysisSession.fromJson(body['data']);
  }

  Future<List<AnalysisSession>> getHistory({int limit = 50, int offset = 0}) async {
    final uri = Uri.parse('$baseUrl/history').replace(queryParameters: {
      'limit': limit.toString(),
      'offset': offset.toString(),
    });
    final response = await _client.get(uri);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    final list = body['data'] as List? ?? [];
    return list.map((e) => AnalysisSession.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<AnalysisSession> getReport(int id) async {
    final response = await _client.get(Uri.parse('$baseUrl/report/$id'));
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode == 404) throw ApiException('Report not found', statusCode: 404);
    return AnalysisSession.fromJson(body['data']);
  }

  Future<bool> healthCheck() async {
    try {
      final response = await _client.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  AnalysisSession _parseSessionResponse(http.Response response) {
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw ApiException(body['error']?.toString() ?? 'Request failed', statusCode: response.statusCode);
    }
    return AnalysisSession.fromJson(body['data']);
  }

  void dispose() => _client.close();
}
