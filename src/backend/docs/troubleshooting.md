# Troubleshooting Guide

## Common Issues and Solutions

### Development Environment Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError` or import-related errors

**Solutions**:
```bash
# Ensure you're in the backend directory
cd src/backend

# Use uv to run commands
uv run python -m app.main

# Check if modules are properly installed
uv sync

# Verify Python path
uv run python -c "import sys; print(sys.path)"
```

#### 2. Environment Variables Not Loading

**Problem**: Configuration values are empty or default

**Solutions**:
```bash
# Check if .env file exists
ls -la .env

# Verify environment variables are set
uv run python -c "import os; print(os.getenv('FIREBASE_PROJECT_ID'))"

# Load environment manually in Python
from dotenv import load_dotenv
load_dotenv()
```

#### 3. Firebase Connection Issues

**Problem**: Firebase authentication or database connection fails

**Solutions**:
```bash
# Verify Firebase configuration
uv run python -c "
from app.modules.shared.config import get_settings
settings = get_settings()
print('Project ID:', settings.firebase_project_id)
print('Client Email:', settings.firebase_client_email)
"

# Check Firebase service account permissions
# - Ensure service account has required roles
# - Verify private key format (should have \n for line breaks)
# - Check if Firestore and Authentication are enabled
```

**Common Firebase Errors**:
- `DefaultCredentialsError`: Service account credentials not properly configured
- `PermissionDenied`: Insufficient permissions for service account
- `NotFound`: Firebase project or collection doesn't exist

#### 4. OpenAI API Issues

**Problem**: OpenAI API calls fail or return errors

**Solutions**:
```bash
# Verify API key
uv run python -c "
from app.modules.shared.config import get_settings
settings = get_settings()
print('API Key set:', bool(settings.openai_api_key))
print('Key prefix:', settings.openai_api_key[:10] if settings.openai_api_key else 'None')
"

# Test API connection
uv run python -c "
import openai
from app.modules.shared.config import get_settings
client = openai.OpenAI(api_key=get_settings().openai_api_key)
try:
    models = client.models.list()
    print('OpenAI connection successful')
except Exception as e:
    print('OpenAI error:', e)
"
```

**Common OpenAI Errors**:
- `AuthenticationError`: Invalid API key
- `RateLimitError`: API rate limit exceeded
- `InsufficientQuotaError`: No credits remaining
- `APIError`: General API error

### Runtime Issues

#### 1. Server Won't Start

**Problem**: FastAPI server fails to start

**Solutions**:
```bash
# Check if port is already in use
lsof -i :8000

# Kill process using the port
kill -9 $(lsof -t -i :8000)

# Start with different port
uv run uvicorn app.main_new:app --port 8001

# Check for syntax errors
uv run python -m py_compile app/main_new.py
```

#### 2. 500 Internal Server Error

**Problem**: API endpoints return 500 errors

**Solutions**:
1. **Check server logs**:
```bash
# If running with uvicorn
uv run uvicorn app.main_new:app --log-level debug

# Check application logs
tail -f app.log
```

2. **Common causes**:
- Missing environment variables
- Database connection issues
- Invalid API keys
- Code errors in business logic

3. **Debug with interactive mode**:
```bash
# Start Python REPL and test components
uv run python
>>> from app.modules.shared.container import container
>>> auth_service = container.auth_service()
>>> # Test individual components
```

#### 3. Authentication Failures

**Problem**: 401 Unauthorized errors

**Solutions**:
1. **Verify token format**:
```bash
# Test with curl
curl -X POST "http://localhost:8000/api/v1/solve" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -F "file=@test_image.png"
```

2. **Check Firebase token**:
- Ensure token is not expired
- Verify token is from correct Firebase project
- Check if user exists in Firebase Authentication

3. **Debug authentication service**:
```python
# Test token verification
from app.modules.auth.infrastructure.firebase_auth_service import FirebaseAuthenticationService
service = FirebaseAuthenticationService()
result = await service.verify_token("your_token_here")
print(result)
```

#### 4. File Upload Issues

**Problem**: File uploads fail or return errors

**Solutions**:
1. **Check file size limits**:
```python
# In FastAPI, default limit is 16MB
# Check if file is too large
```

2. **Verify file format**:
```python
# Supported formats: PNG, JPG, JPEG
import mimetypes
print(mimetypes.guess_type("your_file.png"))
```

3. **Debug file processing**:
```python
# Test file reading
async def test_file(file):
    content = await file.read()
    print(f"File size: {len(content)} bytes")
    print(f"Content type: {file.content_type}")
```

### Testing Issues

#### 1. Tests Fail to Run

**Problem**: pytest fails to discover or run tests

**Solutions**:
```bash
# Run from backend directory
cd src/backend

# Check test discovery
uv run pytest --collect-only

# Run specific test file
uv run pytest tests/unit/test_math_solver.py -v

# Check for missing dependencies
uv sync
```

#### 2. Integration Tests Fail

**Problem**: Integration tests fail due to external dependencies

**Solutions**:
1. **Mock external services**:
```python
# Use pytest fixtures to mock Firebase and OpenAI
@pytest.fixture
def mock_firebase():
    # Mock implementation
    pass
```

2. **Use test configuration**:
```python
# Create test-specific settings
class TestSettings(Settings):
    environment = "test"
    debug = True
```

#### 3. AI Evaluation Tests Fail

**Problem**: DeepEval tests fail or timeout

**Solutions**:
```bash
# Check OpenAI API key for evaluation
export OPENAI_API_KEY=your_key

# Run with fewer test cases
uv run python tests/evaluation/run_evaluation.py --max-cases 5

# Check test case files exist
ls tests/evaluation/usecases/
```

### Deployment Issues

#### 1. Docker Build Failures

**Problem**: Docker image build fails

**Solutions**:
```bash
# Check Dockerfile syntax
docker build --no-cache -t math-solver-backend .

# Build with verbose output
docker build --progress=plain -t math-solver-backend .

# Check base image compatibility
docker pull python:3.11-slim
```

#### 2. Container Runtime Issues

**Problem**: Container starts but application doesn't work

**Solutions**:
```bash
# Check container logs
docker logs math-solver-backend

# Access container shell
docker exec -it math-solver-backend /bin/bash

# Check environment variables in container
docker exec math-solver-backend env

# Test health endpoint
curl http://localhost:8000/health
```

#### 3. Cloud Deployment Issues

**Problem**: Deployment to cloud platforms fails

**Solutions**:

**Google Cloud Run**:
```bash
# Check service logs
gcloud logging read "resource.type=cloud_run_revision"

# Check service configuration
gcloud run services describe math-solver-backend --region=us-central1
```

**AWS ECS**:
```bash
# Check task logs
aws logs describe-log-groups
aws logs get-log-events --log-group-name /ecs/math-solver-backend
```

### Performance Issues

#### 1. Slow API Responses

**Problem**: API endpoints are slow

**Solutions**:
1. **Profile the application**:
```python
import cProfile
import pstats

# Profile a specific function
profiler = cProfile.Profile()
profiler.enable()
# Your code here
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)
```

2. **Check external service latency**:
- Firebase response times
- OpenAI API response times
- Network connectivity

3. **Optimize database queries**:
- Use Firestore query optimization
- Implement caching where appropriate

#### 2. Memory Issues

**Problem**: High memory usage or out-of-memory errors

**Solutions**:
```bash
# Monitor memory usage
docker stats math-solver-backend

# Check for memory leaks
uv run python -m memory_profiler app/main_new.py
```

### Security Issues

#### 1. CORS Errors

**Problem**: Frontend can't access API due to CORS

**Solutions**:
```python
# Update CORS settings in config
allowed_origins = [
    "http://localhost:3000",
    "https://yourdomain.com"
]

# Check CORS headers in response
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS http://localhost:8000/api/v1/solve
```

#### 2. Authentication Token Issues

**Problem**: Tokens are rejected or expire quickly

**Solutions**:
1. **Check token expiration**:
```javascript
// In frontend, refresh token before expiration
const user = firebase.auth().currentUser;
if (user) {
    const token = await user.getIdToken(true); // Force refresh
}
```

2. **Verify token claims**:
```python
# Check token contents
import firebase_admin.auth as auth
decoded_token = auth.verify_id_token(token)
print(decoded_token)
```

### Database Issues

#### 1. Firestore Permission Denied

**Problem**: Database operations fail with permission errors

**Solutions**:
1. **Check Firestore security rules**:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/solutions/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

2. **Verify service account permissions**:
- Firebase Admin SDK Service Agent
- Cloud Datastore User

#### 2. Data Not Persisting

**Problem**: Data is not saved to Firestore

**Solutions**:
```python
# Debug database operations
from app.modules.shared.database.firebase_client import FirebaseClient
client = FirebaseClient()

# Test connection
try:
    test_doc = client.db.collection('test').document('test')
    test_doc.set({'test': True})
    print('Database connection successful')
except Exception as e:
    print('Database error:', e)
```

## Debugging Tools and Techniques

### Logging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add request logging
import uvicorn
uvicorn.run(app, log_level="debug")
```

### Interactive Debugging

Use Python debugger:
```python
import pdb; pdb.set_trace()  # Set breakpoint
# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

### Health Checks

Create comprehensive health checks:
```python
@app.get("/health/detailed")
async def detailed_health():
    health_status = {
        "api": "healthy",
        "database": "unknown",
        "ai_service": "unknown"
    }
    
    # Test database connection
    try:
        client = FirebaseClient()
        # Test operation
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    # Test AI service
    try:
        # Test OpenAI connection
        health_status["ai_service"] = "healthy"
    except Exception as e:
        health_status["ai_service"] = f"error: {str(e)}"
    
    return health_status
```

## Getting Help

### Log Analysis

When reporting issues, include:
1. **Error messages** with full stack traces
2. **Environment information** (OS, Python version, uv version)
3. **Configuration** (anonymized, without secrets)
4. **Steps to reproduce** the issue
5. **Expected vs actual behavior**

### Useful Commands

```bash
# System information
uv --version
python --version
docker --version

# Check running processes
ps aux | grep python
ps aux | grep uvicorn

# Network diagnostics
netstat -tulpn | grep :8000
curl -I http://localhost:8000/health

# File permissions
ls -la .env
ls -la app/

# Environment diagnostics
uv run python -c "
import sys
print('Python path:', sys.path)
print('Working directory:', os.getcwd())
print('Environment:', os.environ.keys())
"
```

### Community Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Firebase Admin SDK**: https://firebase.google.com/docs/admin/setup
- **OpenAI API Documentation**: https://platform.openai.com/docs/
- **uv Documentation**: https://docs.astral.sh/uv/

Remember to never share sensitive information like API keys or private keys when seeking help!
