"""
DeepEval tests for Math Solver evaluation using test cases and expected answers
"""
import json
import os
import asyncio
from typing import List, Dict, Any
from pathlib import Path

import pytest
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.metrics.base_metric import BaseMetric
from fastapi import UploadFile
from io import BytesIO

from app.services.math_solver import MathSolver
from app.models.problem import ProblemResponse, Answer
from deepeval_config import get_config


class MathAccuracyMetric(BaseMetric):
    """Custom metric to evaluate mathematical answer accuracy"""
    
    def __init__(
        self,
        threshold: float = 0.9,
        model: str = "gpt-4.1",
        strict_matching: bool = False,
        normalize_answers: bool = True,
        include_reason: bool = True
    ):
        self.threshold = threshold
        self.model = model
        self.strict_matching = strict_matching
        self.normalize_answers = normalize_answers
        self.include_reason = include_reason
    
    def measure(self, test_case: LLMTestCase) -> float:
        """Measure the accuracy of the mathematical answer"""
        expected_answer = test_case.expected_output
        actual_answer = test_case.actual_output
        
        if self.normalize_answers:
            expected_normalized = self._normalize_answer(expected_answer)
            actual_normalized = self._normalize_answer(actual_answer)
        else:
            expected_normalized = expected_answer
            actual_normalized = actual_answer
        
        if self.strict_matching:
            # Exact string matching
            score = 1.0 if expected_normalized == actual_normalized else 0.0
        else:
            # Use LLM to evaluate semantic similarity for math answers
            score = self._llm_evaluate_math_accuracy(
                expected_normalized, actual_normalized
            )
        
        self.score = score
        self.reason = self._generate_reason(expected_answer, actual_answer, score)
        self.success = score >= self.threshold
        
        return score
    
    def _normalize_answer(self, answer: str) -> str:
        """Normalize mathematical answers for comparison"""
        if not answer:
            return ""
        
        # Remove extra whitespace
        normalized = answer.strip()
        
        # Handle common mathematical formatting
        replacements = {
            " ": "",  # Remove spaces
            "°": "degrees",  # Convert degree symbol
            "∠": "angle",  # Convert angle symbol
            "^": "**",  # Convert exponent notation
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized.lower()
    
    def _llm_evaluate_math_accuracy(self, expected: str, actual: str) -> float:
        """Use LLM to evaluate mathematical answer accuracy"""
        # This is a simplified version - you would implement LLM evaluation here
        # For now, we'll use string similarity as a fallback
        if expected.lower() == actual.lower():
            return 1.0
        elif expected.lower() in actual.lower() or actual.lower() in expected.lower():
            return 0.8
        else:
            return 0.0
    
    def _generate_reason(self, expected: str, actual: str, score: float) -> str:
        """Generate explanation for the score"""
        if score == 1.0:
            return f"Perfect match: Expected '{expected}', Got '{actual}'"
        elif score >= 0.8:
            return f"Close match: Expected '{expected}', Got '{actual}'"
        else:
            return f"Poor match: Expected '{expected}', Got '{actual}'"
    
    def is_successful(self) -> bool:
        """Check if the metric passed the threshold"""
        return self.success
    
    @property
    def __name__(self):
        return "Math Accuracy"


class MathSolverEvaluator:
    """Evaluator for Math Solver using DeepEval"""
    
    def __init__(self, config_path: str = None):
        self.config = get_config()
        self.math_solver = MathSolver()
        self.test_cases = []
        
    async def load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from JSON file"""
        usecases_file = self.config["test_cases"]["usecases_file"]
        images_dir = self.config["test_cases"]["images_directory"]
        
        with open(usecases_file, 'r') as f:
            raw_cases = json.load(f)
        
        test_cases = []
        for case in raw_cases:
            image_path = os.path.join(images_dir, case["image_file"])
            if os.path.exists(image_path):
                test_cases.append({
                    "image_file": image_path,
                    "expected_answer": case["expected_answer"],
                })
        
        return test_cases
    
    async def create_upload_file(self, image_path: str) -> UploadFile:
        """Create UploadFile object from image path"""
        with open(image_path, 'rb') as f:
            content = f.read()
        
        # Determine content type based on file extension
        ext = Path(image_path).suffix.lower()
        content_type = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }.get(ext, 'image/png')
        
        return UploadFile(
            filename=os.path.basename(image_path),
            file=BytesIO(content),
            headers={"content-type": content_type}
        )
    
    async def solve_math_problem(self, image_path: str) -> str:
        """Solve math problem and extract answer"""
        try:
            upload_file = await self.create_upload_file(image_path)
            response = await self.math_solver.solve(upload_file)
            
            # Extract the answer value from the response
            if hasattr(response, 'answer') and hasattr(response.answer, 'answer_value'):
                return response.answer.answer_value
            elif hasattr(response, 'solution'):
                return response.solution
            else:
                return str(response)
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def create_llm_test_cases(self, test_cases: List[Dict[str, Any]], actual_outputs: List[str]) -> List[LLMTestCase]:
        """Create LLMTestCase objects for evaluation"""
        llm_test_cases = []
        
        for i, (case, actual_output) in enumerate(zip(test_cases, actual_outputs)):
            test_case = LLMTestCase(
                input=f"Math problem from image: {case['image_file']}",
                actual_output=actual_output,
                expected_output=case["expected_answer"],
                context=[f"Mathematical problem solving from image {case['image_file']}"]
            )
            llm_test_cases.append(test_case)
        
        return llm_test_cases
    
    def get_metrics(self) -> List[BaseMetric]:
        """Get configured metrics for evaluation"""
        config = self.config["metrics"]
        
        metrics = [
            # Custom math accuracy metric
            MathAccuracyMetric(
                threshold=config["custom_math_accuracy"]["threshold"],
                strict_matching=config["custom_math_accuracy"]["strict_matching"],
                normalize_answers=config["custom_math_accuracy"]["normalize_answers"],
            ),
            # Answer relevancy - how relevant is the answer to the question
            AnswerRelevancyMetric(
                threshold=config["answer_relevancy"]["threshold"],
                model=config["answer_relevancy"]["model"],
                include_reason=config["answer_relevancy"]["include_reason"],
            ),
            # Faithfulness - how faithful is the answer to the context
            FaithfulnessMetric(
                threshold=config["faithfulness"]["threshold"],
                model=config["faithfulness"]["model"],
                include_reason=config["faithfulness"]["include_reason"],
            ),
        ]
        
        return metrics
    
    async def run_evaluation(self, max_cases: int = None) -> Dict[str, Any]:
        """Run the complete evaluation"""
        print("Loading test cases...")
        test_cases = await self.load_test_cases()
        
        if max_cases:
            test_cases = test_cases[:max_cases]
        
        print(f"Running evaluation on {len(test_cases)} test cases...")
        
        # Solve all math problems
        actual_outputs = []
        for i, case in enumerate(test_cases):
            print(f"Solving case {i+1}/{len(test_cases)}: {case['image_file']}")
            actual_output = await self.solve_math_problem(case["image_file"])
            actual_outputs.append(actual_output)
            print(f"Expected: {case['expected_answer']}, Got: {actual_output}")
        
        # Create LLM test cases
        llm_test_cases = self.create_llm_test_cases(test_cases, actual_outputs)
        
        # Get metrics
        metrics = self.get_metrics()
        
        print("Running DeepEval evaluation...")
        # Run evaluation
        results = evaluate(
            test_cases=llm_test_cases,
            metrics=metrics,
        )
        
        return {
            "test_cases_count": len(test_cases),
            "results": results,
            "detailed_results": [
                {
                    "image_file": case["image_file"],
                    "expected": case["expected_answer"],
                    "actual": output,
                    "test_case": llm_case
                }
                for case, output, llm_case in zip(test_cases, actual_outputs, llm_test_cases)
            ]
        }


# Pytest integration for parallel execution
@pytest.mark.asyncio
@pytest.mark.parametrize("case_index", range(30))  # Adjust range based on your test cases
async def test_individual_math_problem(case_index):
    """Test individual math problem - designed for parallel execution"""
    evaluator = MathSolverEvaluator()
    
    # Load all test cases
    test_cases = await evaluator.load_test_cases()
    
    # Skip if case_index is beyond available test cases
    if case_index >= len(test_cases):
        pytest.skip(f"Test case {case_index} not available (only {len(test_cases)} cases)")
    
    case = test_cases[case_index]
    
    # Solve the math problem
    actual_output = await evaluator.solve_math_problem(case["image_file"])
    
    # Create LLM test case
    llm_test_case = LLMTestCase(
        input=f"Math problem from image: {case['image_file']}",
        actual_output=actual_output,
        expected_output=case["expected_answer"],
        context=[f"Mathematical problem solving from image {case['image_file']}"]
    )
    
    # Get metrics
    metrics = evaluator.get_metrics()
    
    # Use DeepEval's assert_test for individual case evaluation
    from deepeval import assert_test
    
    try:
        assert_test(llm_test_case, metrics)
        print(f"✅ Case {case_index}: {os.path.basename(case['image_file'])} - PASSED")
        print(f"   Expected: {case['expected_answer']}")
        print(f"   Actual: {actual_output}")
    except AssertionError as e:
        print(f"❌ Case {case_index}: {os.path.basename(case['image_file'])} - FAILED")
        print(f"   Expected: {case['expected_answer']}")
        print(f"   Actual: {actual_output}")
        print(f"   Error: {str(e)}")
        # Re-raise to mark test as failed
        raise


@pytest.mark.asyncio
async def test_math_solver_evaluation():
    """Test math solver using DeepEval metrics - sequential version"""
    evaluator = MathSolverEvaluator()
    
    # Run evaluation on first 5 test cases for quick testing
    results = await evaluator.run_evaluation(max_cases=5)
    
    assert results["test_cases_count"] > 0
    assert "results" in results
    
    # Print results for debugging
    print("\n" + "="*50)
    print("MATH SOLVER EVALUATION RESULTS")
    print("="*50)
    
    for detail in results["detailed_results"]:
        print(f"\nImage: {detail['image_file']}")
        print(f"Expected: {detail['expected']}")
        print(f"Actual: {detail['actual']}")
        print("-" * 30)


@pytest.mark.asyncio
async def test_full_math_solver_evaluation():
    """Test math solver on all available test cases"""
    evaluator = MathSolverEvaluator()
    
    # Run evaluation on all test cases
    results = await evaluator.run_evaluation()
    
    assert results["test_cases_count"] > 0
    
    # Generate detailed report
    print("\n" + "="*70)
    print("COMPREHENSIVE MATH SOLVER EVALUATION RESULTS")
    print("="*70)
    
    total_cases = results["test_cases_count"]
    print(f"Total test cases: {total_cases}")
    
    # Calculate accuracy
    correct_answers = 0
    for detail in results["detailed_results"]:
        expected = detail["expected"].strip().lower()
        actual = detail["actual"].strip().lower()
        if expected == actual or expected in actual:
            correct_answers += 1
    
    accuracy = (correct_answers / total_cases) * 100 if total_cases > 0 else 0
    print(f"Basic accuracy: {accuracy:.2f}% ({correct_answers}/{total_cases})")
    
    print("\nDetailed Results:")
    print("-" * 70)
    
    for i, detail in enumerate(results["detailed_results"], 1):
        status = "✓" if detail["expected"].strip().lower() in detail["actual"].strip().lower() else "✗"
        print(f"{i:2d}. {status} {os.path.basename(detail['image_file'])}")
        print(f"    Expected: {detail['expected']}")
        print(f"    Actual:   {detail['actual']}")
        print()


if __name__ == "__main__":
    # Run evaluation directly
    async def main():
        evaluator = MathSolverEvaluator()
        results = await evaluator.run_evaluation(max_cases=10)  # Test with 10 cases
        
        print("\nEvaluation completed!")
        print(f"Processed {results['test_cases_count']} test cases")
    
    asyncio.run(main())
