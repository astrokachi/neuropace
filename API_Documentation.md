# Personalized Study Scheduler API Documentation

## Overview

The Personalized Study Scheduler API is a comprehensive AI-powered learning platform that helps users manage study materials, generate personalized schedules, create adaptive quizzes, and track learning performance using advanced ML algorithms.

**Base URL:** `http://localhost:5000` (or your deployed domain)  
**API Version:** 2.0.0  
**Authentication:** Bearer Token (JWT)

## Features

- 🧠 **Half-Life Regression scheduling** - Optimized spaced repetition
- 🤖 **ML-driven quiz generation** - Adaptive difficulty assessment
- 📊 **Advanced learning analytics** - Comprehensive performance tracking
- ⚡ **Cognitive load optimization** - Personalized learning paths
- 📈 **Adaptive difficulty progression** - Dynamic content adjustment

---

## Authentication

Most endpoints require authentication using JWT Bearer tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your_access_token>
```

### Authentication Flow

1. **Register** → Get user account
2. **Login** → Receive access token
3. **Use token** → Access protected endpoints

---

## Quick Start

```bash
# 1. Register a new user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "studyuser",
    "password": "securepassword123",
    "full_name": "Study User"
  }'

# 2. Login to get access token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=studyuser&password=securepassword123"

# 3. Upload a PDF material
curl -X POST http://localhost:5000/materials/upload \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@study_material.pdf" \
  -F "title=Machine Learning Basics" \
  -F "subject=Computer Science"
```

---

## API Endpoints

### 🔐 Authentication (`/auth`)

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "student@university.edu",
  "username": "studyuser123",
  "password": "securepassword123",
  "full_name": "Alex Johnson"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "student@university.edu",
  "username": "studyuser123",
  "full_name": "Alex Johnson",
  "is_active": true,
  "learning_goals": {},
  "preferred_study_times": {},
  "difficulty_preference": 0.5,
  "average_reading_speed": 200.0,
  "retention_rate": 0.7,
  "cognitive_load_limit": 1.0,
  "created_at": "2025-08-25T10:30:00Z"
}
```

#### Login
```http
POST /auth/login
```

**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
username=studyuser123&password=securepassword123
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "student@university.edu",
  "username": "studyuser123",
  "full_name": "Alex Johnson",
  "is_active": true,
  "learning_goals": {
    "target_subjects": ["Computer Science", "Mathematics"],
    "weekly_hours": 20
  },
  "preferred_study_times": {
    "morning": "09:00-11:00",
    "afternoon": "14:00-16:00"
  },
  "difficulty_preference": 0.6,
  "average_reading_speed": 220.0,
  "retention_rate": 0.75,
  "cognitive_load_limit": 1.2,
  "created_at": "2025-08-25T10:30:00Z"
}
```

#### Update User Profile
```http
PUT /auth/me
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "full_name": "Alexander Johnson",
  "learning_goals": {
    "target_subjects": ["Computer Science", "Mathematics", "Statistics"],
    "weekly_hours": 25,
    "certification_goal": "Data Science Certificate"
  },
  "preferred_study_times": {
    "morning": "08:00-10:00",
    "evening": "19:00-21:00"
  },
  "difficulty_preference": 0.7
}
```

**Response (200):** Updated user object

---

### 📚 Materials (`/materials`)

#### Upload PDF Material
```http
POST /materials/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
```
file: (binary PDF file)
title: "Machine Learning Fundamentals"
subject: "Computer Science"
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/materials/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@ml_textbook.pdf" \
  -F "title=Machine Learning Fundamentals" \
  -F "subject=Computer Science"
```

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Machine Learning Fundamentals",
  "filename": "ml_textbook.pdf",
  "file_size": 2048576,
  "word_count": 45000,
  "estimated_reading_time": 225.0,
  "difficulty_score": 0.72,
  "subject": "Computer Science",
  "content_type": "pdf",
  "created_at": "2025-08-25T11:00:00Z"
}
```

#### Get All Materials
```http
GET /materials/
Authorization: Bearer <token>
```

**Query Parameters:**
- `subject` (optional): Filter by subject

**Example:**
```http
GET /materials/?subject=Computer Science
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Machine Learning Fundamentals",
    "filename": "ml_textbook.pdf",
    "file_size": 2048576,
    "word_count": 45000,
    "estimated_reading_time": 225.0,
    "difficulty_score": 0.72,
    "subject": "Computer Science",
    "content_type": "pdf",
    "created_at": "2025-08-25T11:00:00Z"
  }
]
```

#### Get Specific Material
```http
GET /materials/{material_id}
Authorization: Bearer <token>
```

**Response (200):** Material object

#### Get Material Content
```http
GET /materials/{material_id}/content
Authorization: Bearer <token>
```

**Query Parameters:**
- `section` (optional): Get specific section number

**Example:**
```http
GET /materials/1/content?section=2
Authorization: Bearer <token>
```

**Response (200) - Full Content:**
```json
{
  "title": "Machine Learning Fundamentals",
  "full_content": "Chapter 1: Introduction to Machine Learning...",
  "word_count": 45000,
  "estimated_reading_time": 225.0,
  "difficulty_score": 0.72,
  "total_sections": 8,
  "sections": [
    {
      "section_number": 1,
      "text": "Chapter 1 content...",
      "word_count": 5600,
      "estimated_reading_time": 28.0
    }
  ]
}
```

**Response (200) - Specific Section:**
```json
{
  "section_number": 2,
  "content": "Chapter 2: Supervised Learning...",
  "word_count": 6200,
  "estimated_reading_time": 31.0,
  "total_sections": 8
}
```

#### Get Material Statistics
```http
GET /materials/{material_id}/stats
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "basic_stats": {
    "word_count": 45000,
    "estimated_reading_time": 225.0,
    "difficulty_score": 0.72,
    "file_size": 2048576
  },
  "content_structure": {
    "total_sections": 8,
    "paragraphs": 340,
    "sentences": 1250,
    "avg_words_per_sentence": 36.0
  },
  "sections": [
    {
      "section_number": 1,
      "word_count": 5600,
      "estimated_reading_time": 28.0
    }
  ]
}
```

#### Delete Material
```http
DELETE /materials/{material_id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Material deleted successfully"
}
```

---

### 📅 Schedules (`/schedules`)

#### Generate Study Schedule
```http
POST /schedules/generate
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "material_id": 1,
  "target_completion_date": "2025-09-15T23:59:59Z",
  "daily_study_time": 90
}
```

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "material_id": 1,
    "scheduled_date": "2025-08-26T09:00:00Z",
    "duration_minutes": 90,
    "session_type": "study",
    "priority_score": 1.0,
    "cognitive_load_score": 0.6,
    "repetition_interval": 1,
    "status": "scheduled",
    "start_position": 0,
    "end_position": 5600,
    "created_at": "2025-08-25T12:00:00Z"
  }
]
```

#### Get Schedules
```http
GET /schedules/
Authorization: Bearer <token>
```

**Query Parameters:**
- `material_id` (optional): Filter by material
- `status_filter` (optional): Filter by status (scheduled, completed, skipped, rescheduled)
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date

**Example:**
```http
GET /schedules/?material_id=1&status_filter=scheduled
Authorization: Bearer <token>
```

#### Update Schedule
```http
PUT /schedules/{schedule_id}
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "scheduled_date": "2025-08-27T10:00:00Z",
  "duration_minutes": 120,
  "status": "rescheduled"
}
```

#### Complete Schedule
```http
POST /schedules/{schedule_id}/complete
Authorization: Bearer <token>
```

**Request Body (optional):**
```json
{
  "completion_percentage": 85.5
}
```

**Response (200):**
```json
{
  "message": "Schedule marked as completed",
  "schedule": {
    "id": 1,
    "status": "completed",
    "completed_at": "2025-08-26T10:30:00Z"
  }
}
```

#### Adapt Schedules
```http
POST /schedules/adapt
Authorization: Bearer <token>
```

**Query Parameters:**
- `material_id` (optional): Adapt schedules for specific material

**Response (200):**
```json
{
  "message": "Applied 3 schedule adaptations",
  "adaptations": [
    {
      "schedule_id": 1,
      "adaptations": ["increase_review", "reduce_interval_to_2"]
    }
  ]
}
```

#### Get Weekly Schedule
```http
GET /schedules/upcoming/week
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "week_start": "2025-08-25T00:00:00Z",
  "week_end": "2025-09-01T00:00:00Z",
  "schedule": {
    "2025-08-26": [
      {
        "id": 1,
        "material_id": 1,
        "time": "09:00",
        "duration_minutes": 90,
        "session_type": "study",
        "priority_score": 1.0
      }
    ]
  },
  "total_sessions": 5
}
```

---

### 🧠 Quizzes (`/quizzes`)

#### Generate Quiz
```http
POST /quizzes/generate
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "material_id": 1,
  "num_questions": 8,
  "difficulty_level": 0.6,
  "content_section": "2"
}
```

**Response (200):**
```json
{
  "id": 1,
  "material_id": 1,
  "title": "Quiz for Machine Learning Fundamentals (Section 2)",
  "questions": [
    {
      "question": "What is supervised learning?",
      "type": "multiple_choice",
      "options": [
        "Learning with labeled data",
        "Learning without any data",
        "Learning with unlabeled data",
        "Learning with reinforcement"
      ],
      "correct_answer": 0,
      "explanation": "Supervised learning uses labeled training data."
    }
  ],
  "total_questions": 8,
  "difficulty_level": 0.6,
  "content_section": "2",
  "created_at": "2025-08-25T13:00:00Z"
}
```

#### Get Quiz Questions (for taking)
```http
GET /quizzes/{quiz_id}/questions
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "quiz_id": 1,
  "title": "Quiz for Machine Learning Fundamentals",
  "total_questions": 8,
  "difficulty_level": 0.6,
  "questions": [
    {
      "question_number": 1,
      "question": "What is supervised learning?",
      "type": "multiple_choice",
      "options": [
        "Learning with labeled data",
        "Learning without any data",
        "Learning with unlabeled data",
        "Learning with reinforcement"
      ]
    }
  ]
}
```

#### Submit Quiz Answers
```http
POST /quizzes/{quiz_id}/submit
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "answers": [0, 2, 1, 0, 3, 1, 2, 0],
  "time_taken": 12.5
}
```

**Response (200):**
```json
{
  "score": 0.875,
  "correct_count": 7,
  "total_questions": 8,
  "percentage": 87.5,
  "time_taken": 12.5,
  "detailed_results": [
    {
      "question_number": 1,
      "correct": true,
      "user_answer": 0,
      "correct_answer": 0
    }
  ],
  "performance_id": 1,
  "analysis": {
    "comprehension_speed": 0.56,
    "difficulty_handled": 0.6,
    "areas_for_improvement": ["Neural Networks"]
  }
}
```

#### Retry Quiz (Generate New Questions)
```http
POST /quizzes/{quiz_id}/retry
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Quiz regenerated with new questions",
  "quiz": {
    "id": 1,
    "total_questions": 8,
    "questions": []
  }
}
```

#### Get Quiz Answers (After Completion)
```http
GET /quizzes/{quiz_id}/answers
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "quiz_id": 1,
  "title": "Quiz for Machine Learning Fundamentals",
  "questions_with_answers": [
    {
      "question": "What is supervised learning?",
      "options": ["Learning with labeled data", "..."],
      "correct_answer": 0,
      "explanation": "Supervised learning uses labeled training data."
    }
  ]
}
```

---

### 📊 Performance Analytics (`/performance`)

#### Get Performance Analytics
```http
GET /performance/analytics
Authorization: Bearer <token>
```

**Query Parameters:**
- `material_id` (optional): Filter by material
- `days_back` (optional, default: 30): Analysis period

**Example:**
```http
GET /performance/analytics?material_id=1&days_back=14
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "period_days": 14,
  "overall_metrics": {
    "average_quiz_score": 0.845,
    "total_study_time_hours": 28.5,
    "materials_studied": 3,
    "quizzes_completed": 12
  },
  "learning_curve": {
    "improvement_rate": 0.125,
    "trend": "improving",
    "predicted_mastery_date": "2025-09-10"
  },
  "subject_performance": {
    "Computer Science": {
      "average_score": 0.88,
      "time_spent_hours": 18.2,
      "mastery_level": "proficient"
    }
  },
  "weekly_progress": [
    {
      "week": "2025-08-19",
      "study_hours": 12.5,
      "avg_score": 0.82,
      "materials_covered": 2
    }
  ],
  "recommendations": [
    "Focus more on Neural Networks topics",
    "Increase study session duration to 45 minutes",
    "Schedule review sessions for older materials"
  ]
}
```

#### Get Learning Curve
```http
GET /performance/learning-curve/{material_id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "material_id": 1,
  "curve_data": [
    {
      "session_number": 1,
      "date": "2025-08-20",
      "score": 0.65,
      "retention_rate": 0.7,
      "confidence_level": 0.6
    }
  ],
  "trend_analysis": {
    "slope": 0.042,
    "r_squared": 0.89,
    "projected_mastery": "2025-09-15"
  },
  "half_life_data": {
    "current_half_life": 7.2,
    "optimal_review_interval": 5
  }
}
```

#### Get Performance Summary
```http
GET /performance/summary
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "period": "30 days",
  "quiz_metrics": {
    "total_quizzes": 15,
    "average_score": 0.834,
    "score_percentage": 83.4
  },
  "study_metrics": {
    "total_sessions": 22,
    "total_study_time_minutes": 1680,
    "total_study_time_hours": 28.0,
    "average_focus_score": 0.78,
    "total_words_read": 85000,
    "average_reading_speed": 245.2
  },
  "performance_trend": "improving",
  "user_profile": {
    "retention_rate": 0.82,
    "cognitive_load_limit": 1.2,
    "preferred_difficulty": 0.7
  }
}
```

#### Get Materials Progress
```http
GET /performance/materials-progress
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "materials_progress": [
    {
      "material": {
        "id": 1,
        "title": "Machine Learning Fundamentals",
        "subject": "Computer Science",
        "difficulty_score": 0.72,
        "estimated_reading_time": 225.0
      },
      "progress": {
        "average_quiz_score": 0.875,
        "total_study_time_minutes": 480,
        "completion_rate": 85.5,
        "mastery_level": "proficient",
        "total_quizzes_taken": 6,
        "total_study_sessions": 8
      }
    }
  ],
  "total_materials": 3
}
```

#### Get Study Streaks
```http
GET /performance/streaks
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "current_streak": 7,
  "longest_streak": 14,
  "last_study_date": "2025-08-25",
  "streak_status": "completed_today",
  "total_study_days": 45
}
```

---

### 📖 Study Sessions (`/sessions`)

#### Start Study Session
```http
POST /sessions/start
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "start_time": "2025-08-25T14:00:00Z",
  "schedule_id": 1
}
```

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "schedule_id": 1,
  "start_time": "2025-08-25T14:00:00Z",
  "end_time": null,
  "duration_minutes": null,
  "pages_read": 0,
  "words_read": 0,
  "reading_speed": null,
  "focus_score": 0.5,
  "completion_percentage": 0.0,
  "created_at": "2025-08-25T14:00:00Z"
}
```

#### Update Study Session
```http
PUT /sessions/{session_id}/update
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "pages_read": 12,
  "words_read": 3200,
  "focus_score": 0.85,
  "completion_percentage": 45.0
}
```

#### Complete Study Session
```http
POST /sessions/{session_id}/complete
Authorization: Bearer <token>
```

**Request Body (optional):**
```json
{
  "completion_percentage": 90.0,
  "self_rated_understanding": 0.8,
  "session_notes": "Completed chapters 1-3, need to review neural networks",
  "focus_score": 0.82
}
```

**Response (200):**
```json
{
  "message": "Study session completed successfully",
  "session": {
    "id": 1,
    "duration_minutes": 85.5,
    "reading_speed": 37.4,
    "completion_percentage": 90.0
  },
  "performance_recorded": true,
  "calculated_metrics": {
    "duration_minutes": 85.5,
    "reading_speed": 37.4
  }
}
```

#### Get Active Session
```http
GET /sessions/active/current
Authorization: Bearer <token>
```

**Response (200) - With Active Session:**
```json
{
  "active_session": {
    "id": 1,
    "start_time": "2025-08-25T14:00:00Z",
    "duration_so_far": 42.5,
    "pages_read": 8,
    "words_read": 2100,
    "focus_score": 0.75,
    "schedule_id": 1,
    "schedule": {
      "id": 1,
      "session_type": "study",
      "duration_minutes": 90,
      "material_id": 1
    },
    "material": {
      "id": 1,
      "title": "Machine Learning Fundamentals",
      "subject": "Computer Science"
    }
  },
  "has_active_session": true
}
```

**Response (200) - No Active Session:**
```json
{
  "active_session": null,
  "has_active_session": false
}
```

#### Pause/Resume Session
```http
POST /sessions/{session_id}/pause
Authorization: Bearer <token>
```

```http
POST /sessions/{session_id}/resume
Authorization: Bearer <token>
```

**Request Body (for resume):**
```json
{
  "pause_duration_minutes": 5.2
}
```

#### Get Session Statistics
```http
GET /sessions/{session_id}/stats
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "session_id": 1,
  "basic_metrics": {
    "start_time": "2025-08-25T14:00:00Z",
    "end_time": "2025-08-25T15:25:30Z",
    "duration_minutes": 85.5,
    "effective_duration_minutes": 80.3,
    "pause_count": 2,
    "total_pause_time": 5.2
  },
  "reading_metrics": {
    "pages_read": 12,
    "words_read": 3200,
    "reading_speed": 37.4,
    "estimated_comprehension": 0.8
  },
  "engagement_metrics": {
    "focus_score": 0.82,
    "completion_percentage": 90.0,
    "interaction_count": 15,
    "productivity_score": 0.848
  },
  "material": {
    "id": 1,
    "title": "Machine Learning Fundamentals",
    "subject": "Computer Science",
    "difficulty_score": 0.72
  },
  "notes": "Completed chapters 1-3, need to review neural networks"
}
```

#### Abandon Session
```http
POST /sessions/{session_id}/abandon
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "reason": "interrupted_by_emergency"
}
```

---

### 🏠 General Endpoints

#### API Root
```http
GET /
```

**Response (200):**
```json
{
  "message": "Personalized Study Scheduler API",
  "version": "2.0.0",
  "features": [
    "Half-Life Regression scheduling",
    "ML-driven quiz generation",
    "Advanced learning analytics",
    "Cognitive load optimization",
    "Adaptive difficulty progression"
  ]
}
```

#### Health Check
```http
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

## Error Responses

### Common HTTP Status Codes

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Access denied
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation errors
- **500 Internal Server Error** - Server error

### Error Response Format

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "error_type": "validation_error"
}
```

### Common Error Examples

#### Authentication Error (401)
```json
{
  "detail": "Could not validate credentials",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

#### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### File Upload Error (400)
```json
{
  "detail": "File size exceeds 50.0MB limit"
}
```

---

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **File upload**: 10 uploads per hour  
- **Quiz generation**: 20 requests per hour
- **Other endpoints**: 100 requests per minute

Exceeded limits return HTTP 429 with retry information.

---

## File Upload Guidelines

### Supported Formats
- **PDF files only** (.pdf extension)
- **Maximum size**: 50MB
- **Content**: Text-based PDFs (not scanned images)

### Optimal File Characteristics
- Clear text extraction
- Structured content with sections
- Educational/academic material
- 1,000 - 100,000 words

---

## ML Algorithm Details

### Half-Life Regression Scheduling
- **Purpose**: Optimizes review intervals based on forgetting curves
- **Input**: Performance history, difficulty scores, user retention rates
- **Output**: Personalized review schedules with optimal timing

### Adaptive Quiz Generation
- **Algorithm**: Natural Language Processing + Pattern Matching
- **Difficulty Scaling**: Based on performance history and content complexity
- **Question Types**: Multiple choice, true/false, fill-in-the-blank

### Learning Analytics
- **Metrics**: Comprehension speed, retention rates, focus scores
- **Predictions**: Mastery timelines, performance trends
- **Recommendations**: Study schedule adjustments, content focus areas

---

## Integration Examples

### JavaScript/React Client

```javascript
class StudySchedulerAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }
  
  async uploadMaterial(file, title, subject) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('subject', subject);
    
    const response = await fetch(`${this.baseURL}/materials/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });
    
    return response.json();
  }
  
  async generateQuiz(materialId, numQuestions = 5, difficulty = 0.5) {
    const response = await fetch(`${this.baseURL}/quizzes/generate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        material_id: materialId,
        num_questions: numQuestions,
        difficulty_level: difficulty
      })
    });
    
    return response.json();
  }
}
```

### Python Client

```python
import requests
from typing import List, Optional

class StudySchedulerClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def upload_material(self, file_path: str, title: str, subject: str = None):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'title': title, 'subject': subject}
            response = requests.post(
                f"{self.base_url}/materials/upload",
                headers=self.headers,
                files=files,
                data=data
            )
        return response.json()
    
    def get_performance_analytics(self, material_id: Optional[int] = None, days_back: int = 30):
        params = {'days_back': days_back}
        if material_id:
            params['material_id'] = material_id
            
        response = requests.get(
            f"{self.base_url}/performance/analytics",
            headers=self.headers,
            params=params
        )
        return response.json()
```

---

## Support

### Documentation
- **API Reference**: This document
- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

### Rate Limits & Quotas
Contact support for increased limits for production applications.

### Best Practices
1. **Cache responses** when possible
2. **Implement retry logic** for transient errors
3. **Use pagination** for large datasets
4. **Monitor token expiration** (30 minutes default)
5. **Validate file uploads** before submission

---

**Version**: 2.0.0  
**Last Updated**: August 25, 2025  
**API Status**: ✅ Production Ready