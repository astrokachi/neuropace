"""
Enhanced Learning Analytics Service
Implements comprehensive learning analytics with predictive modeling
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import math
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from collections import defaultdict
from models import User, Performance, StudySession, Quiz, Material, Schedule

class LearningAnalytics:
    """
    Advanced learning analytics service with ML-powered insights
    Provides comprehensive analysis of learning patterns and performance prediction
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Analytics model parameters
        self.analytics_params = {
            'learning_velocity_weights': [0.4, 0.3, 0.2, 0.1],  # Weighted recent performance
            'retention_prediction_threshold': 0.7,
            'cognitive_load_optimal_range': (0.4, 0.7),
            'performance_trend_window': 14,  # Days
            'confidence_threshold': 0.8
        }
    
    def initialize_material_baseline(
        self,
        user_id: int,
        content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Initialize learning analytics baseline for new material
        
        Args:
            user_id: ID of the user
            content_analysis: Content analysis from document processor
            
        Returns:
            Baseline metrics for learning analytics
        """
        try:
            # Get user's historical learning profile
            user_profile = self._get_comprehensive_user_profile(user_id)
            
            # Predict initial learning metrics based on content and user profile
            predicted_metrics = self._predict_initial_learning_metrics(
                content_analysis, user_profile
            )
            
            # Calculate expected learning trajectory
            learning_trajectory = self._calculate_expected_trajectory(
                content_analysis, user_profile, predicted_metrics
            )
            
            # Set up performance monitoring baselines
            monitoring_baselines = self._setup_monitoring_baselines(
                user_profile, content_analysis
            )
            
            return {
                'success': True,
                'baseline_metrics': {
                    'predicted_completion_time': predicted_metrics['completion_time'],
                    'expected_retention_rate': predicted_metrics['retention_rate'],
                    'estimated_sessions_needed': predicted_metrics['sessions_needed'],
                    'predicted_difficulty_adaptation': predicted_metrics['difficulty_adaptation']
                },
                'learning_trajectory': learning_trajectory,
                'monitoring_baselines': monitoring_baselines,
                'initialization_metadata': {
                    'initialized_at': datetime.utcnow().isoformat(),
                    'content_difficulty': content_analysis.get('estimated_difficulty', 0.5),
                    'user_experience_level': user_profile['experience_level']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Baseline initialization failed: {str(e)}'
            }
    
    def analyze_learning_patterns(
        self,
        user_id: int,
        material_id: int,
        analysis_window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of user learning patterns
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            analysis_window_days: Analysis window in days
            
        Returns:
            Detailed learning pattern analysis
        """
        try:
            # Get comprehensive learning data
            learning_data = self._get_comprehensive_learning_data(
                user_id, material_id, analysis_window_days
            )
            
            # Analyze performance patterns
            performance_patterns = self._analyze_performance_patterns(learning_data['performances'])
            
            # Analyze study behavior patterns
            behavior_patterns = self._analyze_study_behavior_patterns(learning_data['study_sessions'])
            
            # Analyze temporal patterns
            temporal_patterns = self._analyze_temporal_learning_patterns(learning_data)
            
            # Calculate learning efficiency metrics
            efficiency_metrics = self._calculate_learning_efficiency(learning_data)
            
            # Identify learning strengths and weaknesses
            strengths_weaknesses = self._identify_strengths_weaknesses(
                performance_patterns, behavior_patterns
            )
            
            # Predict difficulty progression
            difficulty_progression = self._predict_difficulty_progression(
                performance_patterns, material_id
            )
            
            # Calculate overall learning health score
            learning_health_score = self._calculate_learning_health_score(
                performance_patterns, behavior_patterns, efficiency_metrics
            )
            
            return {
                'success': True,
                'performance_patterns': performance_patterns,
                'behavior_patterns': behavior_patterns,
                'temporal_patterns': temporal_patterns,
                'efficiency_metrics': efficiency_metrics,
                'strengths_weaknesses': strengths_weaknesses,
                'difficulty_progression': difficulty_progression,
                'learning_health_score': learning_health_score,
                'analysis_metadata': {
                    'analysis_date': datetime.utcnow().isoformat(),
                    'data_points_analyzed': len(learning_data['performances']) + len(learning_data['study_sessions']),
                    'analysis_confidence': self._calculate_analysis_confidence(learning_data)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Learning pattern analysis failed: {str(e)}'
            }
    
    def calculate_cognitive_load_optimization(
        self,
        user_id: int,
        current_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate cognitive load optimization recommendations
        
        Args:
            user_id: ID of the user
            current_performance: Current performance analysis
            
        Returns:
            Cognitive load optimization recommendations
        """
        try:
            # Get user's cognitive profile
            cognitive_profile = self._get_cognitive_profile(user_id)
            
            # Analyze current cognitive load
            current_load_analysis = self._analyze_current_cognitive_load(
                current_performance, cognitive_profile
            )
            
            # Calculate optimal cognitive load distribution
            optimal_distribution = self._calculate_optimal_cognitive_distribution(
                cognitive_profile, current_load_analysis
            )
            
            # Generate load balancing recommendations
            load_recommendations = self._generate_cognitive_load_recommendations(
                current_load_analysis, optimal_distribution
            )
            
            # Calculate session timing optimizations
            timing_optimizations = self._optimize_session_timing(
                cognitive_profile, current_load_analysis
            )
            
            return {
                'success': True,
                'current_load_analysis': current_load_analysis,
                'optimal_distribution': optimal_distribution,
                'recommendations': load_recommendations,
                'timing_optimizations': timing_optimizations,
                'optimization_metadata': {
                    'optimization_date': datetime.utcnow().isoformat(),
                    'cognitive_capacity': cognitive_profile['capacity'],
                    'optimization_confidence': current_load_analysis['confidence']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Cognitive load optimization failed: {str(e)}'
            }
    
    def predict_learning_velocity(
        self,
        user_id: int,
        current_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict learning velocity and completion timeline
        
        Args:
            user_id: ID of the user
            current_performance: Current performance data
            
        Returns:
            Learning velocity predictions
        """
        try:
            # Get historical velocity data
            velocity_history = self._get_learning_velocity_history(user_id)
            
            # Calculate current velocity trend
            current_velocity = self._calculate_current_velocity(
                velocity_history, current_performance
            )
            
            # Predict future velocity based on patterns
            velocity_prediction = self._predict_future_velocity(
                velocity_history, current_velocity, current_performance
            )
            
            # Calculate completion timeline predictions
            completion_predictions = self._predict_completion_timeline(
                velocity_prediction, current_performance
            )
            
            # Identify velocity optimization opportunities
            optimization_opportunities = self._identify_velocity_optimizations(
                velocity_history, current_velocity
            )
            
            return {
                'success': True,
                'current_velocity': current_velocity,
                'velocity_prediction': velocity_prediction,
                'completion_predictions': completion_predictions,
                'optimization_opportunities': optimization_opportunities,
                'velocity_metadata': {
                    'prediction_date': datetime.utcnow().isoformat(),
                    'historical_data_points': len(velocity_history),
                    'prediction_confidence': velocity_prediction['confidence']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Learning velocity prediction failed: {str(e)}'
            }
    
    def get_comprehensive_learning_history(
        self,
        user_id: int,
        material_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive learning history for a user and material
        
        Args:
            user_id: ID of the user
            material_id: ID of the material
            
        Returns:
            Comprehensive learning history
        """
        try:
            # Get all performance data
            performances = self._get_detailed_performance_history(user_id, material_id)
            
            # Get all study sessions
            study_sessions = self._get_detailed_study_sessions(user_id, material_id)
            
            # Calculate learning milestones
            milestones = self._identify_learning_milestones(performances, study_sessions)
            
            # Analyze learning progression
            progression_analysis = self._analyze_learning_progression(
                performances, study_sessions, milestones
            )
            
            # Calculate comprehensive metrics
            comprehensive_metrics = self._calculate_comprehensive_metrics(
                performances, study_sessions
            )
            
            return {
                'success': True,
                'performances': performances,
                'study_sessions': study_sessions,
                'milestones': milestones,
                'progression_analysis': progression_analysis,
                'comprehensive_metrics': comprehensive_metrics,
                'history_metadata': {
                    'data_span_days': self._calculate_data_span(performances, study_sessions),
                    'total_learning_time': comprehensive_metrics['total_study_time'],
                    'data_quality_score': self._assess_data_quality(performances, study_sessions)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Learning history retrieval failed: {str(e)}'
            }
    
    def get_user_learning_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive user learning profile
        
        Args:
            user_id: ID of the user
            
        Returns:
            Comprehensive user learning profile
        """
        try:
            # Get basic user data
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return self._get_default_learning_profile()
            
            # Calculate learning characteristics
            learning_characteristics = self._calculate_learning_characteristics(user_id)
            
            # Analyze preferred learning patterns
            learning_preferences = self._analyze_learning_preferences(user_id)
            
            # Calculate performance consistency
            performance_consistency = self._calculate_performance_consistency(user_id)
            
            # Determine optimal difficulty level
            optimal_difficulty = self._determine_optimal_difficulty(user_id)
            
            return {
                'user_id': user_id,
                'reading_speed': getattr(user, 'average_reading_speed', 200),
                'current_level': learning_characteristics['current_level'],
                'learning_characteristics': learning_characteristics,
                'learning_preferences': learning_preferences,
                'performance_consistency': performance_consistency,
                'optimal_difficulty': optimal_difficulty,
                'cognitive_profile': {
                    'capacity': getattr(user, 'cognitive_load_limit', 0.8),
                    'attention_span': learning_characteristics['attention_span'],
                    'processing_speed': learning_characteristics['processing_speed']
                },
                'difficulty_tolerance': optimal_difficulty
            }
            
        except Exception as e:
            return self._get_default_learning_profile()
    
    def optimize_session_cognitive_load(
        self,
        user_id: int,
        content_sections: List[Dict[str, Any]],
        available_time: int,
        current_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize cognitive load for a specific study session
        
        Args:
            user_id: ID of the user
            content_sections: Content sections for the session
            available_time: Available time in minutes
            current_state: Current cognitive state
            
        Returns:
            Cognitive load optimization plan
        """
        try:
            # Get user's cognitive profile
            cognitive_profile = self._get_cognitive_profile(user_id)
            
            # Calculate load for each content section
            section_loads = self._calculate_section_cognitive_loads(
                content_sections, cognitive_profile
            )
            
            # Optimize section sequencing
            optimized_sequence = self._optimize_section_sequence(
                section_loads, available_time, cognitive_profile
            )
            
            # Calculate optimal break intervals
            break_intervals = self._calculate_optimal_breaks(
                optimized_sequence, cognitive_profile, available_time
            )
            
            # Generate load management strategies
            load_strategies = self._generate_load_management_strategies(
                optimized_sequence, cognitive_profile, current_state
            )
            
            return {
                'success': True,
                'section_loads': section_loads,
                'optimized_sequence': optimized_sequence,
                'break_intervals': break_intervals,
                'load_strategies': load_strategies,
                'total_estimated_load': sum(s['cognitive_load'] for s in optimized_sequence),
                'optimization_metadata': {
                    'optimization_method': 'cognitive_load_balancing',
                    'user_capacity': cognitive_profile['capacity'],
                    'session_duration': available_time
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Session cognitive load optimization failed: {str(e)}'
            }
    
    # Helper methods for learning analytics
    
    def _get_comprehensive_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user profile for analytics"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # Get performance statistics
        avg_performance = self.db.query(func.avg(Performance.score)).filter(
            Performance.user_id == user_id
        ).scalar() or 0.7
        
        # Get study session statistics
        total_sessions = self.db.query(StudySession).filter(
            StudySession.user_id == user_id
        ).count()
        
        # Calculate experience level
        experience_level = min(1.0, total_sessions / 50.0)  # 50 sessions = experienced
        
        return {
            'user_id': user_id,
            'average_performance': avg_performance,
            'total_sessions': total_sessions,
            'experience_level': experience_level,
            'reading_speed': getattr(user, 'average_reading_speed', 200) if user else 200,
            'retention_rate': getattr(user, 'retention_rate', 0.7) if user else 0.7,
            'cognitive_capacity': getattr(user, 'cognitive_load_limit', 0.8) if user else 0.8
        }
    
    def _predict_initial_learning_metrics(
        self,
        content_analysis: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict initial learning metrics for new material"""
        difficulty = content_analysis.get('estimated_difficulty', 0.5)
        word_count = content_analysis.get('word_count', 1000)
        
        # Predict completion time
        base_time = word_count / user_profile['reading_speed']
        difficulty_multiplier = 1 + (difficulty * 0.5)
        experience_adjustment = 1 - (user_profile['experience_level'] * 0.2)
        completion_time = base_time * difficulty_multiplier * experience_adjustment
        
        # Predict retention rate
        base_retention = user_profile['retention_rate']
        difficulty_penalty = difficulty * 0.15
        retention_rate = max(0.5, base_retention - difficulty_penalty)
        
        # Predict sessions needed
        base_sessions = max(3, int(completion_time / 60))  # 1 hour per session
        sessions_needed = int(base_sessions * (1 + difficulty * 0.3))
        
        # Predict difficulty adaptation
        adaptation_rate = user_profile['experience_level'] * 0.3 + 0.7
        
        return {
            'completion_time': round(completion_time, 1),
            'retention_rate': round(retention_rate, 3),
            'sessions_needed': sessions_needed,
            'difficulty_adaptation': round(adaptation_rate, 3)
        }
    
    def _calculate_expected_trajectory(
        self,
        content_analysis: Dict[str, Any],
        user_profile: Dict[str, Any],
        predicted_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate expected learning trajectory"""
        trajectory = []
        sessions = predicted_metrics['sessions_needed']
        
        for session in range(1, sessions + 1):
            # Predict performance for each session
            progress_factor = session / sessions
            initial_performance = 0.3 + (user_profile['experience_level'] * 0.2)
            
            # Learning curve (exponential improvement with plateau)
            performance = initial_performance + (0.6 * (1 - math.exp(-progress_factor * 3)))
            
            # Adjust for difficulty
            difficulty = content_analysis.get('estimated_difficulty', 0.5)
            adjusted_performance = performance * (1 - difficulty * 0.2)
            
            trajectory.append({
                'session_number': session,
                'expected_performance': round(min(0.9, adjusted_performance), 3),
                'expected_retention': round(predicted_metrics['retention_rate'] * 
                                          (0.8 + progress_factor * 0.2), 3),
                'confidence': round(0.9 - (session * 0.02), 2)  # Decreasing confidence for future
            })
        
        return trajectory
    
    def _setup_monitoring_baselines(
        self,
        user_profile: Dict[str, Any],
        content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Setup monitoring baselines for performance tracking"""
        return {
            'performance_threshold': max(0.6, user_profile['average_performance'] - 0.1),
            'retention_threshold': max(0.5, user_profile['retention_rate'] - 0.1),
            'cognitive_load_threshold': user_profile['cognitive_capacity'] * 0.8,
            'session_duration_optimal': 45,  # minutes
            'break_frequency_optimal': 25,  # minutes between breaks
            'alert_triggers': {
                'performance_decline': 0.15,  # 15% decline triggers alert
                'retention_decline': 0.1,    # 10% decline triggers alert
                'cognitive_overload': 0.9    # 90% of capacity triggers alert
            }
        }
    
    def _get_comprehensive_learning_data(
        self,
        user_id: int,
        material_id: int,
        days: int
    ) -> Dict[str, Any]:
        """Get comprehensive learning data for analysis"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get performance data
        performances = self.db.query(Performance).join(Quiz).filter(
            Performance.user_id == user_id,
            Quiz.material_id == material_id,
            Performance.created_at >= cutoff_date
        ).order_by(Performance.created_at).all()
        
        # Get study sessions
        study_sessions = self.db.query(StudySession).join(Schedule).filter(
            StudySession.user_id == user_id,
            Schedule.material_id == material_id,
            StudySession.start_time >= cutoff_date
        ).order_by(StudySession.start_time).all()
        
        return {
            'performances': performances,
            'study_sessions': study_sessions,
            'analysis_period': days
        }
    
    def _analyze_performance_patterns(self, performances: List[Performance]) -> Dict[str, Any]:
        """Analyze performance patterns from quiz data"""
        if not performances:
            return self._get_default_performance_patterns()
        
        scores = [p.score for p in performances]
        times = [p.time_taken for p in performances if p.time_taken]
        
        # Calculate basic statistics
        avg_score = sum(scores) / len(scores)
        score_trend = self._calculate_trend(scores)
        consistency = 1 - (np.std(scores) if len(scores) > 1 else 0)
        
        # Analyze improvement rate
        if len(scores) >= 4:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            improvement_rate = (sum(second_half)/len(second_half)) - (sum(first_half)/len(first_half))
        else:
            improvement_rate = 0
        
        # Analyze time efficiency
        time_efficiency = self._analyze_time_efficiency(times, scores)
        
        return {
            'average_score': round(avg_score, 3),
            'score_trend': score_trend,
            'consistency_score': round(consistency, 3),
            'improvement_rate': round(improvement_rate, 3),
            'time_efficiency': time_efficiency,
            'total_assessments': len(performances),
            'performance_volatility': round(np.std(scores) if len(scores) > 1 else 0, 3)
        }
    
    def _analyze_study_behavior_patterns(self, study_sessions: List[StudySession]) -> Dict[str, Any]:
        """Analyze study behavior patterns"""
        if not study_sessions:
            return self._get_default_behavior_patterns()
        
        # Calculate session statistics
        durations = [s.duration_minutes for s in study_sessions if s.duration_minutes]
        focus_scores = [s.focus_score for s in study_sessions if s.focus_score is not None]
        
        # Analyze study timing patterns
        study_times = [s.start_time.hour for s in study_sessions]
        preferred_time = max(set(study_times), key=study_times.count) if study_times else 9
        
        # Calculate engagement metrics
        avg_duration = sum(durations) / len(durations) if durations else 0
        avg_focus = sum(focus_scores) / len(focus_scores) if focus_scores else 0.5
        
        # Analyze consistency
        session_consistency = self._analyze_session_consistency(study_sessions)
        
        return {
            'average_session_duration': round(avg_duration, 1),
            'average_focus_score': round(avg_focus, 3),
            'preferred_study_time': preferred_time,
            'session_consistency': session_consistency,
            'total_study_time': sum(durations),
            'total_sessions': len(study_sessions),
            'engagement_level': self._calculate_engagement_level(focus_scores, durations)
        }
    
    def _analyze_temporal_learning_patterns(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal patterns in learning"""
        performances = learning_data['performances']
        study_sessions = learning_data['study_sessions']
        
        # Analyze learning by day of week
        weekday_performance = defaultdict(list)
        for p in performances:
            weekday = p.created_at.weekday()
            weekday_performance[weekday].append(p.score)
        
        # Analyze learning by time of day
        hour_performance = defaultdict(list)
        for p in performances:
            hour = p.created_at.hour
            hour_performance[hour].append(p.score)
        
        # Find optimal learning times
        best_weekday = max(weekday_performance.items(), 
                          key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)[0] if weekday_performance else 1
        best_hour = max(hour_performance.items(),
                       key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)[0] if hour_performance else 9
        
        return {
            'best_weekday': best_weekday,
            'best_hour': best_hour,
            'weekday_patterns': dict(weekday_performance),
            'hourly_patterns': dict(hour_performance),
            'learning_rhythm': self._identify_learning_rhythm(performances, study_sessions)
        }
    
    def _calculate_learning_efficiency(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate learning efficiency metrics"""
        performances = learning_data['performances']
        study_sessions = learning_data['study_sessions']
        
        if not performances or not study_sessions:
            return {'efficiency_score': 0.5, 'time_to_competency': 0}
        
        # Calculate score per unit time
        total_study_time = sum(s.duration_minutes for s in study_sessions if s.duration_minutes)
        avg_score = sum(p.score for p in performances) / len(performances)
        
        if total_study_time > 0:
            efficiency_score = avg_score / (total_study_time / 60)  # Score per hour
        else:
            efficiency_score = 0
        
        # Calculate time to competency (score > 0.7)
        competent_performances = [p for p in performances if p.score >= 0.7]
        time_to_competency = 0
        if competent_performances:
            first_competent = min(competent_performances, key=lambda x: x.created_at)
            first_session = min(study_sessions, key=lambda x: x.start_time)
            time_to_competency = (first_competent.created_at - first_session.start_time).days
        
        return {
            'efficiency_score': round(min(efficiency_score, 2.0), 3),  # Cap at 2.0
            'time_to_competency': time_to_competency,
            'total_study_time_hours': round(total_study_time / 60, 1),
            'average_performance': round(avg_score, 3),
            'learning_rate': self._calculate_learning_rate(performances)
        }
    
    def _identify_strengths_weaknesses(
        self,
        performance_patterns: Dict[str, Any],
        behavior_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify learning strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Analyze performance strengths/weaknesses
        if performance_patterns['average_score'] >= 0.8:
            strengths.append('High performance consistency')
        elif performance_patterns['average_score'] < 0.6:
            weaknesses.append('Below average performance')
        
        if performance_patterns['improvement_rate'] > 0.1:
            strengths.append('Strong learning progression')
        elif performance_patterns['improvement_rate'] < -0.05:
            weaknesses.append('Declining performance trend')
        
        if performance_patterns['consistency_score'] > 0.8:
            strengths.append('Consistent performance')
        elif performance_patterns['consistency_score'] < 0.6:
            weaknesses.append('Inconsistent performance')
        
        # Analyze behavior strengths/weaknesses
        if behavior_patterns['average_focus_score'] > 0.7:
            strengths.append('High focus and attention')
        elif behavior_patterns['average_focus_score'] < 0.5:
            weaknesses.append('Attention and focus challenges')
        
        if behavior_patterns['session_consistency']['consistency_score'] > 0.7:
            strengths.append('Regular study habits')
        elif behavior_patterns['session_consistency']['consistency_score'] < 0.5:
            weaknesses.append('Irregular study schedule')
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'improvement_priorities': self._prioritize_improvements(weaknesses),
            'strength_leverage_opportunities': self._identify_leverage_opportunities(strengths)
        }
    
    def _predict_difficulty_progression(
        self,
        performance_patterns: Dict[str, Any],
        material_id: int
    ) -> Dict[str, Any]:
        """Predict optimal difficulty progression"""
        current_performance = performance_patterns['average_score']
        improvement_rate = performance_patterns['improvement_rate']
        consistency = performance_patterns['consistency_score']
        
        # Calculate optimal difficulty
        if current_performance >= 0.8 and consistency > 0.7:
            recommended_difficulty = 'increase'
            target_difficulty = min(1.0, 0.7 + current_performance * 0.3)
        elif current_performance < 0.6 or consistency < 0.5:
            recommended_difficulty = 'decrease'
            target_difficulty = max(0.3, current_performance * 0.8)
        else:
            recommended_difficulty = 'maintain'
            target_difficulty = 0.5 + current_performance * 0.2
        
        return {
            'current_optimal_difficulty': round(target_difficulty, 2),
            'recommendation': recommended_difficulty,
            'progression_rate': 'gradual' if consistency > 0.7 else 'careful',
            'confidence': round(consistency * 0.8 + (1 - abs(improvement_rate)) * 0.2, 2)
        }
    
    def _calculate_learning_health_score(
        self,
        performance_patterns: Dict[str, Any],
        behavior_patterns: Dict[str, Any],
        efficiency_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall learning health score"""
        # Weight different components
        performance_weight = 0.4
        behavior_weight = 0.3
        efficiency_weight = 0.3
        
        # Normalize scores to 0-1 range
        performance_score = performance_patterns['average_score']
        behavior_score = (behavior_patterns['average_focus_score'] + 
                         behavior_patterns['session_consistency']['consistency_score']) / 2
        efficiency_score = min(1.0, efficiency_metrics['efficiency_score'] / 2.0)
        
        # Calculate weighted health score
        health_score = (performance_score * performance_weight + 
                       behavior_score * behavior_weight + 
                       efficiency_score * efficiency_weight)
        
        # Determine health category
        if health_score >= 0.8:
            health_category = 'excellent'
        elif health_score >= 0.7:
            health_category = 'good'
        elif health_score >= 0.6:
            health_category = 'fair'
        else:
            health_category = 'needs_improvement'
        
        return {
            'overall_score': round(health_score, 3),
            'category': health_category,
            'component_scores': {
                'performance': round(performance_score, 3),
                'behavior': round(behavior_score, 3),
                'efficiency': round(efficiency_score, 3)
            },
            'improvement_potential': round((1 - health_score) * 100, 1)  # Percentage improvement possible
        }
    
    # Additional helper methods would continue here...
    # This represents the core structure of the LearningAnalytics service
    
    def _get_default_learning_profile(self) -> Dict[str, Any]:
        """Return default learning profile for new users"""
        return {
            'reading_speed': 200,
            'current_level': 0.5,
            'difficulty_tolerance': 0.5,
            'cognitive_profile': {
                'capacity': 0.8,
                'attention_span': 45,
                'processing_speed': 0.7
            }
        }
    
    def _calculate_analysis_confidence(self, learning_data: Dict[str, Any]) -> float:
        """Calculate confidence in analysis based on data quality"""
        performances = learning_data['performances']
        study_sessions = learning_data['study_sessions']
        
        data_points = len(performances) + len(study_sessions)
        if data_points >= 10:
            return 0.9
        elif data_points >= 5:
            return 0.7
        elif data_points >= 2:
            return 0.5
        else:
            return 0.3
    
    def _get_default_performance_patterns(self) -> Dict[str, Any]:
        """Return default performance patterns"""
        return {
            'average_score': 0.5,
            'score_trend': 'stable',
            'consistency_score': 0.5,
            'improvement_rate': 0.0,
            'time_efficiency': {'efficiency_score': 0.5},
            'total_assessments': 0,
            'performance_volatility': 0.0
        }
    
    def _get_default_behavior_patterns(self) -> Dict[str, Any]:
        """Return default behavior patterns"""
        return {
            'average_session_duration': 30,
            'average_focus_score': 0.5,
            'preferred_study_time': 9,
            'session_consistency': {'consistency_score': 0.5},
            'total_study_time': 0,
            'total_sessions': 0,
            'engagement_level': 0.5
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 3:
            return 'stable'
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.05:
            return 'improving'
        elif slope < -0.05:
            return 'declining'
        else:
            return 'stable'