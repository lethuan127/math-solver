class SolutionStep {
  final int stepNumber;
  final String description;
  final String? calculation;

  SolutionStep({
    required this.stepNumber,
    required this.description,
    this.calculation,
  });

  factory SolutionStep.fromJson(Map<String, dynamic> json) {
    return SolutionStep(
      stepNumber: json['step_number'],
      description: json['description'],
      calculation: json['calculation'],
    );
  }
}

class MathSolution {
  final String originalText;
  final String solution;
  final List<SolutionStep> steps;
  final String explanation;

  MathSolution({
    required this.originalText,
    required this.solution,
    required this.steps,
    required this.explanation,
  });

  factory MathSolution.fromJson(Map<String, dynamic> json) {
    return MathSolution(
      originalText: json['original_text'],
      solution: json['solution'],
      steps: (json['steps'] as List)
          .map((step) => SolutionStep.fromJson(step))
          .toList(),
      explanation: json['explanation'],
    );
  }
}