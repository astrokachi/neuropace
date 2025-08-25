from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Schedule, Material
from schemas import Schedule as ScheduleSchema, ScheduleCreate, ScheduleUpdate
from auth import get_current_active_user
from services.scheduler import StudyScheduler

router = APIRouter()

@router.post("/generate", response_model=List[ScheduleSchema])
async def generate_schedule(
    material_id: int,
    target_completion_date: datetime,
    daily_study_time: int = 60,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a study schedule for a material"""
    
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
    
    # Validate target date
    if target_completion_date <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target completion date must be in the future"
        )
    
    # Generate schedule
    scheduler = StudyScheduler(db)
    schedule_data = scheduler.generate_initial_schedule(
        user_id=current_user.id,
        material_id=material_id,
        target_completion_date=target_completion_date,
        daily_study_time=daily_study_time
    )
    
    if not schedule_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate schedule"
        )
    
    # Save schedules to database
    schedules = []
    for schedule_entry in schedule_data:
        schedule = Schedule(**schedule_entry)
        db.add(schedule)
        schedules.append(schedule)
    
    db.commit()
    
    # Refresh all schedules to get IDs
    for schedule in schedules:
        db.refresh(schedule)
    
    return schedules

@router.get("/", response_model=List[ScheduleSchema])
async def get_schedules(
    material_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get schedules for the current user"""
    
    query = db.query(Schedule).filter(Schedule.user_id == current_user.id)
    
    if material_id:
        query = query.filter(Schedule.material_id == material_id)
    
    if status_filter:
        query = query.filter(Schedule.status == status_filter)
    
    if start_date:
        query = query.filter(Schedule.scheduled_date >= start_date)
    
    if end_date:
        query = query.filter(Schedule.scheduled_date <= end_date)
    
    schedules = query.order_by(Schedule.scheduled_date).all()
    return schedules

@router.get("/{schedule_id}", response_model=ScheduleSchema)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific schedule"""
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleSchema)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a schedule"""
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Update fields
    update_data = schedule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    # Mark as completed if end time is being set
    if schedule_update.status == "completed":
        schedule.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(schedule)
    
    return schedule

@router.post("/{schedule_id}/complete")
async def complete_schedule(
    schedule_id: int,
    completion_data: dict = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a schedule as completed"""
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    if schedule.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule is already completed"
        )
    
    # Update schedule status
    schedule.status = "completed"
    schedule.completed_at = datetime.utcnow()
    
    # Update completion percentage if provided
    if completion_data and 'completion_percentage' in completion_data:
        completion_percentage = completion_data['completion_percentage']
        if 0 <= completion_percentage <= 100:
            # Store completion data (could extend Schedule model to include this)
            pass
    
    db.commit()
    db.refresh(schedule)
    
    return {"message": "Schedule marked as completed", "schedule": schedule}

@router.post("/adapt")
async def adapt_schedules(
    material_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Adapt schedules based on performance data"""
    
    scheduler = StudyScheduler(db)
    adaptations = scheduler.adapt_schedule_based_on_performance(
        user_id=current_user.id,
        material_id=material_id
    )
    
    if not adaptations:
        return {"message": "No adaptations needed", "adaptations": []}
    
    # Apply adaptations to schedules
    applied_adaptations = []
    for adaptation in adaptations:
        schedule_id = adaptation['schedule_id']
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if schedule:
            # Apply specific adaptations
            for adapt_action in adaptation['adaptations']:
                if adapt_action == 'increase_review':
                    # Add additional review session
                    review_schedule = Schedule(
                        user_id=current_user.id,
                        material_id=schedule.material_id,
                        scheduled_date=schedule.scheduled_date + timedelta(days=1),
                        duration_minutes=schedule.duration_minutes // 2,
                        session_type='review',
                        priority_score=schedule.priority_score + 0.2,
                        cognitive_load_score=schedule.cognitive_load_score * 0.8,
                        repetition_interval=1,
                        start_position=schedule.start_position,
                        end_position=schedule.end_position,
                        status='scheduled'
                    )
                    db.add(review_schedule)
                
                elif adapt_action.startswith('reduce_interval_to_'):
                    interval = int(adapt_action.split('_')[-1])
                    schedule.repetition_interval = interval
                
                elif adapt_action.startswith('increase_interval_to_'):
                    interval = int(adapt_action.split('_')[-1])
                    schedule.repetition_interval = interval
                
                elif adapt_action.startswith('reschedule_to_'):
                    hour = int(adapt_action.split('_')[-1])
                    schedule.scheduled_date = schedule.scheduled_date.replace(hour=hour)
                
                elif adapt_action == 'reduce_session_duration':
                    schedule.duration_minutes = int(schedule.duration_minutes * 0.8)
            
            applied_adaptations.append(adaptation)
    
    db.commit()
    
    return {
        "message": f"Applied {len(applied_adaptations)} schedule adaptations",
        "adaptations": applied_adaptations
    }

@router.get("/upcoming/week")
async def get_weekly_schedule(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get upcoming week's schedule"""
    
    start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=7)
    
    schedules = db.query(Schedule).filter(
        Schedule.user_id == current_user.id,
        Schedule.scheduled_date >= start_date,
        Schedule.scheduled_date <= end_date,
        Schedule.status.in_(['scheduled', 'rescheduled'])
    ).order_by(Schedule.scheduled_date).all()
    
    # Group by date
    weekly_schedule = {}
    for schedule in schedules:
        date_key = schedule.scheduled_date.strftime('%Y-%m-%d')
        if date_key not in weekly_schedule:
            weekly_schedule[date_key] = []
        
        weekly_schedule[date_key].append({
            'id': schedule.id,
            'material_id': schedule.material_id,
            'time': schedule.scheduled_date.strftime('%H:%M'),
            'duration_minutes': schedule.duration_minutes,
            'session_type': schedule.session_type,
            'priority_score': schedule.priority_score
        })
    
    return {
        'week_start': start_date.isoformat(),
        'week_end': end_date.isoformat(),
        'schedule': weekly_schedule,
        'total_sessions': len(schedules)
    }

@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a schedule"""
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    db.delete(schedule)
    db.commit()
    
    return {"message": "Schedule deleted successfully"}
