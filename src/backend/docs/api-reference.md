# API Reference

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

All protected endpoints require a Firebase JWT token in the Authorization header:

```http
Authorization: Bearer <firebase_jwt_token>
```

## Endpoints

### Health & Info

#### GET `/`
**Description**: Root endpoint with API information  
**Authentication**: Not required

**Response**:
```json
{
  "message": "Math Homework Solver API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### GET `/health`
**Description**: Health check endpoint  
**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy"
}
```

### Math Solving

#### POST `/api/v1/solve`
**Description**: Solve a math problem from an uploaded image  
**Authentication**: Required  
**Content-Type**: `multipart/form-data`

**Request**:
- `file`: Image file (PNG, JPG, JPEG) containing the math problem

**Response**:
```json
{
  "question": "What is 2 + 2?",
  "answer": {
    "question": "What is 2 + 2?",
    "answer_label": null,
    "answer_value": "4",
    "explanation": "This is a basic addition problem. To solve it, we add the two numbers together.",
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

**Error Responses**:
- `400 Bad Request`: Invalid file format or missing file
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Processing failed

#### GET `/api/v1/history`
**Description**: Get user's solution history  
**Authentication**: Required

**Query Parameters**:
- `limit` (optional): Maximum number of problems to return (default: 50)

**Response**:
```json
{
  "history": [
    {
      "id": "problem_id_123",
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
      },
      "file_name": "math_problem.png",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "user_id": "firebase_user_id",
  "total_problems": 1
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Failed to retrieve history

#### DELETE `/api/v1/history/{problem_id}`
**Description**: Delete a specific problem from history  
**Authentication**: Required

**Path Parameters**:
- `problem_id`: ID of the problem to delete

**Response**:
```json
{
  "message": "Problem deleted successfully",
  "problem_id": "problem_id_123",
  "user_id": "firebase_user_id"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Problem not found or access denied
- `500 Internal Server Error`: Failed to delete problem

## Data Models

### SolutionStep
```json
{
  "step_number": 1,
  "description": "Description of the step",
  "calculation": "Mathematical calculation (optional)"
}
```

### MathAnswer
```json
{
  "question": "The original question",
  "answer_label": "A, B, C, D, or null for open-ended questions",
  "answer_value": "The final answer",
  "explanation": "Detailed explanation of the solution",
  "steps": [SolutionStep],
  "confidence": 0.95
}
```

### ProblemResponse
```json
{
  "question": "The original question",
  "answer": MathAnswer
}
```

### ProblemHistoryItem
```json
{
  "id": "unique_problem_id",
  "question": "The original question",
  "answer": MathAnswer,
  "file_name": "original_filename.png",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters or data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## CORS

The API supports CORS for the following origins:
- `http://localhost:3000` (React development)
- `http://localhost:8080` (Vue development)

Additional origins can be configured in the settings.

## Interactive Documentation

Visit `/docs` for interactive API documentation using Swagger UI, or `/redoc` for ReDoc documentation.
