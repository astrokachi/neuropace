from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Performance, StudySession, Material, Quiz
from schemas import Performance as PerformanceSchema, PerformanceCreate
from auth import get_current_active_user
from services.performance_tracker import PerformanceTracker

router = APIRouter()

@router.get("/analytics")
async def get_performance_analytics(
    material_id: Optional[int] = Query(None, description="Filter by specific material"),
    days_back: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive performance analytics for the current user"""
    
    tracker = PerformanceTracker(db)
    analytics = tracker.get_performance_analytics(
        user_id=current_user.id,
        material_id=material_id,
        days_back=days_back
    )
    
    if not analytics['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=analytics.get('error', 'Failed to retrieve analytics')
        )
    
    return analytics

@router.get("/learning-curve/{material_id}")
async def get_learning_curve(
    material_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get learning curve data for a specific material"""
    
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
    
    tracker = PerformanceTracker(db)
    curve_data = tracker.get_learning_curve_data(
        user_id=current_user.id,
        material_id=material_id
    )
    
    if not curve_data['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=curve_data.get('error', 'Failed to retrieve learning curve data')
        )
    
    return curve_data

@router.get("/quiz-history", response_model=List[PerformanceSchema])
async def get_quiz_history(
    material_id: Optional[int] = Query(None, description="Filter by material"),
    limit: int = Query(50, description="Number of records to return", ge=1, le=200),
    offset: int = Query(0, description="Number of records to skip", ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quiz performance history for the current user"""
    
    query = db.query(Performance).filter(
        Performance.user_id == current_user.id,
        Performance.quiz_id.isnot(None)
    )
    
    if material_id:
        query = query.join(Quiz).filter(Quiz.material_id == material_id)
    
    performances = query.order_by(Performance.created_at.desc()).offset(offset).limit(limit).all()
    return performances

@router.get("/session-history")
async def get_session_history(
    material_id: Optional[int] = Query(None, description="Filter by material"),
    days_back: int = Query(30, description="Days to look back", ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get study session history with performance metrics"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    query = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= cutoff_date
    )
    
    if material_id:
        # Join through Schedule to filter by material
        from models import Schedule
        query = query.join(Schedule, StudySession.schedule_id == Schedule.id).filter(
            Schedule.material_id == material_id
        )
    
    sessions = query.order_by(StudySession.start_time.desc()).all()
    
    # Format session data with performance metrics
    session_data = []
    for session in sessions:
        session_info = {
            'id': session.id,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'duration_minutes': session.duration_minutes,
            'pages_read': session.pages_read,
            'words_read': session.words_read,
            'reading_speed': session.reading_speed,
            'focus_score': session.focus_score,
            'completion_percentage': session.completion_percentage,
            'self_rated_understanding': session.self_rated_understanding,
            'schedule_id': session.schedule_id
        }
        
        # Add material info if available through schedule
        if session.schedule and session.schedule.material:
            session_info['material'] = {
                'id': session.schedule.material.id,
                'title': session.schedule.material.title,
                'subject': session.schedule.material.subject
            }
        
        session_data.append(session_info)
    
    return {
        'sessions': session_data,
        'total_sessions': len(sessions),
        'period_days': days_back
    }

@router.get("/summary")
async def get_performance_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overall performance summary for the current user"""
    
    # Get recent performance data (last 30 days)
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    # Quiz performances
    quiz_performances = db.query(Performance).filter(
        Performance.user_id == current_user.id,
        Performance.quiz_id.isnot(None),
        Performance.created_at >= cutoff_date
    ).all()
    
    # Study sessions
    study_sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= cutoff_date
    ).all()
    
    # Calculate summary metrics
    total_quizzes = len(quiz_performances)
    avg_quiz_score = sum(p.score for p in quiz_performances) / total_quizzes if total_quizzes > 0 else 0
    
    total_sessions = len(study_sessions)
    total_study_time = sum(s.duration_minutes for s in study_sessions if s.duration_minutes) or 0
    avg_focus_score = sum(s.focus_score for s in study_sessions) / total_sessions if total_sessions > 0 else 0
    
    # Reading speed calculation
    reading_speeds = [s.reading_speed for s in study_sessions if s.reading_speed and s.reading_speed > 0]
    avg_reading_speed = sum(reading_speeds) / len(reading_speeds) if reading_speeds else current_user.average_reading_speed
    
    # Words read total
    total_words_read = sum(s.words_read for s in study_sessions if s.words_read) or 0
    
    # Performance trends (comparing last 15 days to previous 15 days)
    mid_date = datetime.utcnow() - timedelta(days=15)
    
    recent_performances = [p for p in quiz_performances if p.created_at >= mid_date]
    older_performances = [p for p in quiz_performances if p.created_at < mid_date]
    
    trend = "stable"
    if recent_performances and older_performances:
        recent_avg = sum(p.score for p in recent_performances) / len(recent_performances)
        older_avg = sum(p.score for p in older_performances) / len(older_performances)
        
        if recent_avg > older_avg + 0.05:
            trend = "improving"
        elif recent_avg < older_avg - 0.05:
            trend = "declining"
    
    return {
        'period': '30 days',
        'quiz_metrics': {
            'total_quizzes': total_quizzes,
            'average_score': round(avg_quiz_score, 3),
            'score_percentage': round(avg_quiz_score * 100, 1)
        },
        'study_metrics': {
            'total_sessions': total_sessions,
            'total_study_time_minutes': total_study_time,
            'total_study_time_hours': round(total_study_time / 60, 1),
            'average_focus_score': round(avg_focus_score, 3),
            'total_words_read': total_words_read,
            'average_reading_speed': round(avg_reading_speed, 1)
        },
        'performance_trend': trend,
        'user_profile': {
            'retention_rate': current_user.retention_rate,
            'cognitive_load_limit': current_user.cognitive_load_limit,
            'preferred_difficulty': current_user.difficulty_preference
        }
    }

@router.get("/materials-progress")
async def get_materials_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get progress overview for all user materials"""
    
    materials = db.query(Material).filter(Material.user_id == current_user.id).all()
    
    materials_progress = []
    for material in materials:
        # Get quiz performances for this material
        quiz_performances = db.query(Performance).join(Quiz).filter(
            Performance.user_id == current_user.id,
            Quiz.material_id == material.id
        ).order_by(Performance.created_at.desc()).limit(10).all()
        
        # Get study sessions for this material
        from models import Schedule
        study_sessions = db.query(StudySession).join(Schedule).filter(
            StudySession.user_id == current_user.id,
            Schedule.material_id == material.id
        ).order_by(StudySession.start_time.desc()).limit(10).all()
        
        # Calculate progress metrics
        avg_score = 0
        total_study_time = 0
        completion_rate = 0
        
        if quiz_performances:
            avg_score = sum(p.score for p in quiz_performances) / len(quiz_performances)
        
        if study_sessions:
            total_study_time = sum(s.duration_minutes for s in study_sessions if s.duration_minutes) or 0
            completion_rates = [s.completion_percentage for s in study_sessions if s.completion_percentage is not None]
            completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        
        # Determine mastery level
        mastery_level = "not_started"
        if avg_score >= 0.9:
            mastery_level = "mastered"
        elif avg_score >= 0.7:
            mastery_level = "proficient"
        elif avg_score >= 0.5:
            mastery_level = "learning"
        elif avg_score > 0:
            mastery_level = "struggling"
        
        materials_progress.append({
            'material': {
                'id': material.id,
                'title': material.title,
                'subject': material.subject,
                'difficulty_score': material.difficulty_score,
                'estimated_reading_time': material.estimated_reading_time
            },
            'progress': {
                'average_quiz_score': round(avg_score, 3),
                'total_study_time_minutes': total_study_time,
                'completion_rate': round(completion_rate, 1),
                'mastery_level': mastery_level,
                'total_quizzes_taken': len(quiz_performances),
                'total_study_sessions': len(study_sessions)
            }
        })
    
    return {
        'materials_progress': materials_progress,
        'total_materials': len(materials)
    }

@router.get("/streaks")
async def get_study_streaks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get study streak information"""
    
    # Get all study sessions ordered by date
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).order_by(StudySession.start_time.desc()).all()
    
    if not sessions:
        return {
            'current_streak': 0,
            'longest_streak': 0,
            'last_study_date': None,
            'streak_status': 'no_data'
        }
    
    # Calculate streaks
    study_dates = []
    for session in sessions:
        date_str = session.start_time.strftime('%Y-%m-%d')
        if date_str not in study_dates:
            study_dates.append(date_str)
    
    # Sort dates (newest first)
    study_dates.sort(reverse=True)
    
    # Calculate current streak
    current_streak = 0
    today = datetime.utcnow().strftime('%Y-%m-%d')
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Check if studied today or yesterday (allow for timezone differences)
    if study_dates and (study_dates[0] == today or study_dates[0] == yesterday):
        current_date = datetime.strptime(study_dates[0], '%Y-%m-%d')
        current_streak = 1
        
        for i in range(1, len(study_dates)):
            prev_date = datetime.strptime(study_dates[i], '%Y-%m-%d')
            if (current_date - prev_date).days == 1:
                current_streak += 1
                current_date = prev_date
            else:
                break
    
    # Calculate longest streak
    longest_streak = 0
    temp_streak = 1
    
    if len(study_dates) > 1:
        for i in range(1, len(study_dates)):
            current_date = datetime.strptime(study_dates[i-1], '%Y-%m-%d')
            prev_date = datetime.strptime(study_dates[i], '%Y-%m-%d')
            
            if (current_date - prev_date).days == 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak)
    else:
        longest_streak = 1 if study_dates else 0
    
    # Determine streak status
    streak_status = "active"
    if current_streak == 0:
        streak_status = "broken"
    elif study_dates[0] == today:
        streak_status = "completed_today"
    elif study_dates[0] == yesterday:
        streak_status = "pending_today"
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'last_study_date': study_dates[0] if study_dates else None,
        'streak_status': streak_status,
        'total_study_days': len(study_dates)
    }

@router.post("/record-quiz", response_model=PerformanceSchema)
async def record_quiz_performance(
    performance_data: PerformanceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a quiz performance (alternative endpoint to quiz submission)"""
    
    if not performance_data.quiz_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz ID is required for quiz performance recording"
        )
    
    # Verify quiz exists and belongs to user's material
    quiz = db.query(Quiz).join(Material).filter(
        Quiz.id == performance_data.quiz_id,
        Material.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    tracker = PerformanceTracker(db)
    result = tracker.record_quiz_performance(
        user_id=current_user.id,
        quiz_id=performance_data.quiz_id,
        score=performance_data.score,
        time_taken=performance_data.time_taken,
        questions_correct=performance_data.questions_correct,
        questions_total=performance_data.questions_total,
        question_responses=performance_data.question_responses
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get('error', 'Failed to record performance')
        )
    
    # Get the created performance record
    performance = db.query(Performance).filter(Performance.id == result['performance_id']).first()
    return performance

@router.delete("/{performance_id}")
async def delete_performance_record(
    performance_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a performance record"""
    
    performance = db.query(Performance).filter(
        Performance.id == performance_id,
        Performance.user_id == current_user.id
    ).first()
    
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance record not found"
        )
    
    db.delete(performance)
    db.commit()
    
    return {"message": "Performance record deleted successfully"}
