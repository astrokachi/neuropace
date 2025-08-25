# Overview

This is a **Personalized Study Scheduler API** built with FastAPI that helps users manage their study materials, generate quizzes, and create adaptive learning schedules. The system processes PDF documents, analyzes content difficulty, tracks performance metrics, and provides personalized study recommendations based on individual learning patterns.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **FastAPI** serves as the main web framework, providing automatic API documentation and request/response validation
- **SQLAlchemy** handles database operations with connection pooling for performance optimization
- **Alembic** manages database migrations and schema changes
- Modular router architecture separates concerns (auth, materials, quizzes, schedules, performance, sessions)

## Authentication & Security
- **JWT (JSON Web Tokens)** for stateless authentication using the JOSE library
- **bcrypt password hashing** via Passlib for secure credential storage
- **Bearer token authentication** with automatic token validation middleware
- User session management with configurable token expiration

## Database Architecture
- **PostgreSQL** as the primary database (configurable via environment variables)
- **Connection pooling** with pre-ping health checks and automatic reconnection
- Relational data model with foreign key relationships between users, materials, schedules, and performance metrics
- JSON fields for storing flexible user preferences and learning analytics

## File Processing System
- **PDF text extraction** using PyPDF2 for content analysis
- **File upload handling** with size limits and unique filename generation
- **Content analysis pipeline** that calculates reading time, difficulty scores, and word counts
- Structured text processing for quiz generation and content sectioning

## AI-Powered Features
- **Quiz generation service** that creates multiple-choice, true/false, and fill-in-the-blank questions from text content
- **Performance tracking system** that monitors learning progress and adapts to user patterns
- **Adaptive scheduling algorithm** that adjusts study plans based on user performance and preferences
- **Difficulty analysis** that matches content complexity to user skill levels

## Service Layer Architecture
- **PDFProcessor**: Handles document parsing and text extraction
- **QuizGenerator**: Creates assessments from text content using pattern matching
- **PerformanceTracker**: Analyzes learning metrics and progress patterns  
- **StudyScheduler**: Generates and adapts personalized study timelines

# External Dependencies

## Database
- **PostgreSQL** for primary data storage with connection pooling
- **SQLAlchemy** ORM for database abstraction and query building
- **Alembic** for database schema migrations

## Authentication & Security
- **python-jose** for JWT token creation and validation
- **passlib[bcrypt]** for secure password hashing
- **cryptography** libraries for token security

## File Processing
- **PyPDF2** for PDF text extraction and metadata analysis
- **FastAPI file upload** handling for document processing

## Optional Integrations
- **Supabase** integration (configured via environment variables) for cloud database hosting
- **CORS middleware** for cross-origin request handling in web applications

## Development & Deployment
- **uvicorn** ASGI server for running the FastAPI application
- **pydantic** for data validation and serialization
- Environment-based configuration system for deployment flexibility