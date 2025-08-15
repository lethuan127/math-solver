# Development Guide

## Setup Development Environment

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Firebase project with Firestore and Authentication enabled
- OpenAI API key

### Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd src/backend
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Create environment configuration:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_service_account_private_key
FIREBASE_CLIENT_EMAIL=your_service_account_email
FIREBASE_STORAGE_BUCKET=your_storage_bucket

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Development Settings
DEBUG=true
ENVIRONMENT=development
```

## Project Structure

```
src/backend/app/
├── modules/                    # Feature modules
│   ├── auth/                  # Authentication module
│   │   ├── domain/            # Domain layer
│   │   └── infrastructure/    # Infrastructure layer
│   ├── math_solving/          # Math solving module
│   │   ├── domain/            # Domain entities & interfaces
│   │   ├── application/       # Use cases & DTOs
│   │   ├── infrastructure/    # External services & repositories
│   │   └── presentation/      # API endpoints
│   └── shared/                # Shared components
│       ├── config.py          # Configuration management
│       ├── utils.py           # Utility functions
│       ├── container.py       # Dependency injection
│       └── database/          # Database clients
├── tests/                     # Test suites
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── evaluation/            # AI evaluation tests
├── docs/                      # Documentation
└── main_new.py               # New modular application entry point
```

## Architecture Principles

### Clean Architecture

The backend follows Clean Architecture principles:

1. **Domain Layer**: Contains business entities and interfaces (ports)
2. **Application Layer**: Contains use cases and application logic
3. **Infrastructure Layer**: Contains external service implementations
4. **Presentation Layer**: Contains API endpoints and controllers

### Dependency Injection

The system uses a dependency injection container (`shared/container.py`) to manage dependencies and improve testability.

### Feature-Based Modules

Code is organized by business features rather than technical layers, making it easier to understand and maintain.

## Running the Application

### Development Server

```bash
# Using uvicorn directly
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Using the Makefile (if available)
make dev

# Background process
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
```

### Production Server

```bash
# Without reload
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# With gunicorn (recommended for production)
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Development Workflow

### Code Quality Tools

The project uses several tools to maintain code quality:

#### Formatting
```bash
# Format code with Black
uv run black app/

# Check formatting
uv run black --check app/
```

#### Linting
```bash
# Lint with Ruff
uv run ruff check app/

# Fix auto-fixable issues
uv run ruff check --fix app/
```

#### Type Checking
```bash
# Type check with MyPy
uv run mypy app/
```

#### All Quality Checks
```bash
# Run all checks
uv run black --check app/ && uv run ruff check app/ && uv run mypy app/
```

### Testing

#### Unit Tests
```bash
# Run unit tests
uv run pytest tests/unit/ -v

# Run with coverage
uv run pytest tests/unit/ --cov=app --cov-report=html
```

#### Integration Tests
```bash
# Run integration tests
uv run pytest tests/integration/ -v
```

#### All Tests
```bash
# Run all tests
uv run pytest -v

# Run with coverage report
uv run pytest --cov=app --cov-report=html --cov-report=term
```

#### AI Evaluation Tests
```bash
# Run AI evaluation (requires OpenAI API key)
uv run pytest tests/evaluation/ -v

# Run evaluation with custom parameters
uv run python tests/evaluation/run_evaluation.py --max-cases 5
```

## Adding New Features

### Creating a New Module

1. Create the module directory structure:
```bash
mkdir -p app/modules/new_feature/{domain,application,infrastructure,presentation}
```

2. Create the domain layer:
```python
# app/modules/new_feature/domain/entities.py
from dataclasses import dataclass

@dataclass
class NewEntity:
    id: str
    name: str
```

```python
# app/modules/new_feature/domain/interfaces.py
from abc import ABC, abstractmethod

class NewRepository(ABC):
    @abstractmethod
    async def save(self, entity: NewEntity) -> str:
        pass
```

3. Create the application layer:
```python
# app/modules/new_feature/application/use_cases.py
class NewUseCase:
    def __init__(self, repository: NewRepository):
        self.repository = repository
    
    async def execute(self, data: dict) -> NewEntity:
        # Implementation
        pass
```

4. Create the infrastructure layer:
```python
# app/modules/new_feature/infrastructure/repository.py
class NewRepositoryImpl(NewRepository):
    async def save(self, entity: NewEntity) -> str:
        # Implementation
        pass
```

5. Create the presentation layer:
```python
# app/modules/new_feature/presentation/endpoints.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/new-endpoint")
async def new_endpoint():
    # Implementation
    pass
```

6. Register in the dependency container:
```python
# app/modules/shared/container.py
def new_repository(self) -> NewRepository:
    return NewRepositoryImpl()

def new_use_case(self) -> NewUseCase:
    return NewUseCase(self.new_repository())
```

7. Include the router in the main app:
```python
# app/main_new.py
from .modules.new_feature.presentation.endpoints import router as new_router

app.include_router(new_router, prefix="/api/v1", tags=["New Feature"])
```

### Adding New Endpoints

1. Define DTOs in `application/dto.py`
2. Implement use case in `application/use_cases.py`
3. Create endpoint in `presentation/endpoints.py`
4. Add tests in `tests/unit/` and `tests/integration/`

## Debugging

### Logging

The application uses Python's built-in logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Info message")
logger.error("Error message")
logger.debug("Debug message")  # Only shown when DEBUG=true
```

### Interactive Debugging

Use the interactive API docs at `http://localhost:8000/docs` to test endpoints.

### Database Debugging

Check Firebase console for Firestore data and authentication logs.

## Common Issues

### Import Errors

If you encounter import errors, ensure you're running commands from the backend directory and using `uv run`.

### Firebase Connection Issues

1. Verify environment variables are set correctly
2. Check Firebase service account permissions
3. Ensure Firestore and Authentication are enabled

### OpenAI API Issues

1. Verify API key is valid and has sufficient credits
2. Check API rate limits
3. Monitor usage in OpenAI dashboard

## Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```bash
uv run pre-commit install
```

This will run formatting, linting, and type checking before each commit.

## Performance Monitoring

### Profiling

Use cProfile for performance profiling:

```bash
uv run python -m cProfile -o profile.stats -m uvicorn app.main:app
```

### Monitoring

Consider integrating monitoring tools like:
- Sentry for error tracking
- Prometheus for metrics
- Grafana for visualization

## Contributing

1. Follow the existing architecture patterns
2. Write comprehensive tests
3. Update documentation
4. Ensure all quality checks pass
5. Use meaningful commit messages following conventional commits

## Deployment

See the [Deployment Guide](deployment.md) for production deployment instructions.
