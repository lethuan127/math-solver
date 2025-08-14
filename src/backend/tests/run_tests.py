#!/usr/bin/env python3
"""
Test runner script for the Math Homework Solver backend
Usage: python run_tests.py [unit|integration|all]
"""

import argparse
import subprocess
import sys


def run_tests(test_type="all"):
    """Run tests based on the specified type"""

    base_cmd = ["uv", "run", "pytest"]

    if test_type == "unit":
        cmd = base_cmd + ["tests/unit/", "-m", "not integration"]
    elif test_type == "integration":
        cmd = base_cmd + ["tests/integration/", "-m", "not unit"]
    elif test_type == "all":
        cmd = base_cmd + ["tests/"]
    else:
        print(f"Unknown test type: {test_type}")
        return 1

    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=".", capture_output=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run backend tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["unit", "integration", "all"],
        help="Type of tests to run (default: all)",
    )

    args = parser.parse_args()
    exit_code = run_tests(args.test_type)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
