#!/usr/bin/env python3
"""
Standalone script to run DeepEval evaluation of the Math Solver
"""
import argparse
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from tests.evaluation.test_math_solver_deepeval import MathSolverEvaluator


class EvaluationRunner:
    """Runner for math solver evaluation with reporting capabilities"""

    def __init__(self, output_dir: str = "evaluation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.evaluator = MathSolverEvaluator()

    async def run_comprehensive_evaluation(
        self,
        max_cases: int = None,
        save_results: bool = True,
        generate_report: bool = True,
    ) -> dict[str, Any]:
        """Run comprehensive evaluation with detailed reporting"""

        print("🚀 Starting Math Solver Evaluation")
        print("=" * 50)

        start_time = datetime.now()

        try:
            # Run the evaluation
            results = await self.evaluator.run_evaluation(max_cases=max_cases)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Add metadata
            results["metadata"] = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "max_cases": max_cases,
                "total_available_cases": len(results["detailed_results"]),
            }

            # Calculate additional metrics
            results["summary"] = self._calculate_summary_metrics(results)

            if save_results:
                await self._save_results(results)

            if generate_report:
                self._print_evaluation_report(results)

            return results

        except Exception as e:
            print(f"❌ Evaluation failed: {str(e)}")
            raise

    def _calculate_summary_metrics(self, results: dict[str, Any]) -> dict[str, Any]:
        """Calculate summary metrics from detailed results"""
        detailed_results = results["detailed_results"]
        total_cases = len(detailed_results)

        if total_cases == 0:
            return {"error": "No test cases processed"}

        # Basic accuracy calculation
        exact_matches = 0
        partial_matches = 0
        no_matches = 0

        answer_lengths = []
        expected_lengths = []

        for result in detailed_results:
            expected = result["expected"].strip().lower()
            actual = result["actual"].strip().lower()

            answer_lengths.append(len(actual))
            expected_lengths.append(len(expected))

            if expected == actual:
                exact_matches += 1
            elif (
                expected in actual
                or actual in expected
                or self._is_numerically_equivalent(expected, actual)
            ):
                partial_matches += 1
            else:
                no_matches += 1

        return {
            "total_cases": total_cases,
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "no_matches": no_matches,
            "exact_accuracy": (exact_matches / total_cases) * 100,
            "partial_accuracy": ((exact_matches + partial_matches) / total_cases) * 100,
            "average_answer_length": sum(answer_lengths) / len(answer_lengths),
            "average_expected_length": sum(expected_lengths) / len(expected_lengths),
        }

    def _is_numerically_equivalent(self, expected: str, actual: str) -> bool:
        """Check if two strings represent numerically equivalent values"""
        import re

        # Extract numbers from both strings
        expected_nums = re.findall(r"\d+(?:\.\d+)?", expected)
        actual_nums = re.findall(r"\d+(?:\.\d+)?", actual)

        if not expected_nums or not actual_nums:
            return False

        try:
            expected_val = float(expected_nums[0])
            actual_val = float(actual_nums[0])
            return abs(expected_val - actual_val) < 0.01
        except (ValueError, IndexError):
            return False

    async def _save_results(self, results: dict[str, Any]) -> None:
        """Save evaluation results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save full results as JSON
        json_file = self.output_dir / f"evaluation_results_{timestamp}.json"
        with open(json_file, "w") as f:
            # Convert any non-serializable objects to strings
            serializable_results = self._make_serializable(results)
            json.dump(serializable_results, f, indent=2, default=str)

        # Save CSV for easy analysis
        csv_file = self.output_dir / f"evaluation_summary_{timestamp}.csv"
        await self._save_csv_summary(results, csv_file)

        print("📊 Results saved to:")
        print(f"   JSON: {json_file}")
        print(f"   CSV:  {csv_file}")

    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if hasattr(obj, "__dict__"):
            return {k: self._make_serializable(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj

    async def _save_csv_summary(self, results: dict[str, Any], csv_file: Path) -> None:
        """Save results summary as CSV"""
        import csv

        detailed_results = results["detailed_results"]

        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(
                [
                    "Test Case",
                    "Image File",
                    "Expected Answer",
                    "Actual Answer",
                    "Exact Match",
                    "Partial Match",
                    "Answer Length",
                    "Expected Length",
                ]
            )

            # Data rows
            for i, result in enumerate(detailed_results, 1):
                expected = result["expected"].strip()
                actual = result["actual"].strip()

                exact_match = expected.lower() == actual.lower()
                partial_match = (
                    expected.lower() in actual.lower()
                    or actual.lower() in expected.lower()
                    or self._is_numerically_equivalent(expected, actual)
                )

                writer.writerow(
                    [
                        i,
                        os.path.basename(result["image_file"]),
                        expected,
                        actual,
                        exact_match,
                        partial_match,
                        len(actual),
                        len(expected),
                    ]
                )

    def _print_evaluation_report(self, results: dict[str, Any]) -> None:
        """Print detailed evaluation report"""
        summary = results["summary"]
        metadata = results["metadata"]

        print("\n" + "=" * 70)
        print("📋 MATH SOLVER EVALUATION REPORT")
        print("=" * 70)

        # Metadata
        print(f"⏱️  Duration: {metadata['duration_seconds']:.2f} seconds")
        print(f"📊 Test Cases: {summary['total_cases']}")
        print(
            f"🎯 Exact Accuracy: {summary['exact_accuracy']:.1f}% ({summary['exact_matches']}/{summary['total_cases']})"
        )
        print(
            f"🎯 Partial Accuracy: {summary['partial_accuracy']:.1f}% ({summary['exact_matches'] + summary['partial_matches']}/{summary['total_cases']})"
        )

        print("\n📈 DETAILED BREAKDOWN:")
        print(f"   ✅ Exact Matches: {summary['exact_matches']}")
        print(f"   ⚡ Partial Matches: {summary['partial_matches']}")
        print(f"   ❌ No Matches: {summary['no_matches']}")

        print("\n📏 RESPONSE ANALYSIS:")
        print(
            f"   Average Answer Length: {summary['average_answer_length']:.1f} characters"
        )
        print(
            f"   Average Expected Length: {summary['average_expected_length']:.1f} characters"
        )

        # Detailed results
        print("\n🔍 DETAILED RESULTS:")
        print("-" * 70)

        for i, result in enumerate(results["detailed_results"], 1):
            expected = result["expected"]
            actual = result["actual"]
            image_name = os.path.basename(result["image_file"])

            # Determine status
            if expected.strip().lower() == actual.strip().lower():
                status = "✅ EXACT"
            elif (
                expected.strip().lower() in actual.strip().lower()
                or actual.strip().lower() in expected.strip().lower()
                or self._is_numerically_equivalent(expected, actual)
            ):
                status = "⚡ PARTIAL"
            else:
                status = "❌ MISS"

            print(f"{i:2d}. {status} | {image_name}")
            print(f"    Expected: {expected}")
            print(f"    Actual:   {actual}")

            if i < len(results["detailed_results"]):
                print()

        print("=" * 70)


async def main():
    """Main function to run evaluation"""
    parser = argparse.ArgumentParser(description="Run Math Solver DeepEval Evaluation")
    parser.add_argument(
        "--max-cases", type=int, help="Maximum number of test cases to run"
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation_results",
        help="Output directory for results",
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Don't save results to files"
    )
    parser.add_argument(
        "--no-report", action="store_true", help="Don't print detailed report"
    )

    args = parser.parse_args()

    runner = EvaluationRunner(output_dir=args.output_dir)

    try:
        results = await runner.run_comprehensive_evaluation(
            max_cases=args.max_cases,
            save_results=not args.no_save,
            generate_report=not args.no_report,
        )

        print("\n🎉 Evaluation completed successfully!")
        print(f"📊 Final Accuracy: {results['summary']['exact_accuracy']:.1f}%")

        return 0

    except Exception as e:
        print(f"\n💥 Evaluation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
