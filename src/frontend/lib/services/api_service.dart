import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/math_solution.dart';

final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

class ApiService {
  static const String baseUrl = 'http://localhost:8000'; // Change for production
  
  Future<MathSolution> solveMathProblem(File imageFile) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/solve-problem'),
      );
      
      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          imageFile.path,
        ),
      );
      
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return MathSolution.fromJson(data);
      } else {
        throw Exception('Failed to solve problem: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}