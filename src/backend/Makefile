.PHONY: lint format check test install clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  lint     - Run all linting and formatting tools"
	@echo "  format   - Format code with black"
	@echo "  check    - Check code with ruff"
	@echo "  test     - Run tests"
	@echo "  install  - Install dependencies"
	@echo "  clean    - Clean cache files"

# Install dependencies
install:
	uv sync --dev

# Format code with black
format:
	uv run black app/ tests/

# Check code with ruff
check:
	uv run ruff check app/ tests/

# Fix linting issues
fix:
	uv run ruff check app/ tests/ --fix

# Run all linting and formatting
lint: fix format
	@echo "✅ Linting complete!"
	uv run ruff check app/ tests/
	uv run black --check app/ tests/

# Run tests
test:
	uv run pytest

# Type checking with mypy
typecheck:
	uv run mypy app/ --ignore-missing-imports

# Full check (lint + typecheck + test)
full-check: lint typecheck test
	@echo "🎉 All checks passed!"

# Clean cache files
clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name ".ruff_cache" -delete
