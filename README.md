# Math Homework Solver 🧮

A comprehensive full-stack application that helps students solve mathematics homework problems by taking pictures of their problems and providing step-by-step AI-powered solutions.

## 🏗️ Architecture Overview

This project is a modular full-stack application with the following components:

- **Frontend**: Flutter cross-platform mobile application
- **Backend**: FastAPI REST API (Python 3.11+)
- **Database**: Firebase Firestore for data persistence
- **AI/ML**: OpenAI API for mathematical problem solving
- **Infrastructure**: Docker containers, optional Nginx reverse proxy
- **Package Management**: UV for Python dependency management
- **Testing**: Pytest suite and DeepEval for AI evaluation

## 📁 Project Structure

```
Mini-project/
├── src/
│   ├── backend/                        # FastAPI Backend Service
│   │   ├── app/
│   │   │   ├── main.py                 # FastAPI application entry point
│   │   │   ├── modules/                # Modular DDD-style structure
│   │   │   │   ├── auth/
│   │   │   │   │   ├── domain/
│   │   │   │   │   └── infrastructure/ # Firebase auth service
│   │   │   │   ├── math_solving/
│   │   │   │   │   ├── application/    # DTOs and use cases
│   │   │   │   │   ├── domain/         # Entities and interfaces
│   │   │   │   │   ├── infrastructure/ # OpenAI service, repository
│   │   │   │   │   └── presentation/   # API endpoints
│   │   │   │   └── shared/              # Config, DI container, Firebase client, utils
│   │   ├── tests/                      # Backend tests (integration, e2e harness)
│   │   ├── docs/                       # Backend docs
│   │   ├── pyproject.toml              # UV project configuration
│   │   ├── uv.lock                     # UV lock file
│   │   └── Dockerfile                  # Backend container configuration
│   │
│   ├── frontend/                       # Flutter Mobile Application
│   │   ├── lib/                        # Flutter source code
│   │   ├── android/                    # Android-specific configurations
│   │   └── pubspec.yaml                # Flutter dependencies
│   │
│   └── scripts/                        # Deployment and utility scripts
│       ├── deploy.sh                   # Automated deployment script
│       └── setup.sh                    # Environment setup script
│
├── firebase-config/                    # (Optional) Firebase files for container mounts
├── ssl/                                # SSL certificates for HTTPS (for Nginx)
├── docker-compose.yml                  # Multi-container orchestration
├── nginx.conf                          # Nginx reverse proxy configuration
├── package.json                        # Node.js tooling (CommitLint/Husky)
├── commitlint.config.js                # Conventional commit linting configuration
└── behavioural_questions.md            # Assessment responses
```

## 🚀 Key Features

### Core Functionality
- **📸 Image Upload & Processing**: Take photos or upload images of math problems
- **🔍 AI-Powered Problem Solving**: Advanced GPT-4 Vision integration for mathematical analysis
- **📝 Step-by-Step Solutions**: Detailed explanations with solution steps and confidence scoring
- **📚 Problem History**: Store and retrieve previously solved problems
- **🔐 User Authentication**: Firebase Authentication integration
- **☁️ Cloud Storage**: Firebase Storage for image persistence

### Technical Features
- **🌐 Cross-Platform**: Flutter app supports iOS and Android
- **⚡ High Performance**: Async/await patterns throughout the backend
- **🔄 Real-time Updates**: Firebase Firestore real-time data synchronization
- **🛡️ Security**: CORS configuration, input validation, and secure API endpoints
- **📊 Comprehensive Testing**: Integration and AI evaluation tests
- **🐳 Containerization**: Docker support with optional Nginx reverse proxy
- **🔍 Code Quality**: Linting with Ruff, formatting with Black, type checking with MyPy
- **📈 Monitoring**: Health check endpoints and structured logging

### AI/ML Capabilities
- **🧠 Advanced OCR**: Text extraction from mathematical images
- **🎯 Evaluation**: Custom metrics with DeepEval framework
- **📋 Comprehensive Test Suite**: 30 diverse math problems for model validation
- **🔄 Parallel Testing**: Optimized test execution for faster feedback
- **📊 Performance Metrics**: Answer relevancy, faithfulness, and custom math accuracy scoring

## 🛠️ Technology Stack

### Backend Technologies
- **FastAPI 0.115.0+**: Modern, fast web framework with automatic API documentation
- **Python 3.11+**: Latest Python features with enhanced performance
- **OpenAI Python SDK**: AI integration for problem solving
- **Firebase Admin SDK 6.2.0**: Authentication, database, and storage integration
- **UV**: Modern Python package manager for faster dependency resolution
- **Pydantic 2.9.0+**: Data validation and serialization with Python type hints
- **Uvicorn**: ASGI server with auto-reload in development

### Frontend Technologies
- **Flutter 3.10.0+**: Google's UI toolkit for cross-platform development
- **Riverpod 2.4.9**: Advanced state management solution
- **Provider 6.1.1**: State management for Flutter applications
- **Firebase SDK**: Authentication, Firestore, and Storage integration
- **HTTP/Dio**: Robust API communication libraries
- **Image Picker**: Camera and gallery integration

### Database & Storage
- **Firebase Firestore**: Scalable NoSQL cloud database
- **Firebase Storage**: Secure file storage with CDN
- **Firebase Authentication**: Comprehensive user management

### Infrastructure & DevOps
- **Docker & Docker Compose**: Containerization and orchestration
- **Nginx (optional)**: Reverse proxy and TLS termination
- **SSL/TLS**: Secure HTTPS configuration

### Development & Testing
- **DeepEval 3.3.5**: AI model evaluation framework
- **Pytest**: Testing framework with async support
- **Ruff**: Fast Python linter
- **Black**: Code formatter
- **MyPy**: Static type checking
- **CommitLint**: Conventional commit message linting
- **Husky**: Git hooks (run `npm run prepare` once)

## 📱 API Documentation

### Core Endpoints

#### `POST /api/v1/solve` (requires Firebase auth)
Solve a mathematical problem from an uploaded image.

**Request:**
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Body**: Image file (PNG, JPG, JPEG)
- **Max File Size**: 10MB

Include header: `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**
```json
{
  "question": "What is 2 + 2?",
  "answer": {
    "question": "What is 2 + 2?",
    "answer_label": null,
    "answer_value": "4",
    "explanation": "This is a basic addition problem...",
    "steps": [
      {
        "step_number": 1,
        "description": "Add the numbers together",
        "calculation": "2 + 2 = 4"
      }
    ],
    "confidence": 0.95
  }
}
```

#### `GET /api/v1/history` (requires Firebase auth)
Retrieve the authenticated user's solution history.

**Parameters:**
- `user_id` (string): Firebase user ID

**Response:**
```json
{
  "history": [
    {
      "id": "problem_id",
      "question": "Problem description",
      "answer": {...},
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### `DELETE /api/v1/history/{problem_id}` (requires Firebase auth)
Delete a specific problem from the authenticated user's history.

**Parameters:**
- `problem_id` (string): Problem identifier
- `user_id` (string): Firebase user ID

#### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.11+**
- **Flutter SDK 3.10.0+**
- **Docker & Docker Compose**
- **UV Package Manager**
- **Firebase Project** with Firestore and Storage enabled
- **OpenAI API Key**

### Backend Setup

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd Mini-project/src/backend
   ```

2. **Install UV** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install Dependencies**
   ```bash
   uv sync
   ```

4. **Environment Configuration**
   Create a `.env` file in `src/backend` with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"  # note escaped newlines
   FIREBASE_CLIENT_EMAIL=your_service_account_email
   FIREBASE_STORAGE_BUCKET=your_bucket_name
   ```

5. **Run Development Server**
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Flutter App Setup

1. **Navigate to Frontend**
   ```bash
   cd src/frontend
   ```

2. **Install Dependencies**
   ```bash
   flutter pub get
   ```

3. **Firebase Configuration**
   - Add `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
   - Configure `firebase_options.dart` with your project settings

4. **Run Application**
   ```bash
   flutter run
   ```

### Docker Deployment

1. **Start Services**
   ```bash
   docker-compose up -d --build
   ```

2. **View Logs**
   ```bash
   docker-compose logs -f backend
   ```

3. **Stop Services**
   ```bash
   docker-compose down
   ```

## 🧪 Testing & Evaluation

### Backend Testing

**Run All Tests:**
```bash
cd src/backend
uv run pytest
```

**Run with Coverage:**
```bash
uv run pytest --cov=app --cov-report=html
```

**Run AI Model Evaluation:**
```bash
uv run pytest app/modules/math_solving/evaluation/test_math_solver_deepeval.py -v
```

Note: parallel execution requires `pytest-xdist` which is not included by default.

### Test Coverage

The application includes testing across multiple layers:

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **AI Model Evaluation**: 30 diverse mathematical problems
- **Performance Testing**: Response time and accuracy metrics
- **Code Quality**: Linting, formatting, and type checking

### Evaluation Metrics

The AI model is evaluated using:
- **Custom Math Accuracy**: Specialized metric for mathematical correctness
- **Answer Relevancy**: How relevant the answer is to the question
- **Faithfulness**: Consistency between context and response
- **Confidence Scoring**: Model's confidence in the solution

## 📊 Performance & Monitoring

### Key Performance Indicators (targets)
- **Response Time**: Average API response time < 5 seconds
- **Accuracy**: Mathematical problem solving accuracy > 85%
- **Availability**: 99.9% uptime target
- **Error Rate**: < 1% error rate for valid requests

### Monitoring Features
- **Health Check Endpoints**: `/health` for service monitoring
- **Structured Logging**: Comprehensive logging with log levels
- **Error Tracking**: Detailed error reporting and stack traces
- **Performance Metrics**: Response time and throughput monitoring

## 🔧 Configuration

### Environment Variables

**Required:**
- `OPENAI_API_KEY`: OpenAI API key for GPT-4 Vision access
- `FIREBASE_PROJECT_ID`: Firebase project identifier
- `FIREBASE_PRIVATE_KEY`: Firebase service account private key
- `FIREBASE_CLIENT_EMAIL`: Firebase service account email
- `FIREBASE_STORAGE_BUCKET`: Firebase storage bucket name

**Optional:**
- `DEEPEVAL_API_KEY`: DeepEval cloud features API key
- `DEBUG`: Enable debug mode (default: true)

### Firebase Setup

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Create new project or use existing one

2. **Enable Services**
   - Firestore Database (Native mode)
   - Firebase Storage
   - Firebase Authentication

3. **Generate Service Account**
   - Go to Project Settings > Service Accounts
   - Generate new private key
   - Download JSON credentials

4. **Configure Security Rules**
   ```javascript
   // Firestore rules
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{userId}/solutions/{document=**} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
     }
   }
   ```

## 🚀 Deployment

### Production Deployment

1. **Build & Run**
   ```bash
   docker-compose up -d --build
   ```

2. **Deploy with Script (optional)**
   ```bash
   ./src/scripts/deploy.sh
   ```

3. **SSL Configuration (if using Nginx)**
   - Place SSL certificates in `ssl/`
   - Update `nginx.conf` for HTTPS configuration

### Cloud Deployment Options

- **Google Cloud Run**: Serverless container deployment
- **AWS ECS**: Container orchestration service
- **Azure Container Instances**: Managed container service
- **Digital Ocean App Platform**: Platform-as-a-Service deployment

## 🔮 Future Enhancements

### Planned Features
- **🌍 Multi-language Support**: Support for different mathematical notations and languages
- **✍️ Handwriting Recognition**: Enhanced OCR for handwritten mathematical problems
- **📱 Offline Mode**: Basic functionality without internet connection
- **🎨 Advanced UI/UX**: Enhanced user interface with animations and better accessibility
- **📈 Analytics Dashboard**: Usage analytics and performance monitoring
- **🔄 Real-time Collaboration**: Share problems and solutions with classmates
- **🎓 Learning Paths**: Personalized learning recommendations

### Technical Improvements
- **⚡ Performance Optimization**: Response caching and request optimization
- **🧮 Advanced Mathematics**: Support for calculus, linear algebra, and advanced topics
- **🔐 Enhanced Security**: Rate limiting, input sanitization, and security headers
- **📊 Advanced Analytics**: User behavior tracking and performance metrics
- **🤖 Multiple AI Models**: Integration with additional AI providers for comparison

## 🤝 Contributing

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make Changes**
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation as needed
4. **Commit Changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
5. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Submit Pull Request**

### Code Quality Standards
- **Linting**: Code must pass Ruff linting checks
- **Formatting**: Code must be formatted with Black
- **Type Checking**: Code must pass MyPy type checking
- **Testing**: New features must include appropriate tests
- **Documentation**: Code must be properly documented

## 📄 License

This project is created for the Growtrics interview assessment and is intended for educational and evaluation purposes.

## 📞 Support & Contact

For questions, issues, or feature requests:
- **Create an Issue**: Use GitHub Issues for bug reports and feature requests
- **Documentation**: Check the comprehensive documentation in this README
- **API Documentation**: Visit `/docs` endpoint when running the backend server

---

**Built with ❤️ using modern technologies and best practices for the Growtrics interview assessment.**