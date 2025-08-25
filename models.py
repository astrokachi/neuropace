from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Learning preferences
    learning_goals = Column(JSON, default=dict)
    preferred_study_times = Column(JSON, default=dict)
    difficulty_preference = Column(Float, default=0.5)
    
    # Personal learning metrics
    average_reading_speed = Column(Float, default=200.0)  # words per minute
    retention_rate = Column(Float, default=0.7)
    cognitive_load_limit = Column(Float, default=1.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    materials = relationship("Material", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")
    performance_records = relationship("Performance", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    
    # Content analysis
    extracted_text = Column(Text)
    word_count = Column(Integer)
    estimated_reading_time = Column(Float)  # in minutes
    difficulty_score = Column(Float)
    
    # Metadata
    subject = Column(String)
    content_type = Column(String, default="pdf")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="materials")
    schedules = relationship("Schedule", back_populates="material")
    quizzes = relationship("Quiz", back_populates="material")

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    
    # Schedule details
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    session_type = Column(String, default="study")  # study, review, quiz
    
    # Adaptive scheduling data
    priority_score = Column(Float, default=1.0)
    cognitive_load_score = Column(Float, default=0.5)
    repetition_interval = Column(Integer, default=1)  # days
    
    # Session status
    status = Column(String, default="scheduled")  # scheduled, completed, skipped, rescheduled
    completed_at = Column(DateTime(timezone=True))
    
    # Content section (for partial material study)
    start_position = Column(Integer, default=0)
    end_position = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="schedules")
    material = relationship("Material", back_populates="schedules")
    study_sessions = relationship("StudySession", back_populates="schedule")

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    
    # Quiz metadata
    title = Column(String, nullable=False)
    questions = Column(JSON, nullable=False)  # List of question objects
    total_questions = Column(Integer, nullable=False)
    difficulty_level = Column(Float, default=0.5)
    
    # Content reference
    content_section = Column(String)  # Which part of material this quiz covers
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    material = relationship("Material", back_populates="quizzes")
    performance_records = relationship("Performance", back_populates="quiz")

class Performance(Base):
    __tablename__ = "performance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    session_id = Column(Integer, ForeignKey("study_sessions.id"))
    
    # Performance metrics
    score = Column(Float)  # 0.0 to 1.0
    time_taken = Column(Float)  # minutes
    questions_correct = Column(Integer)
    questions_total = Column(Integer)
    
    # Learning analytics
    comprehension_speed = Column(Float)  # questions per minute
    retention_score = Column(Float)  # based on follow-up quizzes
    
    # Response analysis
    question_responses = Column(JSON, default=dict)  # detailed responses
    difficulty_handled = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="performance_records")
    quiz = relationship("Quiz", back_populates="performance_records")
    study_session = relationship("StudySession", back_populates="performance_records")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    
    # Session details
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Float)
    
    # Reading metrics
    pages_read = Column(Integer, default=0)
    words_read = Column(Integer, default=0)
    reading_speed = Column(Float)  # words per minute
    
    # Engagement metrics
    focus_score = Column(Float, default=0.5)  # 0.0 to 1.0
    interaction_count = Column(Integer, default=0)
    pause_count = Column(Integer, default=0)
    total_pause_time = Column(Float, default=0.0)  # minutes
    
    # Session outcome
    completion_percentage = Column(Float, default=0.0)
    self_rated_understanding = Column(Float)  # 0.0 to 1.0
    session_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    schedule = relationship("Schedule", back_populates="study_sessions")
    performance_records = relationship("Performance", back_populates="study_session")
