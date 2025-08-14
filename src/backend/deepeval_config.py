"""
DeepEval configuration for math solver evaluation
"""
import os
from typing import Dict, Any

# DeepEval configuration
DEEPEVAL_CONFIG = {
    "project_name": "math-solver-evaluation",
    "api_key": os.getenv("DEEPEVAL_API_KEY"),  # Optional: for cloud features
    "cache_results": True,
    "verbose": True,
    # Parallel execution settings
    "max_workers": int(os.getenv("DEEPEVAL_MAX_WORKERS", "4")),
    "parallel_timeout": int(os.getenv("DEEPEVAL_PARALLEL_TIMEOUT", "300")),  # 5 minutes
}

# Test case configuration
TEST_CASES_CONFIG = {
    "usecases_file": "tests/evaluation/usecases/0.json",
    "images_directory": "tests/evaluation/usecases/",
    "max_test_cases": None,  # None means all test cases
    "timeout_seconds": 60,
}

# Metrics configuration
METRICS_CONFIG = {
    "answer_relevancy": {
        "threshold": 0.7,
        "model": "gpt-4.1",
        "include_reason": True,
    },
    "faithfulness": {
        "threshold": 0.8,
        "model": "gpt-4.1",
        "include_reason": True,
    },
    "contextual_precision": {
        "threshold": 0.7,
        "model": "gpt-4.1",
        "include_reason": True,
    },
    "contextual_recall": {
        "threshold": 0.7,
        "model": "gpt-4.1",
        "include_reason": True,
    },
    "custom_math_accuracy": {
        "threshold": 0.9,
        "strict_matching": False,  # Allow for formatting differences
        "normalize_answers": True,  # Normalize answers for comparison
    }
}

# LLM configuration for evaluation
LLM_CONFIG = {
    "model": "gpt-4.1",
    "temperature": 0.1,  # Low temperature for consistent evaluation
    "max_tokens": 1000,
    "timeout": 30,
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration"""
    return {
        "deepeval": DEEPEVAL_CONFIG,
        "test_cases": TEST_CASES_CONFIG,
        "metrics": METRICS_CONFIG,
        "llm": LLM_CONFIG,
    }
