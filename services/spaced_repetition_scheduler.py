"""
Advanced Spaced Repetition Scheduler with Half-Life Regression (HLR)
Implements Duolingo-inspired adaptive scheduling algorithm
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import math
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import User, Material, Schedule, Performance, StudySession, Quiz

class SpacedRepetitionScheduler:
    """
    Advanced spaced repetition scheduler using Half-Life Regression
    Implements adaptive scheduling based on individual learning patterns
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # HLR model parameters (based on Duolingo research)
        self.hlr_params = {
            'initial_stability': 2.5,  # Initial memory stability in days
            'difficulty_weight': -0.05,  # Weight for item difficulty
            'previous_successes_weight': 0.15,  # Weight for previous successes
            'previous_failures_weight': -0.077,  # Weight for previous failures
            'elapsed_time_weight': 0.05,  # Weight for elapsed time since last review
            'lag_time_weight': 0.112,  # Weight for lag time (delay in review)
            'decay_factor': -0.105,  # Exponential decay factor
            'threshold_recall_probability': 0.85  # Target recall probability
        }
        
        # Cognitive load management parameters
        self.cognitive_params = {
            'max_daily_cognitive_load': 1.0,
            'optimal_session_load': 0.6,
            'load_recovery_rate': 0.2,  # Per hour
            'difficulty_cognitive_multiplier': 1.5
        }
    
    def generate_hlr_schedule(
        self,
        user_id: int,
        content_analysis: Dict[str, Any],
        target_date: datetime,
        initial_difficulty: float
    ) -> Dict[str, Any]:
        """
        Generate initial schedule using Half-Life Regression
        
        Args:
            user_id: ID of the user
            content_analysis: Content analysis from document processor
            target_date: Target completion date
            initial_difficulty: Initial difficulty assessment
            
        Returns:
            HLR-based schedule with adaptive intervals
        """
        try:
            # Get user's learning profile
            user_profile = self._get_user_hlr_profile(user_id)
            
            # Calculate content segments for scheduling
            content_segments = self._prepare_content_segments(content_analysis)
            
            # Initialize HLR model for each segment
            hlr_models = self._initialize_hlr_models(content_segments, initial_difficulty)
            
            # Generate adaptive schedule
            schedule_entries = self._generate_adaptive_schedule(
                user_id, user_profile, hlr_models, target_date
            )
            
            # Optimize schedule for cognitive load
            optimized_schedule = self._optimize_cognitive_load_distribution(
                schedule_entries, user_profile
            )
            
            # Calculate schedule metadata
            schedule_metadata = self._calculate_schedule_metadata(optimized_schedule)
            
            return {
                'success': True,
                'schedule_entries': optimized_schedule,
                'hlr_models': hlr_models,
                'schedule_metadata': schedule_metadata,
                'optimization_info': {
                    'algorithm': 'half_life_regression',
                    'target_recall_probability': self.hlr_params['threshold_recall_probability'],
                    'cognitive_load_optimized': True,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'HLR schedule generation failed: {str(e)}'
            }
    
    def update_hlr_model(
        self,
        user_id: int,
        material_id: int,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update HLR model based on new performance data
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            performance_data: Latest performance metrics
            
        Returns:
            Updated HLR model parameters
        """
        try:
            # Get current HLR state
            current_hlr_state = self._get_current_hlr_state(user_id, material_id)
            
            # Calculate new memory stability based on performance
            new_stability = self._calculate_memory_stability(
                current_hlr_state, performance_data
            )
            
            # Update difficulty estimate
            updated_difficulty = self._update_difficulty_estimate(
                current_hlr_state, performance_data
            )
            
            # Calculate next optimal interval
            next_interval = self._calculate_optimal_interval(
                new_stability, self.hlr_params['threshold_recall_probability']
            )
            
            # Update HLR parameters based on learning
            updated_params = self._update_hlr_parameters(
                current_hlr_state, performance_data, new_stability
            )
            
            return {
                'success': True,
                'updated_stability': new_stability,
                'updated_difficulty': updated_difficulty,
                'next_optimal_interval': next_interval,
                'updated_parameters': updated_params,
                'model_confidence': self._calculate_model_confidence(current_hlr_state),
                'update_metadata': {
                    'updated_at': datetime.utcnow().isoformat(),
                    'performance_score': performance_data.get('score', 0),
                    'model_version': '2.0'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'HLR model update failed: {str(e)}'
            }
    
    def optimize_schedule_intervals(
        self,
        user_id: int,
        material_id: int,
        performance_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize schedule intervals based on performance analysis
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            performance_analysis: Performance analysis data
            
        Returns:
            Optimized schedule intervals
        """
        try:
            # Get current scheduled items
            current_schedules = self._get_current_schedules(user_id, material_id)
            
            # Calculate interval optimizations for each scheduled item
            interval_optimizations = []
            
            for schedule in current_schedules:
                # Get HLR state for this item
                hlr_state = self._get_schedule_hlr_state(schedule)
                
                # Calculate optimal interval based on current performance
                optimal_interval = self._calculate_performance_based_interval(
                    hlr_state, performance_analysis
                )
                
                # Calculate cognitive load adjustment
                cognitive_adjustment = self._calculate_cognitive_load_adjustment(
                    schedule, performance_analysis, user_id
                )
                
                # Combine optimizations
                final_interval = self._combine_interval_optimizations(
                    optimal_interval, cognitive_adjustment
                )
                
                # Check if optimization is significant enough
                if self._is_optimization_significant(schedule, final_interval):
                    interval_optimizations.append({
                        'schedule_id': schedule.id,
                        'current_interval': schedule.repetition_interval,
                        'optimized_interval': final_interval,
                        'optimization_reason': self._get_optimization_reason(
                            schedule, final_interval, performance_analysis
                        ),
                        'expected_improvement': self._calculate_expected_improvement(
                            schedule, final_interval
                        )
                    })
            
            # Optimize overall schedule balance
            balanced_optimizations = self._balance_schedule_optimizations(
                interval_optimizations, user_id
            )
            
            return {
                'success': True,
                'interval_optimizations': balanced_optimizations,
                'optimization_summary': {
                    'total_items_optimized': len(balanced_optimizations),
                    'average_interval_change': self._calculate_average_change(balanced_optimizations),
                    'expected_performance_improvement': self._calculate_overall_improvement(balanced_optimizations)
                },
                'optimization_metadata': {
                    'optimized_at': datetime.utcnow().isoformat(),
                    'optimization_algorithm': 'hlr_performance_based',
                    'user_performance_level': performance_analysis.get('performance_patterns', {}).get('average_score', 0.5)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Schedule optimization failed: {str(e)}'
            }
    
    def predict_retention_curve(
        self,
        user_id: int,
        material_id: int,
        time_horizon: int
    ) -> Dict[str, Any]:
        """
        Predict retention curve using HLR model
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            time_horizon: Prediction horizon in days
            
        Returns:
            Predicted retention curve data
        """
        try:
            # Get current HLR states for all material segments
            hlr_states = self._get_material_hlr_states(user_id, material_id)
            
            # Generate retention predictions for each segment
            retention_predictions = []
            
            for segment_id, hlr_state in hlr_states.items():
                segment_curve = self._predict_segment_retention(
                    hlr_state, time_horizon
                )
                retention_predictions.append({
                    'segment_id': segment_id,
                    'retention_curve': segment_curve,
                    'half_life': hlr_state['memory_stability'],
                    'current_strength': hlr_state['memory_strength']
                })
            
            # Calculate overall material retention curve
            overall_retention = self._calculate_overall_retention_curve(
                retention_predictions, time_horizon
            )
            
            # Identify critical review points
            critical_points = self._identify_critical_review_points(
                overall_retention, self.hlr_params['threshold_recall_probability']
            )
            
            # Calculate forgetting curve parameters
            forgetting_curve_params = self._calculate_forgetting_curve_parameters(
                hlr_states, retention_predictions
            )
            
            return {
                'success': True,
                'overall_retention_curve': overall_retention,
                'segment_predictions': retention_predictions,
                'critical_review_points': critical_points,
                'forgetting_curve_parameters': forgetting_curve_params,
                'prediction_metadata': {
                    'prediction_date': datetime.utcnow().isoformat(),
                    'time_horizon_days': time_horizon,
                    'model_confidence': self._calculate_prediction_confidence(hlr_states),
                    'segments_analyzed': len(hlr_states)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Retention curve prediction failed: {str(e)}'
            }
    
    def predict_optimal_intervals(
        self,
        user_id: int,
        learning_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict optimal intervals for future learning
        
        Args:
            user_id: ID of the user
            learning_history: Comprehensive learning history
            
        Returns:
            Predicted optimal intervals
        """
        try:
            # Analyze historical interval effectiveness
            interval_effectiveness = self._analyze_interval_effectiveness(learning_history)
            
            # Calculate user-specific HLR parameters
            personalized_params = self._calculate_personalized_hlr_params(
                user_id, learning_history
            )
            
            # Predict optimal intervals for different difficulty levels
            interval_predictions = {}
            difficulty_levels = [0.3, 0.5, 0.7, 0.9]
            
            for difficulty in difficulty_levels:
                optimal_sequence = self._predict_optimal_sequence(
                    personalized_params, difficulty, interval_effectiveness
                )
                interval_predictions[f'difficulty_{difficulty}'] = optimal_sequence
            
            # Calculate adaptive interval recommendations
            adaptive_recommendations = self._generate_adaptive_interval_recommendations(
                interval_predictions, learning_history
            )
            
            return {
                'success': True,
                'interval_predictions': interval_predictions,
                'adaptive_recommendations': adaptive_recommendations,
                'personalized_parameters': personalized_params,
                'interval_effectiveness_analysis': interval_effectiveness,
                'prediction_metadata': {
                    'prediction_date': datetime.utcnow().isoformat(),
                    'personalization_confidence': self._calculate_personalization_confidence(learning_history),
                    'recommendations_based_on': 'hlr_historical_analysis'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Optimal interval prediction failed: {str(e)}'
            }
    
    # Core HLR algorithm implementation
    
    def _calculate_memory_stability(
        self,
        hlr_state: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> float:
        """Calculate memory stability using HLR algorithm"""
        
        # Get performance metrics
        success = 1 if performance_data.get('score', 0) >= 0.7 else 0
        response_time = performance_data.get('time_taken', 10)  # Default 10 seconds
        difficulty = hlr_state.get('difficulty', 0.5)
        
        # Get previous performance history
        previous_successes = hlr_state.get('success_count', 0)
        previous_failures = hlr_state.get('failure_count', 0)
        
        # Calculate elapsed time since last review
        last_review = hlr_state.get('last_review_date')
        if last_review:
            elapsed_days = (datetime.utcnow() - last_review).days
        else:
            elapsed_days = 0
        
        # Calculate lag time (delay from scheduled review)
        scheduled_date = hlr_state.get('scheduled_date')
        if scheduled_date and datetime.utcnow() > scheduled_date:
            lag_days = (datetime.utcnow() - scheduled_date).days
        else:
            lag_days = 0
        
        # HLR stability calculation
        log_stability = (
            math.log(max(self.hlr_params['initial_stability'], 0.1)) +
            self.hlr_params['difficulty_weight'] * difficulty +
            self.hlr_params['previous_successes_weight'] * previous_successes +
            self.hlr_params['previous_failures_weight'] * previous_failures +
            self.hlr_params['elapsed_time_weight'] * elapsed_days +
            self.hlr_params['lag_time_weight'] * lag_days
        )
        
        # Convert back to days and apply success/failure modifier
        stability = math.exp(log_stability)
        
        # Update based on current performance
        if success:
            stability *= (1.3 + (response_time / 100))  # Faster response = better memory
        else:
            stability *= 0.6  # Failure decreases stability
        
        # Ensure reasonable bounds
        return max(0.5, min(30.0, stability))
    
    def _calculate_recall_probability(
        self,
        stability: float,
        elapsed_time: float
    ) -> float:
        """Calculate recall probability using exponential decay"""
        if stability <= 0:
            return 0.0
        
        # Exponential decay function: P(recall) = 2^(-elapsed_time/stability)
        recall_probability = math.pow(2, -elapsed_time / stability)
        return max(0.0, min(1.0, recall_probability))
    
    def _calculate_optimal_interval(
        self,
        stability: float,
        target_recall_probability: float
    ) -> int:
        """Calculate optimal interval for target recall probability"""
        if stability <= 0 or target_recall_probability <= 0:
            return 1
        
        # Solve for time: target_recall = 2^(-time/stability)
        # time = -stability * log2(target_recall)
        optimal_time = -stability * math.log2(target_recall_probability)
        
        # Convert to days and ensure reasonable bounds
        optimal_days = max(1, min(30, int(round(optimal_time))))
        return optimal_days
    
    def _update_difficulty_estimate(
        self,
        hlr_state: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> float:
        """Update difficulty estimate based on performance"""
        current_difficulty = hlr_state.get('difficulty', 0.5)
        score = performance_data.get('score', 0)
        time_taken = performance_data.get('time_taken', 10)
        
        # Calculate difficulty indicators
        score_indicator = 1 - score  # Lower score = higher difficulty
        time_indicator = min(1.0, time_taken / 60)  # Longer time = higher difficulty
        
        # Weighted update
        difficulty_update = (score_indicator * 0.7) + (time_indicator * 0.3)
        
        # Smooth update using exponential moving average
        alpha = 0.3  # Learning rate
        new_difficulty = (1 - alpha) * current_difficulty + alpha * difficulty_update
        
        return max(0.0, min(1.0, new_difficulty))
    
    def _get_user_hlr_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user's HLR learning profile"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # Get historical performance for personalization
        recent_performances = self.db.query(Performance).filter(
            Performance.user_id == user_id
        ).order_by(Performance.created_at.desc()).limit(20).all()
        
        # Calculate personalized HLR parameters
        if recent_performances:
            avg_score = sum(p.score for p in recent_performances) / len(recent_performances)
            avg_time = sum(p.time_taken for p in recent_performances if p.time_taken) / len(recent_performances)
        else:
            avg_score = 0.7
            avg_time = 15
        
        # Adjust HLR parameters based on user performance
        personalized_params = self.hlr_params.copy()
        
        # Better performers can handle longer intervals
        if avg_score > 0.8:
            personalized_params['threshold_recall_probability'] = 0.8
        elif avg_score < 0.6:
            personalized_params['threshold_recall_probability'] = 0.9
        
        return {
            'user_id': user_id,
            'average_performance': avg_score,
            'average_response_time': avg_time,
            'cognitive_capacity': getattr(user, 'cognitive_load_limit', 0.8) if user else 0.8,
            'learning_rate': min(1.0, avg_score + 0.2),
            'hlr_parameters': personalized_params
        }
    
    def _prepare_content_segments(self, content_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare content segments for HLR scheduling"""
        segments = content_analysis.get('content_segments', [])
        
        prepared_segments = []
        for i, segment in enumerate(segments):
            prepared_segments.append({
                'segment_id': f'segment_{i+1}',
                'content': segment.get('content', ''),
                'word_count': segment.get('word_count', 0),
                'difficulty': segment.get('difficulty_score', 0.5),
                'estimated_study_time': segment.get('estimated_reading_time', 15),
                'cognitive_load': segment.get('cognitive_load', 0.5),
                'key_concepts': segment.get('key_concepts', [])
            })
        
        return prepared_segments
    
    def _initialize_hlr_models(
        self,
        content_segments: List[Dict[str, Any]],
        initial_difficulty: float
    ) -> Dict[str, Dict[str, Any]]:
        """Initialize HLR models for content segments"""
        hlr_models = {}
        
        for segment in content_segments:
            segment_id = segment['segment_id']
            
            hlr_models[segment_id] = {
                'segment_id': segment_id,
                'difficulty': segment['difficulty'],
                'memory_stability': self.hlr_params['initial_stability'],
                'memory_strength': 1.0,
                'success_count': 0,
                'failure_count': 0,
                'last_review_date': None,
                'scheduled_date': None,
                'repetition_number': 0,
                'cognitive_load': segment['cognitive_load'],
                'initial_interval': self._calculate_initial_interval(segment['difficulty'])
            }
        
        return hlr_models
    
    def _calculate_initial_interval(self, difficulty: float) -> int:
        """Calculate initial review interval based on difficulty"""
        base_interval = 2  # 2 days base
        difficulty_adjustment = 1 - (difficulty * 0.5)  # Easier content = longer interval
        return max(1, int(base_interval * difficulty_adjustment))
    
    def _generate_adaptive_schedule(
        self,
        user_id: int,
        user_profile: Dict[str, Any],
        hlr_models: Dict[str, Dict[str, Any]],
        target_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate adaptive schedule using HLR models"""
        schedule_entries = []
        current_date = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Calculate total available days
        available_days = max(7, (target_date - current_date).days)
        
        for segment_id, hlr_model in hlr_models.items():
            # Generate review schedule for this segment
            segment_schedule = self._generate_segment_schedule(
                user_id, segment_id, hlr_model, current_date, available_days, user_profile
            )
            schedule_entries.extend(segment_schedule)
        
        # Sort by scheduled date
        schedule_entries.sort(key=lambda x: x['scheduled_date'])
        
        return schedule_entries
    
    def _generate_segment_schedule(
        self,
        user_id: int,
        segment_id: str,
        hlr_model: Dict[str, Any],
        start_date: datetime,
        available_days: int,
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate schedule for a single content segment"""
        schedule = []
        current_date = start_date
        repetition_number = 0
        current_interval = hlr_model['initial_interval']
        
        # Generate review sessions until target mastery or end date
        while current_date <= start_date + timedelta(days=available_days) and repetition_number < 8:
            # Create schedule entry
            schedule_entry = {
                'user_id': user_id,
                'segment_id': segment_id,
                'scheduled_date': current_date,
                'repetition_number': repetition_number,
                'repetition_interval': current_interval,
                'estimated_duration': self._calculate_session_duration(hlr_model, repetition_number),
                'session_type': self._determine_session_type(repetition_number),
                'difficulty_level': hlr_model['difficulty'],
                'cognitive_load': self._calculate_session_cognitive_load(hlr_model, repetition_number),
                'expected_recall_probability': self._calculate_recall_probability(
                    hlr_model['memory_stability'], current_interval
                ),
                'priority_score': self._calculate_priority_score(hlr_model, repetition_number),
                'status': 'scheduled'
            }
            
            schedule.append(schedule_entry)
            
            # Calculate next interval using HLR
            next_interval = self._predict_next_interval(hlr_model, repetition_number)
            current_date += timedelta(days=next_interval)
            repetition_number += 1
            current_interval = next_interval
        
        return schedule
    
    def _predict_next_interval(self, hlr_model: Dict[str, Any], repetition_number: int) -> int:
        """Predict next optimal interval"""
        # Simulate performance for interval calculation
        # In real implementation, this would be updated after actual performance
        simulated_success_rate = max(0.5, 1.0 - hlr_model['difficulty'] * 0.4)
        
        if simulated_success_rate > 0.8:
            # Good performance, increase interval
            multiplier = 2.0 + (repetition_number * 0.2)
        elif simulated_success_rate > 0.6:
            # Average performance, moderate increase
            multiplier = 1.5 + (repetition_number * 0.1)
        else:
            # Poor performance, conservative increase
            multiplier = 1.2
        
        base_interval = hlr_model.get('initial_interval', 2)
        next_interval = int(base_interval * multiplier)
        
        return max(1, min(14, next_interval))  # Bounds: 1-14 days
    
    def _calculate_session_duration(self, hlr_model: Dict[str, Any], repetition_number: int) -> int:
        """Calculate session duration based on repetition number and difficulty"""
        base_duration = 20  # 20 minutes base
        difficulty_multiplier = 1 + (hlr_model['difficulty'] * 0.3)
        repetition_adjustment = max(0.7, 1 - (repetition_number * 0.1))  # Shorter for later repetitions
        
        duration = int(base_duration * difficulty_multiplier * repetition_adjustment)
        return max(10, min(60, duration))  # Bounds: 10-60 minutes
    
    def _determine_session_type(self, repetition_number: int) -> str:
        """Determine session type based on repetition number"""
        if repetition_number == 0:
            return 'initial_learning'
        elif repetition_number <= 2:
            return 'active_recall'
        elif repetition_number <= 4:
            return 'spaced_review'
        else:
            return 'maintenance_review'
    
    def _calculate_session_cognitive_load(self, hlr_model: Dict[str, Any], repetition_number: int) -> float:
        """Calculate cognitive load for session"""
        base_load = hlr_model['cognitive_load']
        repetition_reduction = repetition_number * 0.1  # Load decreases with repetition
        
        adjusted_load = max(0.2, base_load - repetition_reduction)
        return round(adjusted_load, 2)
    
    def _calculate_priority_score(self, hlr_model: Dict[str, Any], repetition_number: int) -> float:
        """Calculate priority score for scheduling"""
        difficulty_priority = hlr_model['difficulty']  # Higher difficulty = higher priority
        urgency_priority = 1.0 / (repetition_number + 1)  # First reviews have higher priority
        
        priority = (difficulty_priority * 0.6) + (urgency_priority * 0.4)
        return round(priority, 3)
    
    def _optimize_cognitive_load_distribution(
        self,
        schedule_entries: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Optimize cognitive load distribution across schedule"""
        # Group by date
        daily_schedules = {}
        for entry in schedule_entries:
            date_key = entry['scheduled_date'].date()
            if date_key not in daily_schedules:
                daily_schedules[date_key] = []
            daily_schedules[date_key].append(entry)
        
        # Optimize each day's cognitive load
        optimized_entries = []
        user_capacity = user_profile.get('cognitive_capacity', 0.8)
        
        for date, daily_entries in daily_schedules.items():
            # Calculate total cognitive load for the day
            total_load = sum(entry['cognitive_load'] for entry in daily_entries)
            
            if total_load > user_capacity:
                # Redistribute or reschedule some items
                optimized_daily = self._redistribute_daily_cognitive_load(
                    daily_entries, user_capacity
                )
            else:
                optimized_daily = daily_entries
            
            optimized_entries.extend(optimized_daily)
        
        return sorted(optimized_entries, key=lambda x: x['scheduled_date'])
    
    def _redistribute_daily_cognitive_load(
        self,
        daily_entries: List[Dict[str, Any]],
        capacity: float
    ) -> List[Dict[str, Any]]:
        """Redistribute cognitive load for a single day"""
        # Sort by priority (high priority items stay on original day)
        daily_entries.sort(key=lambda x: x['priority_score'], reverse=True)
        
        redistributed = []
        current_load = 0
        
        for entry in daily_entries:
            if current_load + entry['cognitive_load'] <= capacity:
                # Keep on original day
                redistributed.append(entry)
                current_load += entry['cognitive_load']
            else:
                # Move to next available day
                entry['scheduled_date'] += timedelta(days=1)
                entry['rescheduled'] = True
                redistributed.append(entry)
        
        return redistributed
    
    def _calculate_schedule_metadata(self, schedule_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metadata for the generated schedule"""
        if not schedule_entries:
            return {'total_sessions': 0}
        
        total_sessions = len(schedule_entries)
        total_duration = sum(entry['estimated_duration'] for entry in schedule_entries)
        avg_cognitive_load = sum(entry['cognitive_load'] for entry in schedule_entries) / total_sessions
        
        # Calculate schedule span
        start_date = min(entry['scheduled_date'] for entry in schedule_entries)
        end_date = max(entry['scheduled_date'] for entry in schedule_entries)
        schedule_span = (end_date - start_date).days
        
        # Calculate session types distribution
        session_types = {}
        for entry in schedule_entries:
            session_type = entry['session_type']
            session_types[session_type] = session_types.get(session_type, 0) + 1
        
        return {
            'total_sessions': total_sessions,
            'total_estimated_duration': total_duration,
            'average_cognitive_load': round(avg_cognitive_load, 3),
            'schedule_span_days': schedule_span,
            'session_types_distribution': session_types,
            'average_repetition_interval': round(
                sum(entry['repetition_interval'] for entry in schedule_entries) / total_sessions, 1
            ),
            'cognitive_load_optimized': any(entry.get('rescheduled', False) for entry in schedule_entries)
        }
    
    # Additional helper methods would continue here...
    # This represents the core HLR implementation structure