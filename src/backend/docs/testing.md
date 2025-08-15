# Testing Guide

## Overview

The Math Solver backend uses a comprehensive testing strategy with tests organized by the modular architecture. Tests are categorized into three main types:

- **Unit Tests**: Located within each module, test individual components in isolation
- **Integration Tests**: Located at the root level, test API endpoints and cross-module interactions
- **Evaluation Tests**: Located within the math_solving module, test AI model performance

## Test Structure

```
src/backend/
├── app/modules/
│   ├── auth/tests/                    # Auth module unit tests
│   │   ├── conftest.py               # Auth-specific fixtures
│   │   ├── test_entities.py          # Domain entity tests
│   │   └── test_firebase_auth_service.py  # Auth service tests
│   ├── math_solving/tests/           # Math solving unit tests
│   │   ├── conftest.py               # Math solving fixtures
│   │   ├── test_entities.py          # Domain entity tests
│   │   ├── test_use_cases.py         # Use case tests
│   │   └── test_ai_service.py        # AI service tests
│   ├── math_solving/evaluation/      # AI evaluation tests
│   │   ├── test_math_solver_deepeval.py  # DeepEval tests
│   │   ├── metrics.py                # Custom evaluation metrics
│   │   └── usecases/                 # Test cases and images
│   └── shared/tests/                 # Shared component tests
│       ├── test_container.py         # Dependency injection tests
│       └── test_config.py            # Configuration tests
├── tests/integration/                # Integration tests
│   └── test_api_endpoints.py         # API endpoint tests
└── tests/
    ├── conftest.py                   # Global test configuration
    └── run_tests_new.py              # Enhanced test runner
```

## Running Tests

### Using the Enhanced Test Runner

The enhanced test runner provides convenient commands for different test scenarios:

```bash
# Run all unit tests
python tests/run_tests.py unit

# Run unit tests for specific module
python tests/run_tests.py unit auth
python tests/run_tests.py unit math_solving
python tests/run_tests.py unit shared

# Run integration tests
python tests/run_tests.py integration

# Run evaluation tests
python tests/run_tests.py evaluation

# Run all tests
python tests/run_tests.py all

# Run tests with coverage
python tests/run_tests.py coverage

# Run only fast tests (exclude slow/evaluation)
python tests/run_tests.py fast

# Code quality checks
python tests/run_tests.py lint        # Run linting
python tests/run_tests.py format      # Format code
python tests/run_tests.py check       # Run lint + fast tests

# Run specific test file
python tests/run_tests.py specific app/modules/auth/tests/test_entities.py
```

### Using pytest Directly

```bash
# Run all tests
uv run pytest

# Run unit tests for specific module
uv run pytest app/modules/auth/tests/ -v
uv run pytest app/modules/math_solving/tests/ -v

# Run integration tests
uv run pytest tests/integration/ -v

# Run evaluation tests
uv run pytest app/modules/math_solving/evaluation/ -v

# Run tests with markers
uv run pytest -m "unit" -v
uv run pytest -m "integration" -v
uv run pytest -m "evaluation" -v

# Run tests with coverage
uv run pytest --cov=app --cov-report=html --cov-report=term-missing
```

## Test Categories

### Unit Tests

Unit tests are located within each module and test individual components in isolation.

#### Auth Module Tests (`app/modules/auth/tests/`)

- **test_entities.py**: Tests for User domain entity
- **test_firebase_auth_service.py**: Tests for Firebase authentication service

#### Math Solving Module Tests (`app/modules/math_solving/tests/`)

- **test_entities.py**: Tests for domain entities (MathProblem, MathAnswer, SolutionStep)
- **test_use_cases.py**: Tests for application use cases
- **test_ai_service.py**: Tests for OpenAI integration service

#### Shared Module Tests (`app/modules/shared/tests/`)

- **test_container.py**: Tests for dependency injection container
- **test_config.py**: Tests for configuration management

### Integration Tests

Integration tests are located at `tests/integration/` and test the complete API functionality.

- **test_api_endpoints.py**: Tests for FastAPI endpoints with proper mocking

### Evaluation Tests

Evaluation tests are located at `app/modules/math_solving/evaluation/` and test AI model performance.

- **test_math_solver_deepeval.py**: DeepEval-based performance evaluation
- **metrics.py**: Custom evaluation metrics for mathematical accuracy

## Test Configuration

### Global Configuration (`tests/conftest.py`)

- Sets up test environment variables
- Provides global fixtures for Firebase mocking
- Configures async event loop for tests

### Module-Specific Configuration

Each module has its own `conftest.py` with module-specific fixtures:

- **Auth module**: Mock Firebase client, sample user entities
- **Math solving module**: Mock services, sample domain entities
- **Shared module**: Configuration and container fixtures

### pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests app/modules
markers =
    unit: Unit tests
    integration: Integration tests
    evaluation: Evaluation tests for math solver
    slow: Slow running tests
    requires_openai: Tests that require OpenAI API access
asyncio_mode = auto
```

## Writing Tests

### Unit Test Example

```python
# app/modules/math_solving/tests/test_use_cases.py
import pytest
from unittest.mock import Mock, AsyncMock

from ..application.use_cases import SolveMathProblemUseCase
from ..domain.entities import MathAnswer, User

class TestSolveMathProblemUseCase:
    def setup_method(self):
        self.mock_ai_service = Mock()
        self.mock_repository = Mock()
        self.use_case = SolveMathProblemUseCase(
            ai_service=self.mock_ai_service,
            repository=self.mock_repository
        )

    @pytest.mark.asyncio
    async def test_execute_success(self):
        # Test implementation
        pass
```

### Integration Test Example

```python
# tests/integration/test_api_endpoints.py
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.main import app

client = TestClient(app)

@patch("app.modules.shared.container.container.auth_service")
def test_solve_problem_success(mock_auth_container):
    # Test implementation
    pass
```

### Evaluation Test Example

```python
# app/modules/math_solving/evaluation/test_math_solver_deepeval.py
import pytest
from deepeval import evaluate
from deepeval.test_case import LLMTestCase

@pytest.mark.evaluation
@pytest.mark.requires_openai
@pytest.mark.asyncio
async def test_math_solver_evaluation():
    # DeepEval test implementation
    pass
```

## Test Fixtures

### Common Fixtures

Available in all tests through `app/modules/conftest.py`:

- `sample_user`: Sample user entity
- `sample_math_problem`: Sample math problem data
- `mock_firebase_init`: Mocks Firebase initialization

### Module-Specific Fixtures

#### Auth Module
- `mock_firebase_client`: Mocked Firebase client
- `sample_user`: Auth-specific user entity

#### Math Solving Module
- `sample_solution_step`: Sample solution step
- `sample_math_answer`: Sample math answer
- `sample_math_problem`: Sample math problem
- `mock_ai_service`: Mocked AI service
- `mock_repository`: Mocked repository
- `mock_upload_file`: Mocked file upload

## Mocking Strategy

### External Services

- **Firebase**: Mocked at the client level to avoid real API calls
- **OpenAI**: Mocked at the service level for unit tests
- **File uploads**: Mocked using FastAPI's UploadFile interface

### Dependency Injection

Tests use the dependency injection container to easily swap real implementations with mocks:

```python
@patch("app.modules.shared.container.container.auth_service")
def test_with_mocked_auth(mock_auth_container):
    mock_service = Mock()
    mock_auth_container.return_value = mock_service
    # Test implementation
```

## Coverage

### Running Coverage

```bash
# Generate coverage report
uv run pytest --cov=app --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Coverage Targets

- **Unit Tests**: Aim for >90% coverage of business logic
- **Integration Tests**: Ensure all API endpoints are tested
- **Overall**: Target >85% overall coverage

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Run fast tests
        run: uv run pytest -m "not slow and not evaluation"
      - name: Run evaluation tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: uv run pytest -m "evaluation" --maxfail=1
```

## Best Practices

### Test Organization

1. **Follow the AAA pattern**: Arrange, Act, Assert
2. **Use descriptive test names**: `test_solve_problem_with_invalid_file`
3. **Group related tests in classes**: `TestSolveMathProblemUseCase`
4. **Use fixtures for common setup**: Avoid repetitive setup code

### Mocking Guidelines

1. **Mock external dependencies**: Don't make real API calls in tests
2. **Mock at the right level**: Mock services, not internal methods
3. **Verify interactions**: Assert that mocked methods were called correctly
4. **Use realistic mock data**: Make mocks behave like real services

### Performance

1. **Mark slow tests**: Use `@pytest.mark.slow` for tests that take >1 second
2. **Separate evaluation tests**: Keep AI evaluation tests separate from unit tests
3. **Use fixtures efficiently**: Scope fixtures appropriately (session, module, function)

### Maintenance

1. **Keep tests simple**: Each test should test one thing
2. **Update tests with code changes**: Don't let tests become stale
3. **Review test coverage regularly**: Identify untested code paths
4. **Refactor test code**: Apply same quality standards as production code

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure proper module structure and `__init__.py` files
2. **Async test failures**: Use `@pytest.mark.asyncio` for async tests
3. **Fixture not found**: Check fixture scope and import paths
4. **Mock not working**: Verify mock patch paths match actual imports

### Debug Tips

```bash
# Run with verbose output
uv run pytest -v -s

# Run specific test with debug
uv run pytest path/to/test.py::test_function -v -s --pdb

# Show fixture setup
uv run pytest --fixtures-per-test
```
