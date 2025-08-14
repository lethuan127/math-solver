# Code Quality & Linting Setup

This document describes the linting and code quality tools configured for the backend project.

## Tools Used

### 🔍 Ruff
- **Purpose**: Fast Python linter and formatter (replaces flake8, isort, and more)
- **Configuration**: Configured in `pyproject.toml`
- **Features**: 
  - Code style checking (PEP 8)
  - Import sorting
  - Bug detection
  - Code modernization (pyupgrade)
  - Automatic fixes for many issues

### 🎨 Black
- **Purpose**: Uncompromising Python code formatter
- **Configuration**: Configured in `pyproject.toml`
- **Features**: Consistent code formatting across the entire codebase

### 🔧 MyPy
- **Purpose**: Static type checker for Python
- **Configuration**: Configured in `pyproject.toml`
- **Features**: Type checking, improved code reliability

### ⚡ Pre-commit
- **Purpose**: Git hooks for code quality
- **Configuration**: `.pre-commit-config.yaml`
- **Features**: Runs linting tools before each commit

## Quick Commands

### Using Make (Recommended)

```bash
# Run all linting and formatting
make lint

# Format code only
make format

# Check code only (no fixes)
make check

# Fix linting issues
make fix

# Run type checking
make typecheck

# Run all checks (lint + typecheck + tests)
make full-check

# Clean cache files
make clean

# Show help
make help
```

### Using UV directly

```bash
# Install dependencies
uv sync --dev

# Run ruff linter with fixes
uv run ruff check app/ tests/ --fix

# Format with black
uv run black app/ tests/

# Check formatting
uv run black --check app/ tests/

# Type checking
uv run mypy app/ --ignore-missing-imports

# Run tests
uv run pytest
```

## Configuration Details

### Ruff Configuration
Located in `pyproject.toml`:
- Target Python version: 3.11
- Line length: 88 characters
- Enabled rules: pycodestyle, pyflakes, isort, flake8-bugbear, flake8-comprehensions, pyupgrade
- Automatic import sorting
- Exception handling improvements

### Black Configuration
Located in `pyproject.toml`:
- Line length: 88 characters
- Target Python version: 3.11
- Standard exclusions for build/cache directories

### MyPy Configuration
Located in `pyproject.toml`:
- Strict type checking enabled
- Ignores missing imports for third-party libraries
- Comprehensive type checking rules

## Pre-commit Hooks

To set up pre-commit hooks:

```bash
# Install pre-commit
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files
```

## IDE Integration

### VS Code
Add to your `settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm
1. Install the "Ruff" plugin
2. Configure Black as the code formatter
3. Enable format on save

## Continuous Integration

The linting tools should be run in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Lint code
  run: |
    uv run ruff check app/ tests/
    uv run black --check app/ tests/
    uv run mypy app/ --ignore-missing-imports
```

## Common Issues & Solutions

### Import Sorting
Ruff automatically sorts imports according to PEP 8 standards. If you see import sorting errors, run:
```bash
uv run ruff check app/ tests/ --fix
```

### Line Length
Both Ruff and Black are configured for 88-character lines. Long lines will be automatically wrapped by Black.

### Type Annotations
Use modern Python type annotations:
- Use `list[str]` instead of `List[str]`
- Use `dict[str, Any]` instead of `Dict[str, Any]`
- Use `str | None` instead of `Optional[str]`

### Exception Handling
Always use `raise ... from e` in exception handlers to preserve the original traceback:
```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise CustomException("Operation failed") from e
```

## Excluding Files

To exclude files from linting, add them to the `extend-exclude` section in `pyproject.toml`:

```toml
[tool.ruff]
extend-exclude = ["migrations/", "generated/"]
```

## Performance

- **Ruff**: Extremely fast (written in Rust)
- **Black**: Fast formatting
- **MyPy**: Can be slow on large codebases, consider using `--incremental`

## Getting Help

- Ruff documentation: https://docs.astral.sh/ruff/
- Black documentation: https://black.readthedocs.io/
- MyPy documentation: https://mypy.readthedocs.io/
