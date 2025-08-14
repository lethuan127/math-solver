# Parallel Evaluation with DeepEval

This document explains how to run your math solver evaluation in parallel using DeepEval's built-in parallel execution capabilities.

## Quick Start

### Option 1: Using the Parallel Runner Script (Recommended)

```bash
# Run with 4 parallel workers, max 10 cases
uv run python run_parallel_evaluation.py --parallel --workers 4 --max-cases 10

# Quick test with 2 workers, 5 cases
uv run python run_parallel_evaluation.py -p -w 2 -c 5

# Generate HTML report
uv run python run_parallel_evaluation.py --parallel --workers 8 --output report.html
```

### Option 2: Direct DeepEval CLI

```bash
# Run individual test cases in parallel (4 workers)
uv run deepeval test run tests/evaluation/test_math_solver_deepeval.py::test_individual_math_problem -n 4

# With verbose output
uv run deepeval test run tests/evaluation/test_math_solver_deepeval.py::test_individual_math_problem -n 4 -v

# Generate HTML report
uv run deepeval test run tests/evaluation/test_math_solver_deepeval.py::test_individual_math_problem -n 4 --html report.html
```

### Option 3: Sequential (Original Method)

```bash
# Original sequential approach
uv run python tests/evaluation/run_evaluation.py --max-cases 10

# Or using the runner script
uv run python run_parallel_evaluation.py --sequential --max-cases 10
```

## Performance Comparison

| Method | Workers | 10 Cases | 30 Cases | Notes |
|--------|---------|----------|----------|-------|
| Sequential | 1 | ~2-3 min | ~8-10 min | Original method |
| Parallel | 4 | ~45-60 sec | ~3-4 min | 3-4x faster |
| Parallel | 8 | ~30-45 sec | ~2-3 min | 4-5x faster |

## Configuration

### Environment Variables

You can configure parallel execution using environment variables:

```bash
export DEEPEVAL_MAX_WORKERS=8        # Default number of workers
export DEEPEVAL_PARALLEL_TIMEOUT=300 # Timeout in seconds
```

### Test Case Range

The parallel test function is configured to handle up to 30 test cases by default. If you have more test cases, update the range in `test_math_solver_deepeval.py`:

```python
@pytest.mark.parametrize("case_index", range(50))  # Increase to 50 or your max
```

## How It Works

### Parallel Execution Flow

1. **Test Discovery**: DeepEval discovers all parametrized test cases
2. **Worker Distribution**: Test cases are distributed across N workers
3. **Concurrent Execution**: Each worker processes test cases independently
4. **Result Aggregation**: Results are collected and reported

### Key Components

- **`test_individual_math_problem`**: Parametrized test function that processes one case at a time
- **`run_parallel_evaluation.py`**: Convenient script with CLI options
- **DeepEval CLI**: Built-in parallel execution with `-n` flag

## Troubleshooting

### Common Issues

1. **Too Many Workers**: Don't use more workers than CPU cores
2. **Memory Issues**: Large images might cause memory problems with many workers
3. **API Rate Limits**: LLM APIs might have rate limits affecting parallel requests

### Optimal Settings

- **CPU Cores**: Use `workers = CPU cores - 1` for best performance
- **Memory**: Monitor memory usage with many concurrent image processes
- **Network**: Consider API rate limits when setting worker count

### Example Commands for Different Scenarios

```bash
# Quick test (2 workers, 5 cases)
uv run python run_parallel_evaluation.py -p -w 2 -c 5

# Full evaluation (8 workers, all cases)
uv run python run_parallel_evaluation.py -p -w 8 -c 30

# Generate detailed report
uv run python run_parallel_evaluation.py -p -w 4 -c 10 -o detailed_report.html -v

# Conservative parallel run (good for limited resources)
uv run python run_parallel_evaluation.py -p -w 2 -c 10
```

## Benefits of Parallel Execution

1. **Speed**: 3-5x faster evaluation
2. **Scalability**: Easy to adjust worker count
3. **Resource Utilization**: Better CPU/GPU utilization
4. **Reporting**: Same detailed reports as sequential
5. **Flexibility**: Can mix parallel and sequential runs

## Next Steps

- Monitor your system resources during parallel runs
- Adjust worker count based on your hardware
- Consider API rate limits for your LLM provider
- Use HTML reports for better result visualization
