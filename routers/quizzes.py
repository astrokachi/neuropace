from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Material, Quiz
from schemas import Quiz as QuizSchema, QuizCreate
from auth import get_current_active_user
from services.quiz_generator import QuizGenerator

router = APIRouter()

@router.post("/generate", response_model=QuizSchema)
async def generate_quiz(
    material_id: int,
    num_questions: int = 5,
    difficulty_level: float = 0.5,
    content_section: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a quiz from material content"""
    
    # Verify material belongs to user
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Validate parameters
    if num_questions < 1 or num_questions > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of questions must be between 1 and 20"
        )
    
    if difficulty_level < 0.0 or difficulty_level > 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Difficulty level must be between 0.0 and 1.0"
        )
    
    # Get content for quiz generation
    text_content = material.extracted_text
    if content_section:
        # Extract specific section content if requested
        from services.pdf_processor import PDFProcessor
        sections = PDFProcessor.extract_sections(text_content)
        try:
            section_num = int(content_section) - 1
            if 0 <= section_num < len(sections):
                text_content = sections[section_num]['text']
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid section number"
                )
        except ValueError:
            # If content_section is not a number, use it as a content identifier
            pass
    
    # Generate quiz
    quiz_result = QuizGenerator.generate_quiz_from_text(
        text=text_content,
        num_questions=num_questions,
        difficulty_level=difficulty_level,
        content_section=content_section
    )
    
    if not quiz_result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz generation failed: {quiz_result.get('error', 'Unknown error')}"
        )
    
    # Create quiz record
    quiz_title = f"Quiz for {material.title}"
    if content_section:
        quiz_title += f" (Section {content_section})"
    
    quiz = Quiz(
        material_id=material_id,
        title=quiz_title,
        questions=quiz_result['questions'],
        total_questions=quiz_result['total_questions'],
        difficulty_level=difficulty_level,
        content_section=content_section
    )
    
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    return quiz

@router.get("/", response_model=List[QuizSchema])
async def get_quizzes(
    material_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quizzes for the current user"""
    
    query = db.query(Quiz).join(Material).filter(Material.user_id == current_user.id)
    
    if material_id:
        query = query.filter(Quiz.material_id == material_id)
    
    quizzes = query.order_by(Quiz.created_at.desc()).all()
    return quizzes

@router.get("/{quiz_id}", response_model=QuizSchema)
async def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific quiz"""
    
    quiz = db.query(Quiz).join(Material).filter(
        Quiz.id == quiz_id,
        Material.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return quiz

@router.get("/{quiz_id}/questions")
async def get_quiz_questions(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quiz questions (without correct answers for taking the quiz)"""
    
    quiz = db.query(Quiz).join(Material).filter(
        Quiz.id == quiz_id,
        Material.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Return questions without correct answers for quiz taking
    questions = []
    for i, question in enumerate(quiz.questions):
        question_data = {
            'question_number': i + 1,
            'question': question.get('question', ''),
            'type': question.get('type', 'multiple_choice'),
            'options': question.get('options', [])
        }
        
        # For fill-in-the-blank, don't return the answer
        if question_data['type'] == 'fill_blank':
            question_data['options'] = []
        
        questions.append(question_data)
    
    return {
        'quiz_id': quiz.id,
        'title': quiz.title,
        'total_questions': quiz.total_questions,
        'difficulty_level': quiz.difficulty_level,
        'questions': questions
    }

@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: int,
    answers: List[Any],
    time_taken: float = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit quiz answers and get results"""
    
    quiz = db.query(Quiz).join(Material).filter(
        Quiz.id == quiz_id,
        Material.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Validate answers
    if len(answers) != quiz.total_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected {quiz.total_questions} answers, got {len(answers)}"
        )
    
    # Validate quiz answers
    validation_result = QuizGenerator.validate_quiz_answers(quiz.questions, answers)
    
    if not validation_result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_result.get('error', 'Answer validation failed')
        )
    
    # Record performance
    from services.performance_tracker import PerformanceTracker
    tracker = PerformanceTracker(db)
    
    performance_result = tracker.record_quiz_performance(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=validation_result['score'],
        time_taken=time_taken or 0.0,
        questions_correct=validation_result['correct_count'],
        questions_total=validation_result['total_questions'],
        question_responses={
            'answers': answers,
            'detailed_results': validation_result['detailed_results']
        }
    )
    
    if not performance_result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record performance"
        )
    
    return {
        'score': validation_result['score'],
        'correct_count': validation_result['correct_count'],
        'total_questions': validation_result['total_questions'],
        'percentage': round(validation_result['score'] * 100, 1),
        'time_taken': time_taken,
        'detailed_results': validation_result['detailed_results'],
        'performance_id': performance_result['performance_id'],
        'analysis': performance_result.get('analysis', {})
    }

@router.post("/{quiz_id}/retry")
async def retry_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reset and retry a quiz (generates new questions)"""
    
    quiz = db.query(Quiz).join(Material).filter(
        Quiz.id == quiz_id,
        Material.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Get material content
    material = quiz.material
    text_content = material.extracted_text
    
    # If quiz was for a specific section, use that section
    if quiz.content_section:
        from services.pdf_processor import PDFProcessor
        sections = PDFProcessor.extract_sections(text_content)
        try:
            section_num = int(quiz.content_section) - 1
            if 0 <= section_num < len(sections):
                text_content = sections[section_num]['text']
        except ValueError:
            pass
    
    # Generate new quiz questions
    quiz_result = QuizGenerator.generate_quiz_from_text(
        text=text_content,
        num_questions=quiz.total_questions,
        difficulty_level=quiz.difficulty_level,
        content_section=quiz.content_section
    )
    
    if not quiz_result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz regeneration failed: {quiz_result.get('error', 'Unknown error')}"
        )
    
    # Update quiz with new questions
    quiz.questions = quiz_result['questions']
    quiz.total_questions = quiz_result['total_questions']
    
    db.commit()
    db.refresh(quiz)
    
    return {
        'message': 'Quiz regenerated with new questions',
        'quiz': quiz
    }

@router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a quiz"""
    
    quiz = db.query(Quiz).join(Material).filter(
        Quiz.id == quiz_id,
        Material.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    db.delete(quiz)
    db.commit()
    
    return {"message": "Quiz deleted successfully"}

@router.get("/{quiz_id}/answers")
async def get_quiz_answers(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quiz answers (for review after completion)"""
    
    quiz = db.query(Quiz).join(Material).filter(
        Quiz.id == quiz_id,
        Material.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check if user has attempted this quiz
    from models import Performance
    performance_exists = db.query(Performance).filter(
        Performance.user_id == current_user.id,
        Performance.quiz_id == quiz_id
    ).first()
    
    if not performance_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must attempt the quiz before viewing answers"
        )
    
    # Return complete questions with answers
    return {
        'quiz_id': quiz.id,
        'title': quiz.title,
        'questions_with_answers': quiz.questions
    }
