#!/usr/bin/env python3
"""
Test runner for the modular Math Solver backend.

This script provides convenient commands to run different types of tests:
- Unit tests (per module)
- Integration tests
- Evaluation tests
- All tests

Usage:
    python tests/run_tests.py unit                    # Run all unit tests
    python tests/run_tests.py unit auth               # Run auth module unit tests
    python tests/run_tests.py unit math_solving       # Run math solving unit tests
    python tests/run_tests.py unit shared             # Run shared module unit tests
    python tests/run_tests.py integration             # Run integration tests
    python tests/run_tests.py evaluation              # Run evaluation tests
    python tests/run_tests.py all                     # Run all tests
    python tests/run_tests.py coverage                # Run with coverage report
    python tests/run_tests.py fast                    # Run fast tests only
    python tests/run_tests.py lint                    # Run linting checks
    python tests/run_tests.py format                  # Format code
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)
    return result.returncode


def run_unit_tests(module: str = None) -> int:
    """Run unit tests for a specific module or all modules."""
    if module:
        if module not in ["auth", "math_solving", "shared"]:
            print(f"❌ Invalid module: {module}")
            print("Available modules: auth, math_solving, shared")
            return 1

        test_path = f"app/modules/{module}/tests"
        description = f"Unit tests for {module} module"
    else:
        test_path = "app/modules/*/tests"
        description = "All unit tests"

    cmd = ["uv", "run", "pytest", test_path, "-m", "unit or not slow", "-v"]
    return run_command(cmd, description)


def run_integration_tests() -> int:
    """Run integration tests."""
    cmd = ["uv", "run", "pytest", "tests/integration", "-m", "integration", "-v"]
    return run_command(cmd, "Integration tests")


def run_evaluation_tests() -> int:
    """Run evaluation tests."""
    cmd = [
        "uv",
        "run",
        "pytest",
        "app/modules/math_solving/evaluation",
        "-m",
        "evaluation",
        "-v",
    ]
    return run_command(cmd, "Evaluation tests")


def run_all_tests() -> int:
    """Run all tests."""
    cmd = ["uv", "run", "pytest", "-v"]
    return run_command(cmd, "All tests")


def run_with_coverage() -> int:
    """Run tests with coverage report."""
    cmd = [
        "uv",
        "run",
        "pytest",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "-v",
    ]
    return run_command(cmd, "Tests with coverage")


def run_fast_tests() -> int:
    """Run only fast tests (excluding slow and evaluation tests)."""
    cmd = ["uv", "run", "pytest", "-m", "not slow and not evaluation", "-v"]
    return run_command(cmd, "Fast tests only")


def run_specific_test(test_path: str) -> int:
    """Run a specific test file or test function."""
    cmd = ["uv", "run", "pytest", test_path, "-v"]
    return run_command(cmd, f"Specific test: {test_path}")


def run_lint() -> int:
    """Run linting checks."""
    commands = [
        (["uv", "run", "ruff", "check", "app/"], "Ruff linting"),
        (["uv", "run", "mypy", "app/"], "MyPy type checking"),
    ]

    exit_code = 0
    for cmd, description in commands:
        result = run_command(cmd, description)
        if result != 0:
            exit_code = result

    return exit_code


def run_format() -> int:
    """Format code."""
    commands = [
        (["uv", "run", "black", "app/", "tests/"], "Black formatting"),
        (["uv", "run", "ruff", "check", "--fix", "app/", "tests/"], "Ruff auto-fix"),
    ]

    exit_code = 0
    for cmd, description in commands:
        result = run_command(cmd, description)
        if result != 0:
            exit_code = result

    return exit_code


def run_check() -> int:
    """Run all checks (lint + fast tests)."""
    print(f"\n{'='*60}")
    print("🔍 Running comprehensive checks")
    print(f"{'='*60}")

    # Run linting first
    lint_result = run_lint()
    if lint_result != 0:
        print("❌ Linting failed, skipping tests")
        return lint_result

    # Run fast tests
    fast_result = run_fast_tests()

    return fast_result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced test runner for Math Solver backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "command",
        choices=[
            "unit",
            "integration",
            "evaluation",
            "all",
            "coverage",
            "fast",
            "specific",
            "lint",
            "format",
            "check",
        ],
        help="Type of tests to run",
    )

    parser.add_argument(
        "target",
        nargs="?",
        help="Specific module for unit tests or test path for specific tests",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--no-cov", action="store_true", help="Disable coverage for faster execution"
    )

    args = parser.parse_args()

    # Change to the backend directory
    backend_dir = Path(__file__).parent.parent
    import os

    os.chdir(backend_dir)

    exit_code = 0

    try:
        if args.command == "unit":
            exit_code = run_unit_tests(args.target)
        elif args.command == "integration":
            exit_code = run_integration_tests()
        elif args.command == "evaluation":
            exit_code = run_evaluation_tests()
        elif args.command == "all":
            exit_code = run_all_tests()
        elif args.command == "coverage":
            exit_code = run_with_coverage()
        elif args.command == "fast":
            exit_code = run_fast_tests()
        elif args.command == "specific":
            if not args.target:
                print("❌ Please specify a test path for specific tests")
                return 1
            exit_code = run_specific_test(args.target)
        elif args.command == "lint":
            exit_code = run_lint()
        elif args.command == "format":
            exit_code = run_format()
        elif args.command == "check":
            exit_code = run_check()

    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1

    # Print summary
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*60}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
