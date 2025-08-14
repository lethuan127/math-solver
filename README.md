# Math Homework Solver

A full-stack application that helps students solve mathematics homework problems by taking pictures of their problems and providing step-by-step solutions.

## 🏗️ Architecture

- **Frontend**: Flutter mobile application
- **Backend**: FastAPI with Python
- **Database**: Firebase Firestore
- **AI**: OpenAI GPT-4 for problem solving
- **OCR**: Tesseract for text extraction from images
- **Deployment**: Docker containers with Nginx

## 📁 Project Structure

```
Mini-project/
├── src/
│   ├── backend/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py            # FastAPI application entry point
│   │   │   ├── models/            # Pydantic models
│   │   │   │   └── problem.py     # Problem and solution models
│   │   │   └── services/          # Business logic services
│   │   │       ├── image_processor.py  # OCR and image processing
│   │   │       └── math_solver.py      # LLM integration for solving
│   │   ├── requirements.txt       # Python dependencies
│   │   └── Dockerfile            # Backend container config
│   │
│   └── flutter_app/              # Flutter mobile application
│       ├── lib/
│       │   ├── main.dart         # App entry point
│       │   ├── screens/          # UI screens
│       │   │   └── home_screen.dart
│       │   ├── services/         # API and business logic
│       │   ├── models/           # Data models
│       │   └── widgets/          # Reusable UI components
│       └── pubspec.yaml          # Flutter dependencies
│
├── test_data/                    # Sample math problems for testing
├── firebase-config/              # Firebase configuration files
├── docker-compose.yml           # Multi-container orchestration
├── .env.example                 # Environment variables template
├── README.md                    # This file
└── behavioural_questions.md     # Interview questions responses
```

## 🚀 Features

- **Image Upload**: Take photos or upload images of math problems
- **OCR Processing**: Extract text from images using Tesseract
- **AI Problem Solving**: Use GPT-4 to solve mathematical problems
- **Step-by-Step Solutions**: Detailed explanations and solution steps
- **Firebase Integration**: Store problems and solutions in cloud database
- **Cross-Platform**: Flutter app works on iOS and Android
- **Responsive Design**: Modern, intuitive user interface

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **OpenAI GPT-4**: Advanced language model for problem solving
- **Tesseract OCR**: Text extraction from images
- **Firebase Admin SDK**: Database and authentication
- **Docker**: Containerization for easy deployment

### Frontend
- **Flutter**: Cross-platform mobile development framework
- **Riverpod**: State management solution
- **HTTP/Dio**: API communication
- **Image Picker**: Camera and gallery integration

### Infrastructure
- **Firebase Firestore**: NoSQL cloud database
- **Docker Compose**: Multi-container application orchestration
- **Nginx**: Reverse proxy and load balancer

## 📱 Setup Instructions

### Prerequisites
- Flutter SDK (3.10+)
- Python 3.11+
- Docker and Docker Compose
- Firebase project with Firestore enabled
- OpenAI API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Mini-project
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start backend services**
   ```bash
   docker-compose up -d
   ```

4. **Alternative: Local development**
   ```bash
   cd src/backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

### Flutter App Setup

1. **Install Flutter dependencies**
   ```bash
   cd src/flutter_app
   flutter pub get
   ```

2. **Configure Firebase**
   ```bash
   # Add your google-services.json (Android) and GoogleService-Info.plist (iOS)
   # Update firebase_options.dart with your configuration
   ```

3. **Run the app**
   ```bash
   flutter run
   ```

## 🧪 Testing

### Backend Testing
```bash
cd src/backend
python -m pytest tests/
```

### Flutter Testing
```bash
cd src/flutter_app
flutter test
```

## 📊 API Endpoints

### POST `/solve-problem`
Upload an image and get the mathematical solution.

**Request**: Multipart form with image file
**Response**: JSON with solution, steps, and explanation

### GET `/health`
Health check endpoint for monitoring.

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for GPT-4 access
- `FIREBASE_PROJECT_ID`: Firebase project identifier
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account JSON

### Firebase Setup
1. Create a Firebase project
2. Enable Firestore database
3. Generate service account credentials
4. Add configuration files to the project

## 🚀 Deployment

### Using Docker Compose
```bash
docker-compose up -d --build
```

### Manual Deployment
1. Build and deploy backend API
2. Build Flutter app for production
3. Configure reverse proxy (Nginx)
4. Set up SSL certificates
5. Configure monitoring and logging

## 📈 Future Enhancements

- **Multi-language Support**: Support for different mathematical notations
- **Handwriting Recognition**: Better OCR for handwritten problems
- **Problem History**: Save and review previously solved problems
- **Offline Mode**: Basic functionality without internet connection
- **Performance Optimization**: Caching and request optimization
- **Advanced Math**: Support for calculus, linear algebra, etc.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is created for the Growtrics interview assessment.

## 📞 Support

For questions or issues, please contact the development team or create an issue in the repository.
