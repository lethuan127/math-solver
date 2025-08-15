# Test Runner Guide

## Overview

The Math Solver backend includes an enhanced test runner script (`tests/run_tests.py`) that provides convenient commands for running different types of tests and code quality checks.

## Usage

```bash
# Basic syntax
uv run python tests/run_tests.py <command> [target] [options]
```

## Commands

### Test Commands

#### Unit Tests
```bash
# Run all unit tests
uv run python tests/run_tests.py unit

# Run unit tests for specific module
uv run python tests/run_tests.py unit auth
uv run python tests/run_tests.py unit math_solving
uv run python tests/run_tests.py unit shared
```

#### Integration Tests
```bash
# Run all integration tests
uv run python tests/run_tests.py integration
```

#### Evaluation Tests
```bash
# Run AI evaluation tests (requires OpenAI API key)
uv run python tests/run_tests.py evaluation
```

#### All Tests
```bash
# Run all tests
uv run python tests/run_tests.py all
```

#### Coverage Tests
```bash
# Run tests with coverage report
uv run python tests/run_tests.py coverage
```

#### Fast Tests
```bash
# Run only fast tests (exclude slow and evaluation tests)
uv run python tests/run_tests.py fast
```

#### Specific Tests
```bash
# Run specific test file or function
uv run python tests/run_tests.py specific app/modules/auth/tests/test_entities.py
uv run python tests/run_tests.py specific app/modules/auth/tests/test_entities.py::TestUser::test_user_creation
```

### Code Quality Commands

#### Linting
```bash
# Run linting checks (Ruff + MyPy)
uv run python tests/run_tests.py lint
```

#### Formatting
```bash
# Format code with Black and auto-fix with Ruff
uv run python tests/run_tests.py format
```

#### Comprehensive Check
```bash
# Run linting + fast tests
uv run python tests/run_tests.py check
```

## Options

- `--verbose, -v`: Enable verbose output
- `--no-cov`: Disable coverage for faster execution

## Examples

### Development Workflow

```bash
# 1. Format code before committing
uv run python tests/run_tests.py format

# 2. Run comprehensive checks
uv run python tests/run_tests.py check

# 3. Run specific module tests during development
uv run python tests/run_tests.py unit math_solving

# 4. Run all tests before pushing
uv run python tests/run_tests.py all
```

### CI/CD Workflow

```bash
# Fast feedback loop
uv run python tests/run_tests.py fast

# Full test suite (including evaluation)
uv run python tests/run_tests.py all

# With coverage reporting
uv run python tests/run_tests.py coverage
```

## Output

The test runner provides colored output with clear section headers:

```
============================================================
🧪 Unit tests for auth module
============================================================
Running: uv run pytest app/modules/auth/tests -m unit or not slow -v

... test output ...

============================================================
✅ All tests passed!
============================================================
```

## Exit Codes

- `0`: All tests/checks passed
- `1`: Some tests failed or checks failed
- `2`: Error in test execution

## Integration with IDEs

### VS Code

Add to your VS Code settings:

```json
{
    "python.testing.pytestArgs": [
        "app/modules",
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}
```

### PyCharm

Configure PyCharm to use pytest with the following test roots:
- `app/modules`
- `tests`

## Troubleshooting

### Common Issues

1. **Module not found errors**: Ensure you're running from the backend directory
2. **Import errors**: Check that all `__init__.py` files exist
3. **Test discovery issues**: Verify pytest.ini configuration

### Debug Mode

Run with verbose output for debugging:

```bash
uv run python tests/run_tests.py unit auth --verbose
```

### Manual pytest Commands

If the test runner has issues, you can run pytest directly:

```bash
# All tests
uv run pytest

# Specific module
uv run pytest app/modules/auth/tests/ -v

# With markers
uv run pytest -m "unit" -v
uv run pytest -m "not slow and not evaluation" -v
```

## Performance Tips

1. **Use fast tests during development**: `uv run python tests/run_tests.py fast`
2. **Run specific modules**: Target the module you're working on
3. **Skip evaluation tests**: They require API calls and are slower
4. **Use --no-cov**: Disable coverage for faster execution during development

## Best Practices

1. **Run checks before committing**: Use `check` command
2. **Format code regularly**: Use `format` command
3. **Test specific modules during development**: Focus on what you're changing
4. **Run full suite before releases**: Use `all` command
5. **Monitor coverage**: Use `coverage` command periodically
