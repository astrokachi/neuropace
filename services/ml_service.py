"""
Main ML Service for orchestrating all machine learning operations
Implements the ML pipeline described in the system architecture
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import math
import numpy as np
from sqlalchemy.orm import Session
from .document_processor import DocumentProcessor
from .quiz_generator import QuizGenerator  
from .spaced_repetition_scheduler import SpacedRepetitionScheduler
from .learning_analytics import LearningAnalytics

class MLService:
    """
    Main orchestration service for all ML operations
    Coordinates document processing, quiz generation, scheduling, and analytics
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.document_processor = DocumentProcessor()
        self.quiz_generator = QuizGenerator(db)
        self.scheduler = SpacedRepetitionScheduler(db)
        self.analytics = LearningAnalytics(db)
    
    def process_learning_material(
        self,
        user_id: int,
        file_content: bytes,
        filename: str,
        target_completion_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Complete ML pipeline for processing new learning material
        
        Args:
            user_id: ID of the user
            file_content: Raw file content
            filename: Name of the uploaded file
            target_completion_date: Optional target completion date
            
        Returns:
            Complete processing results with schedule and initial quiz
        """
        try:
            # Step 1: Document Processing Pipeline
            doc_result = self.document_processor.process_document(file_content, filename)
            if not doc_result['success']:
                return doc_result
            
            # Step 2: Content Analysis and Segmentation
            content_analysis = self.document_processor.analyze_content_structure(
                doc_result['full_text']
            )
            
            # Step 3: Generate Initial Assessment Quiz
            initial_quiz = self.quiz_generator.generate_adaptive_quiz(
                text=doc_result['full_text'],
                difficulty_level=content_analysis['estimated_difficulty'],
                num_questions=5,
                quiz_type='assessment'
            )
            
            # Step 4: Create Personalized Study Schedule using HLR
            if not target_completion_date:
                target_completion_date = datetime.utcnow() + timedelta(days=14)
                
            schedule = self.scheduler.generate_hlr_schedule(
                user_id=user_id,
                content_analysis=content_analysis,
                target_date=target_completion_date,
                initial_difficulty=content_analysis['estimated_difficulty']
            )
            
            # Step 5: Initialize Learning Analytics Baseline
            baseline_metrics = self.analytics.initialize_material_baseline(
                user_id=user_id,
                content_analysis=content_analysis
            )
            
            return {
                'success': True,
                'document_analysis': content_analysis,
                'initial_quiz': initial_quiz,
                'study_schedule': schedule,
                'baseline_metrics': baseline_metrics,
                'processing_metadata': {
                    'processed_at': datetime.utcnow().isoformat(),
                    'ml_version': '1.0',
                    'pipeline_stages': ['document_processing', 'content_analysis', 'quiz_generation', 'hlr_scheduling', 'analytics_init']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'ML pipeline failed: {str(e)}',
                'stage': 'ml_orchestration'
            }
    
    def adapt_learning_path(
        self,
        user_id: int,
        material_id: int,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adaptive learning path adjustment based on performance
        Implements continuous optimization of the learning experience
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            performance_data: Latest performance metrics
            
        Returns:
            Updated learning path with adaptations
        """
        try:
            # Step 1: Analyze Current Performance Patterns
            performance_analysis = self.analytics.analyze_learning_patterns(
                user_id=user_id,
                material_id=material_id
            )
            
            # Step 2: Update Half-Life Regression Model
            hlr_update = self.scheduler.update_hlr_model(
                user_id=user_id,
                material_id=material_id,
                performance_data=performance_data
            )
            
            # Step 3: Adaptive Schedule Optimization
            schedule_adaptations = self.scheduler.optimize_schedule_intervals(
                user_id=user_id,
                material_id=material_id,
                performance_analysis=performance_analysis
            )
            
            # Step 4: Generate Adaptive Quizzes
            adaptive_quizzes = self.quiz_generator.generate_adaptive_quiz_sequence(
                user_id=user_id,
                material_id=material_id,
                difficulty_progression=performance_analysis['difficulty_progression']
            )
            
            # Step 5: Cognitive Load Management
            cognitive_load_adjustment = self.analytics.calculate_cognitive_load_optimization(
                user_id=user_id,
                current_performance=performance_analysis
            )
            
            return {
                'success': True,
                'adaptations': {
                    'performance_analysis': performance_analysis,
                    'hlr_model_update': hlr_update,
                    'schedule_changes': schedule_adaptations,
                    'adaptive_quizzes': adaptive_quizzes,
                    'cognitive_load_adjustments': cognitive_load_adjustment
                },
                'adaptation_metadata': {
                    'adapted_at': datetime.utcnow().isoformat(),
                    'adaptation_trigger': 'performance_feedback',
                    'confidence_score': performance_analysis.get('confidence_score', 0.7)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Adaptation pipeline failed: {str(e)}',
                'stage': 'learning_adaptation'
            }
    
    def predict_learning_outcomes(
        self,
        user_id: int,
        material_id: int,
        time_horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Predictive modeling for learning outcomes
        Uses ML models to forecast user progress and retention
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            time_horizon_days: Prediction horizon in days
            
        Returns:
            Predicted learning outcomes and recommendations
        """
        try:
            # Get user's learning history
            learning_history = self.analytics.get_comprehensive_learning_history(
                user_id=user_id,
                material_id=material_id
            )
            
            # Predict retention rates using HLR
            retention_predictions = self.scheduler.predict_retention_curve(
                user_id=user_id,
                material_id=material_id,
                time_horizon=time_horizon_days
            )
            
            # Predict optimal study intervals
            interval_predictions = self.scheduler.predict_optimal_intervals(
                user_id=user_id,
                learning_history=learning_history
            )
            
            # Predict learning velocity
            velocity_prediction = self.analytics.predict_learning_velocity(
                user_id=user_id,
                current_performance=learning_history
            )
            
            # Generate personalized recommendations
            recommendations = self._generate_personalized_recommendations(
                learning_history=learning_history,
                retention_predictions=retention_predictions,
                velocity_prediction=velocity_prediction
            )
            
            return {
                'success': True,
                'predictions': {
                    'retention_curve': retention_predictions,
                    'optimal_intervals': interval_predictions,
                    'learning_velocity': velocity_prediction,
                    'completion_probability': self._calculate_completion_probability(
                        velocity_prediction, time_horizon_days
                    )
                },
                'recommendations': recommendations,
                'prediction_metadata': {
                    'model_version': '1.0',
                    'prediction_date': datetime.utcnow().isoformat(),
                    'confidence_interval': '95%',
                    'time_horizon_days': time_horizon_days
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Prediction pipeline failed: {str(e)}',
                'stage': 'learning_prediction'
            }
    
    def optimize_study_session(
        self,
        user_id: int,
        material_id: int,
        available_time_minutes: int,
        current_cognitive_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Real-time study session optimization
        Optimizes content selection and pacing for maximum learning efficiency
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            available_time_minutes: Available study time
            current_cognitive_state: Optional current cognitive state data
            
        Returns:
            Optimized study session plan
        """
        try:
            # Get current user state and preferences
            user_profile = self.analytics.get_user_learning_profile(user_id)
            
            # Analyze optimal content sections for this session
            content_optimization = self.document_processor.optimize_content_selection(
                material_id=material_id,
                available_time=available_time_minutes,
                user_reading_speed=user_profile['reading_speed'],
                difficulty_preference=user_profile['difficulty_tolerance']
            )
            
            # Optimize cognitive load for session
            cognitive_optimization = self.analytics.optimize_session_cognitive_load(
                user_id=user_id,
                content_sections=content_optimization['recommended_sections'],
                available_time=available_time_minutes,
                current_state=current_cognitive_state
            )
            
            # Generate session-specific quizzes
            session_quizzes = self.quiz_generator.generate_session_quizzes(
                content_sections=content_optimization['recommended_sections'],
                user_performance_level=user_profile['current_level']
            )
            
            # Create adaptive session timeline
            session_timeline = self._create_adaptive_session_timeline(
                content_sections=content_optimization['recommended_sections'],
                quizzes=session_quizzes,
                available_time=available_time_minutes,
                cognitive_optimization=cognitive_optimization
            )
            
            return {
                'success': True,
                'session_plan': {
                    'recommended_sections': content_optimization['recommended_sections'],
                    'quiz_checkpoints': session_quizzes,
                    'session_timeline': session_timeline,
                    'cognitive_load_plan': cognitive_optimization,
                    'break_recommendations': self._calculate_optimal_breaks(available_time_minutes)
                },
                'optimization_metadata': {
                    'optimized_at': datetime.utcnow().isoformat(),
                    'optimization_factors': ['content_difficulty', 'cognitive_load', 'time_constraints', 'user_preferences']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Session optimization failed: {str(e)}',
                'stage': 'session_optimization'
            }
    
    def _generate_personalized_recommendations(
        self,
        learning_history: Dict[str, Any],
        retention_predictions: Dict[str, Any],
        velocity_prediction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        # Retention-based recommendations
        if retention_predictions.get('declining_sections'):
            recommendations.append({
                'type': 'retention_alert',
                'priority': 'high',
                'message': 'Some material sections may need review to prevent forgetting',
                'action': 'schedule_review',
                'sections': retention_predictions['declining_sections']
            })
        
        # Velocity-based recommendations
        if velocity_prediction.get('below_target'):
            recommendations.append({
                'type': 'pace_adjustment',
                'priority': 'medium', 
                'message': 'Consider adjusting study pace or session duration',
                'action': 'modify_schedule',
                'suggested_changes': velocity_prediction['suggested_adjustments']
            })
        
        # Cognitive load recommendations
        if learning_history.get('high_cognitive_load_sessions', 0) > 3:
            recommendations.append({
                'type': 'cognitive_load',
                'priority': 'medium',
                'message': 'Recent sessions may have been too challenging',
                'action': 'reduce_difficulty',
                'suggestion': 'Break complex material into smaller sections'
            })
        
        return recommendations
    
    def _calculate_completion_probability(
        self,
        velocity_prediction: Dict[str, Any],
        time_horizon_days: int
    ) -> float:
        """Calculate probability of material completion within time horizon"""
        expected_velocity = velocity_prediction.get('expected_daily_progress', 0.05)
        current_progress = velocity_prediction.get('current_completion_rate', 0.0)
        
        projected_completion = current_progress + (expected_velocity * time_horizon_days)
        
        # Add uncertainty factor
        uncertainty_factor = 0.1  # 10% uncertainty
        return max(0.0, min(1.0, projected_completion - uncertainty_factor))
    
    def _create_adaptive_session_timeline(
        self,
        content_sections: List[Dict[str, Any]],
        quizzes: List[Dict[str, Any]],
        available_time: int,
        cognitive_optimization: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create an adaptive timeline for the study session"""
        timeline = []
        current_time = 0
        
        for i, section in enumerate(content_sections):
            # Add content study block
            study_duration = min(section['estimated_time'], 
                               cognitive_optimization['max_focus_duration'])
            
            timeline.append({
                'type': 'study',
                'start_time': current_time,
                'duration': study_duration,
                'content': section,
                'cognitive_load': section.get('difficulty_score', 0.5)
            })
            current_time += study_duration
            
            # Add quiz if available
            if i < len(quizzes):
                timeline.append({
                    'type': 'assessment',
                    'start_time': current_time,
                    'duration': 5,  # 5 minutes for quiz
                    'quiz': quizzes[i]
                })
                current_time += 5
            
            # Add break if needed
            if current_time < available_time - 10 and i < len(content_sections) - 1:
                break_duration = cognitive_optimization.get('recommended_break_duration', 5)
                timeline.append({
                    'type': 'break',
                    'start_time': current_time,
                    'duration': break_duration
                })
                current_time += break_duration
        
        return timeline
    
    def _calculate_optimal_breaks(self, available_time: int) -> List[Dict[str, Any]]:
        """Calculate optimal break intervals for the session"""
        breaks = []
        
        # Use research-based break intervals (Pomodoro technique with adaptations)
        if available_time >= 60:  # For sessions 1 hour or longer
            break_intervals = [25, 50, 75]  # Every 25 minutes
            for interval in break_intervals:
                if interval < available_time - 10:
                    breaks.append({
                        'time': interval,
                        'duration': 5 if interval != 50 else 10,  # Longer break at halfway point
                        'type': 'cognitive_refresh'
                    })
        
        return breaks