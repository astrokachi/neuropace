from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Performance, StudySession, Quiz, Material

class PerformanceTracker:
    """Service for tracking and analyzing user performance"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_quiz_performance(
        self,
        user_id: int,
        quiz_id: int,
        score: float,
        time_taken: float,
        questions_correct: int,
        questions_total: int,
        question_responses: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Record quiz performance metrics
        
        Args:
            user_id: ID of the user
            quiz_id: ID of the quiz taken
            score: Score from 0.0 to 1.0
            time_taken: Time taken in minutes
            questions_correct: Number of correct answers
            questions_total: Total number of questions
            question_responses: Detailed responses to questions
            
        Returns:
            Dictionary with recorded performance data
        """
        try:
            # Get quiz and material info for context
            quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
            if not quiz:
                return {'success': False, 'error': 'Quiz not found'}
            
            # Calculate additional metrics
            comprehension_speed = questions_total / time_taken if time_taken > 0 else 0
            difficulty_handled = quiz.difficulty_level
            
            # Create performance record
            performance = Performance(
                user_id=user_id,
                quiz_id=quiz_id,
                score=score,
                time_taken=time_taken,
                questions_correct=questions_correct,
                questions_total=questions_total,
                comprehension_speed=comprehension_speed,
                difficulty_handled=difficulty_handled,
                question_responses=question_responses or {}
            )
            
            self.db.add(performance)
            self.db.commit()
            
            # Update user's learning metrics
            self._update_user_metrics(user_id)
            
            # Analyze performance patterns
            analysis = self._analyze_recent_performance(user_id, quiz.material_id)
            
            return {
                'success': True,
                'performance_id': performance.id,
                'analysis': analysis
            }
            
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def record_study_session(
        self,
        user_id: int,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Record study session performance
        
        Args:
            user_id: ID of the user
            session_data: Dictionary containing session metrics
            
        Returns:
            Dictionary with recorded session data
        """
        try:
            # Calculate derived metrics
            duration = None
            reading_speed = None
            
            if 'end_time' in session_data and 'start_time' in session_data:
                duration = (session_data['end_time'] - session_data['start_time']).total_seconds() / 60
                
                if 'words_read' in session_data and duration > 0:
                    reading_speed = session_data['words_read'] / duration
            
            # Create study session record
            session = StudySession(
                user_id=user_id,
                schedule_id=session_data.get('schedule_id'),
                start_time=session_data['start_time'],
                end_time=session_data.get('end_time'),
                duration_minutes=duration,
                pages_read=session_data.get('pages_read', 0),
                words_read=session_data.get('words_read', 0),
                reading_speed=reading_speed,
                focus_score=session_data.get('focus_score', 0.5),
                interaction_count=session_data.get('interaction_count', 0),
                pause_count=session_data.get('pause_count', 0),
                total_pause_time=session_data.get('total_pause_time', 0.0),
                completion_percentage=session_data.get('completion_percentage', 0.0),
                self_rated_understanding=session_data.get('self_rated_understanding'),
                session_notes=session_data.get('session_notes')
            )
            
            self.db.add(session)
            self.db.commit()
            
            # Update user's reading metrics
            self._update_reading_metrics(user_id)
            
            return {
                'success': True,
                'session_id': session.id,
                'calculated_duration': duration,
                'calculated_reading_speed': reading_speed
            }
            
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_performance_analytics(
        self,
        user_id: int,
        material_id: Optional[int] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive performance analytics for a user
        
        Args:
            user_id: ID of the user
            material_id: Optional material ID to filter by
            days_back: Number of days to look back
            
        Returns:
            Dictionary with performance analytics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get quiz performances
            quiz_query = self.db.query(Performance).filter(
                Performance.user_id == user_id,
                Performance.created_at >= cutoff_date
            )
            
            if material_id:
                quiz_query = quiz_query.join(Quiz).filter(Quiz.material_id == material_id)
            
            quiz_performances = quiz_query.all()
            
            # Get study sessions
            session_query = self.db.query(StudySession).filter(
                StudySession.user_id == user_id,
                StudySession.start_time >= cutoff_date
            )
            
            study_sessions = session_query.all()
            
            # Calculate quiz metrics
            quiz_metrics = self._calculate_quiz_metrics(quiz_performances)
            
            # Calculate study session metrics
            session_metrics = self._calculate_session_metrics(study_sessions)
            
            # Calculate learning trends
            trends = self._calculate_learning_trends(quiz_performances, study_sessions)
            
            # Get user's current metrics
            user = self.db.query(User).filter(User.id == user_id).first()
            
            return {
                'success': True,
                'period': f'{days_back} days',
                'quiz_metrics': quiz_metrics,
                'session_metrics': session_metrics,
                'learning_trends': trends,
                'user_profile': {
                    'average_reading_speed': user.average_reading_speed if user else 200,
                    'retention_rate': user.retention_rate if user else 0.7,
                    'cognitive_load_limit': user.cognitive_load_limit if user else 1.0
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_learning_curve_data(self, user_id: int, material_id: int) -> Dict[str, Any]:
        """
        Get learning curve data for a specific material
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            
        Returns:
            Dictionary with learning curve data points
        """
        try:
            # Get all performances for this material
            performances = self.db.query(Performance).join(Quiz).filter(
                Performance.user_id == user_id,
                Quiz.material_id == material_id
            ).order_by(Performance.created_at).all()
            
            if not performances:
                return {
                    'success': True,
                    'data_points': [],
                    'trend': 'no_data'
                }
            
            # Create data points for learning curve
            data_points = []
            for i, perf in enumerate(performances):
                data_points.append({
                    'session_number': i + 1,
                    'score': perf.score,
                    'time_taken': perf.time_taken,
                    'comprehension_speed': perf.comprehension_speed,
                    'date': perf.created_at.isoformat(),
                    'difficulty': perf.difficulty_handled
                })
            
            # Calculate trend
            if len(performances) >= 3:
                recent_scores = [p.score for p in performances[-3:]]
                early_scores = [p.score for p in performances[:3]]
                
                recent_avg = sum(recent_scores) / len(recent_scores)
                early_avg = sum(early_scores) / len(early_scores)
                
                if recent_avg > early_avg + 0.1:
                    trend = 'improving'
                elif recent_avg < early_avg - 0.1:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'success': True,
                'data_points': data_points,
                'trend': trend,
                'total_sessions': len(performances)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _update_user_metrics(self, user_id: int):
        """Update user's learning metrics based on recent performance"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return
            
            # Get recent performances
            recent_performances = self.db.query(Performance).filter(
                Performance.user_id == user_id,
                Performance.created_at >= datetime.utcnow() - timedelta(days=30)
            ).limit(20).all()
            
            if recent_performances:
                # Update retention rate
                avg_score = sum(p.score for p in recent_performances) / len(recent_performances)
                user.retention_rate = (user.retention_rate * 0.7) + (avg_score * 0.3)
                
                # Update cognitive load limit based on performance under different loads
                high_load_performances = [p for p in recent_performances if hasattr(p, 'cognitive_load') and p.cognitive_load > 0.7]
                if high_load_performances:
                    high_load_avg = sum(p.score for p in high_load_performances) / len(high_load_performances)
                    if high_load_avg > 0.7:
                        user.cognitive_load_limit = min(1.5, user.cognitive_load_limit * 1.1)
                    elif high_load_avg < 0.5:
                        user.cognitive_load_limit = max(0.5, user.cognitive_load_limit * 0.9)
                
                self.db.commit()
                
        except Exception as e:
            print(f"Error updating user metrics: {e}")
            self.db.rollback()
    
    def _update_reading_metrics(self, user_id: int):
        """Update user's reading speed based on recent sessions"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return
            
            # Get recent study sessions with reading speed data
            recent_sessions = self.db.query(StudySession).filter(
                StudySession.user_id == user_id,
                StudySession.reading_speed.isnot(None),
                StudySession.start_time >= datetime.utcnow() - timedelta(days=30)
            ).limit(10).all()
            
            if recent_sessions:
                speeds = [s.reading_speed for s in recent_sessions if s.reading_speed > 0]
                if speeds:
                    avg_speed = sum(speeds) / len(speeds)
                    # Weighted average with existing speed
                    user.average_reading_speed = (user.average_reading_speed * 0.7) + (avg_speed * 0.3)
                    self.db.commit()
                    
        except Exception as e:
            print(f"Error updating reading metrics: {e}")
            self.db.rollback()
    
    def _calculate_quiz_metrics(self, performances: List[Performance]) -> Dict[str, Any]:
        """Calculate quiz performance metrics"""
        if not performances:
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'average_time': 0,
                'improvement_rate': 0
            }
        
        scores = [p.score for p in performances]
        times = [p.time_taken for p in performances if p.time_taken]
        
        # Calculate improvement rate
        improvement_rate = 0
        if len(scores) >= 2:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            improvement_rate = (sum(second_half)/len(second_half)) - (sum(first_half)/len(first_half))
        
        return {
            'total_quizzes': len(performances),
            'average_score': sum(scores) / len(scores),
            'average_time': sum(times) / len(times) if times else 0,
            'improvement_rate': improvement_rate,
            'score_range': {'min': min(scores), 'max': max(scores)},
            'consistency': 1 - (max(scores) - min(scores))  # Higher is more consistent
        }
    
    def _calculate_session_metrics(self, sessions: List[StudySession]) -> Dict[str, Any]:
        """Calculate study session metrics"""
        if not sessions:
            return {
                'total_sessions': 0,
                'total_study_time': 0,
                'average_session_duration': 0,
                'average_focus_score': 0
            }
        
        durations = [s.duration_minutes for s in sessions if s.duration_minutes]
        focus_scores = [s.focus_score for s in sessions]
        reading_speeds = [s.reading_speed for s in sessions if s.reading_speed]
        
        return {
            'total_sessions': len(sessions),
            'total_study_time': sum(durations),
            'average_session_duration': sum(durations) / len(durations) if durations else 0,
            'average_focus_score': sum(focus_scores) / len(focus_scores),
            'average_reading_speed': sum(reading_speeds) / len(reading_speeds) if reading_speeds else 0,
            'completion_rate': sum(s.completion_percentage for s in sessions) / len(sessions) / 100
        }
    
    def _calculate_learning_trends(
        self,
        performances: List[Performance],
        sessions: List[StudySession]
    ) -> Dict[str, Any]:
        """Calculate learning trends over time"""
        trends = {
            'score_trend': 'stable',
            'speed_trend': 'stable',
            'engagement_trend': 'stable'
        }
        
        # Score trend
        if len(performances) >= 4:
            recent_scores = [p.score for p in performances[-len(performances)//2:]]
            early_scores = [p.score for p in performances[:len(performances)//2]]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            early_avg = sum(early_scores) / len(early_scores)
            
            if recent_avg > early_avg + 0.05:
                trends['score_trend'] = 'improving'
            elif recent_avg < early_avg - 0.05:
                trends['score_trend'] = 'declining'
        
        # Reading speed trend
        session_speeds = [s.reading_speed for s in sessions if s.reading_speed and s.reading_speed > 0]
        if len(session_speeds) >= 4:
            recent_speeds = session_speeds[-len(session_speeds)//2:]
            early_speeds = session_speeds[:len(session_speeds)//2]
            
            recent_avg = sum(recent_speeds) / len(recent_speeds)
            early_avg = sum(early_speeds) / len(early_speeds)
            
            if recent_avg > early_avg * 1.1:
                trends['speed_trend'] = 'improving'
            elif recent_avg < early_avg * 0.9:
                trends['speed_trend'] = 'declining'
        
        # Engagement trend (based on focus scores)
        focus_scores = [s.focus_score for s in sessions]
        if len(focus_scores) >= 4:
            recent_focus = focus_scores[-len(focus_scores)//2:]
            early_focus = focus_scores[:len(focus_scores)//2]
            
            recent_avg = sum(recent_focus) / len(recent_focus)
            early_avg = sum(early_focus) / len(early_focus)
            
            if recent_avg > early_avg + 0.05:
                trends['engagement_trend'] = 'improving'
            elif recent_avg < early_avg - 0.05:
                trends['engagement_trend'] = 'declining'
        
        return trends
    
    def _analyze_recent_performance(self, user_id: int, material_id: int) -> Dict[str, Any]:
        """Analyze recent performance for a specific material"""
        try:
            # Get last 5 performances for this material
            recent_performances = self.db.query(Performance).join(Quiz).filter(
                Performance.user_id == user_id,
                Quiz.material_id == material_id
            ).order_by(Performance.created_at.desc()).limit(5).all()
            
            if not recent_performances:
                return {'status': 'no_data'}
            
            avg_score = sum(p.score for p in recent_performances) / len(recent_performances)
            avg_speed = sum(p.comprehension_speed for p in recent_performances if p.comprehension_speed) / len(recent_performances)
            
            # Determine learning status
            if avg_score >= 0.8:
                status = 'mastery'
                recommendation = 'Ready for advanced material or spaced review'
            elif avg_score >= 0.6:
                status = 'progressing'
                recommendation = 'Continue with current pace'
            else:
                status = 'struggling'
                recommendation = 'Consider reviewing fundamentals or reducing difficulty'
            
            return {
                'status': status,
                'average_score': avg_score,
                'average_speed': avg_speed,
                'recommendation': recommendation,
                'total_attempts': len(recent_performances)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
