# API Authentication Guide

## Overview

The Math Homework Solver API uses **Firebase Authentication** with **JWT Bearer tokens** to secure API endpoints. All protected endpoints require a valid Firebase ID token in the Authorization header.

## Authentication Flow

### 1. Client Authentication (Frontend)
```javascript
// Example Firebase authentication in Flutter/JavaScript
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

const auth = getAuth();
const userCredential = await signInWithEmailAndPassword(auth, email, password);
const user = userCredential.user;
const idToken = await user.getIdToken();
```

### 2. API Request with Token
```bash
curl -X POST "http://localhost:8000/api/v1/solve" \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN" \
  -F "file=@math_problem.png"
```

## Protected Endpoints

### POST `/api/v1/solve`
**Description**: Solve a math problem from an uploaded image  
**Authentication**: Required  
**Request**: Multipart form with image file  
**Headers**: `Authorization: Bearer <firebase_id_token>`

**Response**:
```json
{
  "question": "What is 2 + 2?",
  "answer": {
    "question": "What is 2 + 2?",
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

### GET `/api/v1/history`
**Description**: Get user's solution history  
**Authentication**: Required  
**Headers**: `Authorization: Bearer <firebase_id_token>`

**Response**:
```json
{
  "history": [
    {
      "id": "problem_id_123",
      "question": "What is 2 + 2?",
      "answer": { ... },
      "created_at": "2024-01-01T12:00:00Z",
      "file_name": "math_problem.png"
    }
  ],
  "user_id": "firebase_user_id",
  "total_problems": 1
}
```

### DELETE `/api/v1/history/{problem_id}`
**Description**: Delete a specific problem from history  
**Authentication**: Required  
**Parameters**: `problem_id` (path parameter)  
**Headers**: `Authorization: Bearer <firebase_id_token>`

**Response**:
```json
{
  "message": "Problem deleted successfully",
  "problem_id": "problem_id_123",
  "user_id": "firebase_user_id"
}
```

## Public Endpoints

### GET `/`
**Description**: API root endpoint  
**Authentication**: Not required

### GET `/health`
**Description**: Health check endpoint  
**Authentication**: Not required

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authorization token required"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authenticated"
}
```

### 401 Invalid Token
```json
{
  "detail": "Invalid or expired token"
}
```

## Security Features

1. **JWT Token Verification**: All tokens are verified against Firebase Auth
2. **User Isolation**: Users can only access their own data
3. **Automatic History Saving**: Solved problems are automatically saved to user's history
4. **Firebase Security Rules**: Database-level security through Firestore rules

## Firebase Setup Requirements

### Environment Variables
```bash
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_service_account_private_key
FIREBASE_CLIENT_EMAIL=your_service_account_email
FIREBASE_STORAGE_BUCKET=your_storage_bucket
```

### Firestore Security Rules
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

## Testing Authentication

### Test Unauthenticated Request
```bash
curl -X POST "http://localhost:8000/api/v1/solve" \
  -F "file=@test.png"
# Expected: 403 Forbidden
```

### Test Authenticated Request
```bash
curl -X POST "http://localhost:8000/api/v1/solve" \
  -H "Authorization: Bearer valid_firebase_token" \
  -F "file=@test.png"
# Expected: 200 OK with solution
```

## Development Notes

- The authentication service uses lazy initialization for Firebase client
- User information is extracted from JWT claims and passed to endpoint handlers
- All authentication errors are logged for debugging
- The system supports both email/password and other Firebase auth providers

## Migration from Unauthenticated

If upgrading from an unauthenticated version:

1. **Frontend**: Add Firebase authentication to your client application
2. **API Calls**: Include `Authorization: Bearer <token>` header in all API requests
3. **Error Handling**: Handle 401/403 responses and redirect to login
4. **Token Refresh**: Implement token refresh logic for long-running sessions
