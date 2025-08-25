from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import User, Material, Schedule, Performance, StudySession, Quiz
import math

class StudyScheduler:
    """Service for generating and adapting study schedules"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_initial_schedule(
        self,
        user_id: int,
        material_id: int,
        target_completion_date: datetime,
        daily_study_time: int = 60  # minutes per day
    ) -> List[Dict[str, Any]]:
        """
        Generate initial study schedule for a material
        
        Args:
            user_id: ID of the user
            material_id: ID of the material to schedule
            target_completion_date: When to complete the material
            daily_study_time: Available study time per day in minutes
            
        Returns:
            List of schedule entries
        """
        try:
            # Get user and material data
            user = self.db.query(User).filter(User.id == user_id).first()
            material = self.db.query(Material).filter(Material.id == material_id).first()
            
            if not user or not material:
                return []
            
            # Calculate total study sessions needed
            estimated_total_time = material.estimated_reading_time or 60  # fallback to 1 hour
            sessions_needed = math.ceil(estimated_total_time / daily_study_time)
            
            # Calculate days available
            days_available = (target_completion_date - datetime.utcnow()).days
            if days_available <= 0:
                days_available = 7  # Default to 1 week
            
            # Adjust session frequency
            if sessions_needed > days_available:
                # Need multiple sessions per day
                sessions_per_day = math.ceil(sessions_needed / days_available)
                session_duration = daily_study_time // sessions_per_day
            else:
                # One session per scheduled day
                sessions_per_day = 1
                session_duration = daily_study_time
                # Spread sessions across available days
                days_between_sessions = days_available // sessions_needed
            
            schedules = []
            current_date = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)  # Start at 9 AM
            
            # Get user's preferred study times
            preferred_times = user.preferred_study_times or {'morning': 0.7, 'afternoon': 0.5, 'evening': 0.3}
            
            for session_num in range(sessions_needed):
                # Determine optimal time based on user preferences
                study_hour = self._get_optimal_study_time(preferred_times, session_num)
                
                # Calculate schedule date
                if sessions_per_day == 1:
                    schedule_date = current_date + timedelta(days=session_num * days_between_sessions)
                else:
                    day_offset = session_num // sessions_per_day
                    session_of_day = session_num % sessions_per_day
                    schedule_date = current_date + timedelta(days=day_offset)
                    # Spread sessions throughout the day
                    schedule_date = schedule_date.replace(hour=study_hour + (session_of_day * 2))
                
                # Ensure we don't schedule past the target date
                if schedule_date > target_completion_date:
                    schedule_date = target_completion_date - timedelta(hours=(sessions_needed - session_num))
                
                # Calculate content section for this session
                total_words = material.word_count or 1000
                words_per_session = total_words // sessions_needed
                start_position = session_num * words_per_session
                end_position = min((session_num + 1) * words_per_session, total_words)
                
                # Determine session type (alternating study and review)
                session_type = "study" if session_num % 3 != 2 else "review"
                
                # Calculate cognitive load and priority
                cognitive_load = self._calculate_cognitive_load(
                    session_duration, 
                    material.difficulty_score or 0.5, 
                    user.cognitive_load_limit
                )
                
                priority_score = self._calculate_priority_score(
                    session_num, sessions_needed, material.difficulty_score or 0.5
                )
                
                schedule_entry = {
                    'user_id': user_id,
                    'material_id': material_id,
                    'scheduled_date': schedule_date,
                    'duration_minutes': session_duration,
                    'session_type': session_type,
                    'priority_score': priority_score,
                    'cognitive_load_score': cognitive_load,
                    'repetition_interval': 1,  # Initial interval
                    'start_position': start_position,
                    'end_position': end_position,
                    'status': 'scheduled'
                }
                
                schedules.append(schedule_entry)
            
            return schedules
            
        except Exception as e:
            print(f"Error generating schedule: {e}")
            return []
    
    def adapt_schedule_based_on_performance(
        self,
        user_id: int,
        material_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Adapt existing schedules based on user performance
        
        Args:
            user_id: ID of the user
            material_id: Optional specific material ID to adapt
            
        Returns:
            List of updated schedule entries
        """
        try:
            # Get user's performance data
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            # Get recent performance records
            performance_query = self.db.query(Performance).filter(Performance.user_id == user_id)
            if material_id:
                performance_query = performance_query.join(Quiz).filter(Quiz.material_id == material_id)
            
            recent_performances = performance_query.order_by(Performance.created_at.desc()).limit(10).all()
            
            # Get current schedules
            schedule_query = self.db.query(Schedule).filter(
                Schedule.user_id == user_id,
                Schedule.status == 'scheduled',
                Schedule.scheduled_date > datetime.utcnow()
            )
            if material_id:
                schedule_query = schedule_query.filter(Schedule.material_id == material_id)
            
            current_schedules = schedule_query.all()
            
            adaptations = []
            
            # Analyze performance patterns
            performance_analysis = self._analyze_performance(recent_performances)
            
            for schedule in current_schedules:
                adaptations_needed = []
                
                # Check if material needs more review based on performance
                material_performance = [p for p in recent_performances if p.quiz and p.quiz.material_id == schedule.material_id]
                
                if material_performance:
                    avg_score = sum(p.score for p in material_performance) / len(material_performance)
                    
                    # If performance is poor, increase review frequency
                    if avg_score < 0.6:
                        adaptations_needed.append('increase_review')
                        # Decrease interval for spaced repetition
                        new_interval = max(1, schedule.repetition_interval // 2)
                        adaptations_needed.append(f'reduce_interval_to_{new_interval}')
                    
                    # If performance is excellent, we can space out reviews more
                    elif avg_score > 0.9:
                        new_interval = min(14, schedule.repetition_interval * 2)
                        adaptations_needed.append(f'increase_interval_to_{new_interval}')
                
                # Adjust based on user's learning patterns
                if performance_analysis['struggles_with_difficulty']:
                    if schedule.material.difficulty_score > 0.7:
                        # Break difficult material into smaller chunks
                        adaptations_needed.append('reduce_session_duration')
                
                if performance_analysis['peak_performance_time']:
                    # Reschedule to optimal time
                    optimal_time = performance_analysis['peak_performance_time']
                    new_time = schedule.scheduled_date.replace(hour=optimal_time)
                    adaptations_needed.append(f'reschedule_to_{optimal_time}')
                
                # Apply adaptations
                if adaptations_needed:
                    adaptation_entry = {
                        'schedule_id': schedule.id,
                        'original_date': schedule.scheduled_date,
                        'adaptations': adaptations_needed,
                        'reason': 'performance_based_adaptation'
                    }
                    adaptations.append(adaptation_entry)
            
            return adaptations
            
        except Exception as e:
            print(f"Error adapting schedule: {e}")
            return []
    
    def calculate_spaced_repetition_interval(
        self,
        current_interval: int,
        performance_score: float,
        retention_rate: float = 0.7
    ) -> int:
        """
        Calculate next repetition interval using spaced repetition algorithm
        
        Args:
            current_interval: Current interval in days
            performance_score: Score from 0.0 to 1.0
            retention_rate: Target retention rate
            
        Returns:
            Next interval in days
        """
        # Base multiplier based on performance
        if performance_score >= 0.9:
            multiplier = 2.5
        elif performance_score >= 0.8:
            multiplier = 2.0
        elif performance_score >= 0.7:
            multiplier = 1.5
        elif performance_score >= 0.6:
            multiplier = 1.2
        else:
            # Poor performance - reduce interval
            multiplier = 0.8
        
        # Adjust based on retention rate
        retention_adjustment = retention_rate / 0.7  # Normalized to default 0.7
        multiplier *= retention_adjustment
        
        # Calculate new interval
        new_interval = int(current_interval * multiplier)
        
        # Ensure reasonable bounds
        new_interval = max(1, min(new_interval, 30))  # Between 1 and 30 days
        
        return new_interval
    
    def _get_optimal_study_time(self, preferred_times: Dict[str, float], session_num: int) -> int:
        """Get optimal study hour based on preferences"""
        # Convert preferences to hours
        time_scores = {
            9: preferred_times.get('morning', 0.7),   # 9 AM
            14: preferred_times.get('afternoon', 0.5), # 2 PM
            19: preferred_times.get('evening', 0.3)    # 7 PM
        }
        
        # Add some variation to avoid scheduling everything at the same time
        variation = (session_num % 3) - 1  # -1, 0, or 1
        
        # Find the best time
        best_hour = max(time_scores.keys(), key=lambda h: time_scores[h])
        
        return max(8, min(21, best_hour + variation))  # Keep within 8 AM to 9 PM
    
    def _calculate_cognitive_load(
        self, 
        duration_minutes: int, 
        difficulty_score: float, 
        user_limit: float
    ) -> float:
        """Calculate cognitive load for a study session"""
        # Base load from duration
        duration_load = duration_minutes / 120.0  # Normalize to 2-hour max
        
        # Difficulty contributes to cognitive load
        difficulty_load = difficulty_score
        
        # Combine factors
        total_load = (duration_load * 0.6) + (difficulty_load * 0.4)
        
        # Scale to user's limit
        return min(total_load / user_limit, 1.0)
    
    def _calculate_priority_score(
        self,
        session_num: int,
        total_sessions: int,
        difficulty_score: float
    ) -> float:
        """Calculate priority score for a session"""
        # Earlier sessions have higher priority
        position_priority = (total_sessions - session_num) / total_sessions
        
        # More difficult content gets higher priority
        difficulty_priority = difficulty_score
        
        # Combine factors
        return (position_priority * 0.7) + (difficulty_priority * 0.3)
    
    def _analyze_performance(self, performances: List[Performance]) -> Dict[str, Any]:
        """Analyze user performance patterns"""
        if not performances:
            return {
                'struggles_with_difficulty': False,
                'peak_performance_time': 9,  # Default to 9 AM
                'average_score': 0.5
            }
        
        # Calculate average score
        avg_score = sum(p.score for p in performances) / len(performances)
        
        # Check if user struggles with difficult content
        difficult_performances = [p for p in performances if p.difficulty_handled and p.difficulty_handled > 0.7]
        struggles_with_difficulty = False
        if difficult_performances:
            difficult_avg = sum(p.score for p in difficult_performances) / len(difficult_performances)
            struggles_with_difficulty = difficult_avg < avg_score * 0.8
        
        # Find peak performance time (simplified - would need more session data)
        peak_time = 9  # Default morning time
        
        return {
            'struggles_with_difficulty': struggles_with_difficulty,
            'peak_performance_time': peak_time,
            'average_score': avg_score,
            'total_performances': len(performances)
        }
