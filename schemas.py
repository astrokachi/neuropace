from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    learning_goals: Optional[Dict[str, Any]] = None
    preferred_study_times: Optional[Dict[str, Any]] = None
    difficulty_preference: Optional[float] = None

class User(UserBase):
    id: int
    is_active: bool
    learning_goals: Dict[str, Any]
    preferred_study_times: Dict[str, Any]
    difficulty_preference: float
    average_reading_speed: float
    retention_rate: float
    cognitive_load_limit: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Material schemas
class MaterialBase(BaseModel):
    title: str
    subject: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class Material(MaterialBase):
    id: int
    user_id: int
    filename: str
    file_size: Optional[int]
    word_count: Optional[int]
    estimated_reading_time: Optional[float]
    difficulty_score: Optional[float]
    content_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schedule schemas
class ScheduleBase(BaseModel):
    scheduled_date: datetime
    duration_minutes: int
    session_type: str = "study"

class ScheduleCreate(ScheduleBase):
    material_id: int

class ScheduleUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None

class Schedule(ScheduleBase):
    id: int
    user_id: int
    material_id: int
    priority_score: float
    cognitive_load_score: float
    repetition_interval: int
    status: str
    start_position: int
    end_position: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Quiz schemas
class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None

class QuizBase(BaseModel):
    title: str
    difficulty_level: float = 0.5

class QuizCreate(QuizBase):
    material_id: int
    questions: List[QuizQuestion]

class Quiz(QuizBase):
    id: int
    material_id: int
    questions: List[Dict[str, Any]]
    total_questions: int
    content_section: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Performance schemas
class PerformanceBase(BaseModel):
    score: float
    time_taken: float
    questions_correct: int
    questions_total: int

class PerformanceCreate(PerformanceBase):
    quiz_id: Optional[int] = None
    session_id: Optional[int] = None
    question_responses: Optional[Dict[str, Any]] = None

class Performance(PerformanceBase):
    id: int
    user_id: int
    comprehension_speed: Optional[float]
    retention_score: Optional[float]
    difficulty_handled: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Study Session schemas
class StudySessionBase(BaseModel):
    start_time: datetime
    
class StudySessionCreate(StudySessionBase):
    schedule_id: Optional[int] = None

class StudySessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    pages_read: Optional[int] = None
    words_read: Optional[int] = None
    focus_score: Optional[float] = None
    completion_percentage: Optional[float] = None
    self_rated_understanding: Optional[float] = None
    session_notes: Optional[str] = None

class StudySession(StudySessionBase):
    id: int
    user_id: int
    schedule_id: Optional[int]
    end_time: Optional[datetime]
    duration_minutes: Optional[float]
    pages_read: int
    words_read: int
    reading_speed: Optional[float]
    focus_score: float
    completion_percentage: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
