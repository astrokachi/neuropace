from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, StudySession, Schedule, Material
from schemas import StudySession as StudySessionSchema, StudySessionCreate, StudySessionUpdate
from auth import get_current_active_user
from services.performance_tracker import PerformanceTracker

router = APIRouter()

@router.post("/start", response_model=StudySessionSchema)
async def start_study_session(
    session_data: StudySessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a new study session"""
    
    # Verify schedule belongs to user if schedule_id is provided
    if session_data.schedule_id:
        schedule = db.query(Schedule).filter(
            Schedule.id == session_data.schedule_id,
            Schedule.user_id == current_user.id
        ).first()
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
    
    # Create study session
    study_session = StudySession(
        user_id=current_user.id,
        schedule_id=session_data.schedule_id,
        start_time=session_data.start_time
    )
    
    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    
    return study_session

@router.put("/{session_id}/update", response_model=StudySessionSchema)
async def update_study_session(
    session_id: int,
    session_update: StudySessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a study session with progress data"""
    
    study_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    # Update fields
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(study_session, field, value)
    
    # Calculate derived metrics if end_time is set
    if session_update.end_time and study_session.start_time:
        duration = (session_update.end_time - study_session.start_time).total_seconds() / 60
        study_session.duration_minutes = duration
        
        # Calculate reading speed if words_read is provided
        if session_update.words_read and duration > 0:
            study_session.reading_speed = session_update.words_read / duration
    
    db.commit()
    db.refresh(study_session)
    
    return study_session

@router.post("/{session_id}/complete")
async def complete_study_session(
    session_id: int,
    completion_data: dict = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Complete a study session and record performance"""
    
    study_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    if study_session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Study session is already completed"
        )
    
    # Set end time and completion data
    end_time = datetime.utcnow()
    study_session.end_time = end_time
    
    # Calculate duration
    if study_session.start_time:
        duration = (end_time - study_session.start_time).total_seconds() / 60
        study_session.duration_minutes = duration
        
        # Calculate reading speed if words were read
        if study_session.words_read and duration > 0:
            study_session.reading_speed = study_session.words_read / duration
    
    # Update additional completion data if provided
    if completion_data:
        for field in ['completion_percentage', 'self_rated_understanding', 'session_notes', 'focus_score']:
            if field in completion_data:
                setattr(study_session, field, completion_data[field])
    
    db.commit()
    
    # Update associated schedule status if exists
    if study_session.schedule_id:
        schedule = db.query(Schedule).filter(Schedule.id == study_session.schedule_id).first()
        if schedule and schedule.status == 'scheduled':
            schedule.status = 'completed'
            schedule.completed_at = end_time
            db.commit()
    
    # Record session performance
    tracker = PerformanceTracker(db)
    session_performance_data = {
        'start_time': study_session.start_time,
        'end_time': study_session.end_time,
        'duration_minutes': study_session.duration_minutes,
        'pages_read': study_session.pages_read,
        'words_read': study_session.words_read,
        'reading_speed': study_session.reading_speed,
        'focus_score': study_session.focus_score,
        'completion_percentage': study_session.completion_percentage,
        'self_rated_understanding': study_session.self_rated_understanding,
        'session_notes': study_session.session_notes,
        'schedule_id': study_session.schedule_id
    }
    
    performance_result = tracker.record_study_session(
        user_id=current_user.id,
        session_data=session_performance_data
    )
    
    db.refresh(study_session)
    
    return {
        'message': 'Study session completed successfully',
        'session': study_session,
        'performance_recorded': performance_result.get('success', False),
        'calculated_metrics': {
            'duration_minutes': study_session.duration_minutes,
            'reading_speed': study_session.reading_speed
        }
    }

@router.get("/", response_model=List[StudySessionSchema])
async def get_study_sessions(
    schedule_id: Optional[int] = Query(None, description="Filter by schedule ID"),
    material_id: Optional[int] = Query(None, description="Filter by material ID"),
    start_date: Optional[datetime] = Query(None, description="Filter sessions after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter sessions before this date"),
    limit: int = Query(50, description="Number of sessions to return", ge=1, le=200),
    offset: int = Query(0, description="Number of sessions to skip", ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get study sessions for the current user"""
    
    query = db.query(StudySession).filter(StudySession.user_id == current_user.id)
    
    if schedule_id:
        query = query.filter(StudySession.schedule_id == schedule_id)
    
    if material_id:
        query = query.join(Schedule).filter(Schedule.material_id == material_id)
    
    if start_date:
        query = query.filter(StudySession.start_time >= start_date)
    
    if end_date:
        query = query.filter(StudySession.start_time <= end_date)
    
    sessions = query.order_by(StudySession.start_time.desc()).offset(offset).limit(limit).all()
    return sessions

@router.get("/{session_id}", response_model=StudySessionSchema)
async def get_study_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific study session"""
    
    study_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    return study_session

@router.get("/active/current")
async def get_active_session(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get currently active study session (if any)"""
    
    active_session = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.end_time.is_(None)
    ).order_by(StudySession.start_time.desc()).first()
    
    if not active_session:
        return {
            'active_session': None,
            'has_active_session': False
        }
    
    # Check if session is too old (more than 24 hours)
    if datetime.utcnow() - active_session.start_time > timedelta(hours=24):
        # Auto-complete old sessions
        active_session.end_time = active_session.start_time + timedelta(hours=2)  # Assume 2-hour session
        duration = 120  # 2 hours in minutes
        active_session.duration_minutes = duration
        active_session.completion_percentage = 50.0  # Partial completion
        db.commit()
        
        return {
            'active_session': None,
            'has_active_session': False,
            'message': 'Previous session was auto-completed due to timeout'
        }
    
    # Include related information
    session_info = {
        'id': active_session.id,
        'start_time': active_session.start_time,
        'duration_so_far': (datetime.utcnow() - active_session.start_time).total_seconds() / 60,
        'pages_read': active_session.pages_read,
        'words_read': active_session.words_read,
        'focus_score': active_session.focus_score,
        'schedule_id': active_session.schedule_id
    }
    
    # Add schedule and material info if available
    if active_session.schedule_id:
        schedule = db.query(Schedule).filter(Schedule.id == active_session.schedule_id).first()
        if schedule:
            session_info['schedule'] = {
                'id': schedule.id,
                'session_type': schedule.session_type,
                'duration_minutes': schedule.duration_minutes,
                'material_id': schedule.material_id
            }
            
            if schedule.material:
                session_info['material'] = {
                    'id': schedule.material.id,
                    'title': schedule.material.title,
                    'subject': schedule.material.subject
                }
    
    return {
        'active_session': session_info,
        'has_active_session': True
    }

@router.post("/{session_id}/pause")
async def pause_study_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a pause in the study session"""
    
    study_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    if study_session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pause a completed session"
        )
    
    # Increment pause count and record pause time
    study_session.pause_count = (study_session.pause_count or 0) + 1
    
    # Note: In a real application, you might want to track pause start/end times
    # For now, we'll just increment the counter
    
    db.commit()
    
    return {
        'message': 'Pause recorded',
        'total_pauses': study_session.pause_count
    }

@router.post("/{session_id}/resume")
async def resume_study_session(
    session_id: int,
    pause_duration_minutes: float = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Resume a paused study session"""
    
    study_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    if study_session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot resume a completed session"
        )
    
    # Add pause time to total pause time
    if pause_duration_minutes > 0:
        study_session.total_pause_time = (study_session.total_pause_time or 0) + pause_duration_minutes
        db.commit()
    
    return {
        'message': 'Session resumed',
        'total_pause_time': study_session.total_pause_time
    }

@router.get("/{session_id}/stats")
async def get_session_stats(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a study session"""
    
    study_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    # Calculate effective study time (total time minus pauses)
    effective_duration = study_session.duration_minutes or 0
    if study_session.total_pause_time:
        effective_duration = max(0, effective_duration - study_session.total_pause_time)
    
    # Calculate productivity metrics
    productivity_score = 0
    if study_session.duration_minutes and study_session.duration_minutes > 0:
        # Base productivity on focus score and completion percentage
        focus_component = (study_session.focus_score or 0.5) * 0.4
        completion_component = (study_session.completion_percentage or 0) / 100 * 0.6
        productivity_score = focus_component + completion_component
    
    # Get material info if available through schedule
    material_info = None
    if study_session.schedule and study_session.schedule.material:
        material = study_session.schedule.material
        material_info = {
            'id': material.id,
            'title': material.title,
            'subject': material.subject,
            'difficulty_score': material.difficulty_score
        }
    
    return {
        'session_id': session_id,
        'basic_metrics': {
            'start_time': study_session.start_time,
            'end_time': study_session.end_time,
            'duration_minutes': study_session.duration_minutes,
            'effective_duration_minutes': effective_duration,
            'pause_count': study_session.pause_count or 0,
            'total_pause_time': study_session.total_pause_time or 0
        },
        'reading_metrics': {
            'pages_read': study_session.pages_read or 0,
            'words_read': study_session.words_read or 0,
            'reading_speed': study_session.reading_speed,
            'estimated_comprehension': study_session.self_rated_understanding
        },
        'engagement_metrics': {
            'focus_score': study_session.focus_score or 0,
            'completion_percentage': study_session.completion_percentage or 0,
            'interaction_count': study_session.interaction_count or 0,
            'productivity_score': round(productivity_score, 3)
        },
        'material': material_info,
        'notes': study_session.session_notes
    }

@router.delete("/{session_id}")
async def delete_study_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a study session"""
    
    study_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    # Check if session is currently active
    if not study_session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete an active session. Complete or abandon it first."
        )
    
    db.delete(study_session)
    db.commit()
    
    return {"message": "Study session deleted successfully"}

@router.post("/{session_id}/abandon")
async def abandon_study_session(
    session_id: int,
    reason: str = "user_abandoned",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Abandon an active study session without completion"""
    
    study_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    if study_session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already completed"
        )
    
    # Mark session as abandoned
    study_session.end_time = datetime.utcnow()
    if study_session.start_time:
        duration = (study_session.end_time - study_session.start_time).total_seconds() / 60
        study_session.duration_minutes = duration
    
    # Set low completion percentage for abandoned session
    study_session.completion_percentage = min(study_session.completion_percentage or 0, 25.0)
    study_session.session_notes = f"Session abandoned: {reason}"
    
    db.commit()
    
    return {
        'message': 'Study session abandoned',
        'session_id': session_id,
        'reason': reason
    }
