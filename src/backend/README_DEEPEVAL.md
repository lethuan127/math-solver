# DeepEval Math Solver Evaluation

This document describes the DeepEval setup for evaluating the Math Solver LLM performance using test cases with expected answers.

## Overview

The evaluation framework uses DeepEval to assess the Math Solver's performance across multiple dimensions:
- **Mathematical Accuracy**: How correct are the final answers?
- **Solution Completeness**: Does the response include steps, explanations, and reasoning?
- **Answer Relevancy**: How relevant is the response to the mathematical problem?
- **Faithfulness**: How faithful is the solution to the problem context?

## Setup

### Prerequisites

1. **Dependencies**: DeepEval is already included in the project dependencies
2. **OpenAI API Key**: Required for LLM-based evaluation metrics
3. **Test Cases**: Located in `tests/evaluation/usecases/`

### Environment Variables

Set the following environment variables:

```bash
# Required for your Math Solver
export OPENAI_API_KEY="your-openai-api-key"

# Optional for DeepEval cloud features
export DEEPEVAL_API_KEY="your-deepeval-api-key"
```

## Test Cases Structure

Test cases are defined in `tests/evaluation/usecases/0.json`:

```json
[
  {
    "image_file": "1.png",
    "expected_answer": "63 040"
  },
  {
    "image_file": "2.png", 
    "expected_answer": "35%"
  }
  // ... more test cases
]
```

Each test case contains:
- `image_file`: Name of the image file containing the math problem
- `expected_answer`: The correct answer for evaluation

## Files Structure

```
tests/evaluation/
├── usecases/
│   ├── 0.json              # Test case definitions
│   ├── 1.png               # Math problem images
│   ├── 2.png
│   └── ...
├── test_math_solver_deepeval.py  # Main evaluation test
├── metrics.py              # Custom DeepEval metrics
└── run_evaluation.py       # Standalone evaluation runner
```

## Running Evaluations

### Method 1: Using pytest

```bash
# Run evaluation on first 5 test cases (quick test)
uv run pytest tests/evaluation/test_math_solver_deepeval.py::test_math_solver_evaluation -v

# Run evaluation on all test cases
uv run pytest tests/evaluation/test_math_solver_deepeval.py::test_full_math_solver_evaluation -v
```

### Method 2: Using the standalone runner

```bash
# Run evaluation on first 10 test cases
uv run python tests/evaluation/run_evaluation.py --max-cases 10

# Run evaluation on all test cases
uv run python tests/evaluation/run_evaluation.py

# Run without saving results
uv run python tests/evaluation/run_evaluation.py --no-save

# Specify custom output directory
uv run python tests/evaluation/run_evaluation.py --output-dir my_results
```

### Method 3: Direct Python execution

```python
import asyncio
from tests.evaluation.test_math_solver_deepeval import MathSolverEvaluator

async def run_eval():
    evaluator = MathSolverEvaluator()
    results = await evaluator.run_evaluation(max_cases=5)
    print(f"Accuracy: {results['accuracy']:.2f}%")

asyncio.run(run_eval())
```

## Custom Metrics

### MathematicalAccuracyMetric

Evaluates the correctness of mathematical answers with:
- **Advanced normalization** for mathematical expressions
- **Flexible matching** for different representations (e.g., 1/2 = 0.5 = 50%)
- **LLM-based evaluation** for complex equivalences
- **Unit handling** and formatting differences

```python
from tests.evaluation.metrics import MathematicalAccuracyMetric

metric = MathematicalAccuracyMetric(
    threshold=0.9,
    use_llm_evaluation=True,
    strict_matching=False
)
```

### MathSolutionCompletenessMetric

Evaluates the completeness of solutions by checking for:
- Final answer (40% weight)
- Solution steps (30% weight)  
- Explanations (20% weight)
- Mathematical reasoning (10% weight)

### Standard DeepEval Metrics

- **AnswerRelevancyMetric**: Measures relevance to the question
- **FaithfulnessMetric**: Measures faithfulness to context
- **ContextualPrecisionMetric**: Measures precision in context
- **ContextualRecallMetric**: Measures recall in context

## Configuration

Evaluation settings can be customized in `deepeval_config.py`:

```python
METRICS_CONFIG = {
    "custom_math_accuracy": {
        "threshold": 0.9,
        "strict_matching": False,
        "normalize_answers": True,
    },
    "answer_relevancy": {
        "threshold": 0.7,
        "model": "gpt-4.1",
        "include_reason": True,
    },
    # ... more metrics
}
```

## Output and Reporting

### Console Output

The evaluation provides real-time progress and detailed results:

```
🚀 Starting Math Solver Evaluation
==================================================
Solving case 1/30: tests/evaluation/usecases/1.png
Expected: 63 040, Got: 63040
...
📋 MATH SOLVER EVALUATION REPORT
==================================================
⏱️  Duration: 45.23 seconds
📊 Test Cases: 30
🎯 Exact Accuracy: 83.3% (25/30)
🎯 Partial Accuracy: 90.0% (27/30)
```

### Saved Results

Results are automatically saved to:
- **JSON**: `evaluation_results/evaluation_results_YYYYMMDD_HHMMSS.json`
- **CSV**: `evaluation_results/evaluation_summary_YYYYMMDD_HHMMSS.csv`

### DeepEval Dashboard

If you have a DeepEval API key, results can be viewed in the DeepEval web dashboard for advanced analytics and visualization.

## Interpreting Results

### Accuracy Metrics

- **Exact Accuracy**: Percentage of answers that match exactly
- **Partial Accuracy**: Percentage including close matches and numerical equivalents
- **DeepEval Scores**: LLM-based evaluation scores (0.0 to 1.0)

### Common Issues

1. **Formatting Differences**: "1/2" vs "0.5" vs "50%" - handled by normalization
2. **Unit Variations**: "cm³" vs "cubic cm" - handled by unit normalization  
3. **Spacing/Punctuation**: Handled by text cleaning
4. **Mathematical Equivalence**: Different valid forms - handled by LLM evaluation

## Troubleshooting

### Common Errors

1. **Missing OpenAI API Key**
   ```
   Error: OpenAI API key not found
   Solution: Set OPENAI_API_KEY environment variable
   ```

2. **Image File Not Found**
   ```
   Error: Cannot find image file
   Solution: Ensure all images exist in tests/evaluation/usecases/
   ```

3. **DeepEval Import Error**
   ```
   Error: No module named 'deepeval'
   Solution: Run 'uv sync' to install dependencies
   ```

### Performance Tips

1. **Limit Test Cases**: Use `--max-cases` for faster iteration
2. **Disable LLM Evaluation**: Set `use_llm_evaluation=False` for speed
3. **Use Caching**: DeepEval caches results to avoid re-evaluation

## Extending the Framework

### Adding New Metrics

1. Create a new metric class in `metrics.py`:

```python
class YourCustomMetric(BaseMetric):
    def measure(self, test_case: LLMTestCase) -> float:
        # Your evaluation logic
        return score
```

2. Add it to the evaluator in `test_math_solver_deepeval.py`:

```python
def get_metrics(self) -> List[BaseMetric]:
    return [
        # ... existing metrics
        YourCustomMetric(threshold=0.8)
    ]
```

### Adding New Test Cases

1. Add images to `tests/evaluation/usecases/`
2. Update `tests/evaluation/usecases/0.json` with new entries
3. Run evaluation to test new cases

## Best Practices

1. **Regular Evaluation**: Run evaluations after model changes
2. **Version Control**: Track evaluation results over time
3. **Threshold Tuning**: Adjust thresholds based on requirements
4. **Error Analysis**: Review failed cases for improvement opportunities
5. **Comprehensive Testing**: Test across different problem types and difficulties

## Integration with CI/CD

Add to your CI pipeline:

```yaml
- name: Run Math Solver Evaluation
  run: |
    uv run python tests/evaluation/run_evaluation.py --max-cases 10
```

This ensures consistent performance monitoring and prevents regressions.
