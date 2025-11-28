#!/usr/bin/env python3
"""
LEX-VITALITY NODE - Biological State Management
Specialized Lex Node for processing bio-data and optimizing health metrics
Part of the LEX-7 Sovereign Lattice
"""

import torch
import numpy as np
import asyncio
import time
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

from ..core.lex_node import LexNode
from ..communication.bark_protocol import BARKDirective, BARKResponse

logger = logging.getLogger(__name__)

@dataclass
class VitalityMetrics:
    """Represents biological vitality metrics"""
    heart_rate: Optional[float] = None
    sleep_hours: Optional[float] = None
    exercise_minutes: Optional[float] = None
    stress_level: Optional[float] = None
    nutrition_score: Optional[float] = None
    energy_level: Optional[float] = None
    recovery_score: Optional[float] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VitalityMetrics':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class HealthOptimization:
    """Health optimization recommendations"""
    recommended_actions: List[str]
    priority_score: float
    energy_impact: Dict[str, float]
    timeline: str
    compliance_requirements: List[str]

class LexVitalityNode(LexNode):
    """
    Lex Vitality Node
    
    Specialized for biological data processing and health optimization.
    Processes bio-metrics through the Error-State Model to provide
    personalized health recommendations.
    """
    
    def __init__(self, config_path: Path, node_id: str = "lex_vit_001"):
        super().__init__(config_path, node_id)
        
        # Vitality-specific state
        self.current_vitality = VitalityMetrics()
        self.vitality_history: List[VitalityMetrics] = []
        self.health_goals = {}
        self.optimization_cache = {}
        
        # Bio-data processing capabilities
        self.bio_sensors = []
        self.health_thresholds = self._initialize_health_thresholds()
        self.vitality_model = None
        
        # Register vitality-specific directive handlers
        self._register_vitality_handlers()
        
        logger.info(f"Lex Vitality Node {node_id} initialized")
    
    def _initialize_health_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize health threshold values"""
        return {
            'heart_rate': {
                'resting_min': 60.0,
                'resting_max': 100.0,
                'exercise_max': 180.0
            },
            'sleep': {
                'minimum_hours': 7.0,
                'optimal_hours': 8.0,
                'maximum_hours': 9.0
            },
            'exercise': {
                'minimum_minutes': 30.0,
                'target_minutes': 150.0,
                'maximum_minutes': 300.0
            },
            'stress': {
                'low_max': 3.0,
                'moderate_max': 6.0,
                'high_max': 10.0
            },
            'nutrition': {
                'poor_max': 4.0,
                'fair_max': 6.0,
                'good_max': 8.0,
                'excellent_max': 10.0
            },
            'energy': {
                'low_max': 4.0,
                'moderate_max': 7.0,
                'high_min': 7.0
            }
        }
    
    def _register_vitality_handlers(self):
        """Register vitality-specific directive handlers"""
        
        # Health data ingestion
        self.register_directive_handler("ingest_bio_data", self._handle_ingest_bio_data)
        self.register_directive_handler("update_vitality_metrics", self._handle_update_vitality_metrics)
        
        # Health optimization
        self.register_directive_handler("analyze_health_patterns", self._handle_analyze_health_patterns)
        self.register_directive_handler("generate_health_recommendations", self._handle_generate_health_recommendations)
        self.register_directive_handler("optimize_sleep_schedule", self._handle_optimize_sleep_schedule)
        self.register_directive_handler("plan_exercise_routine", self._handle_plan_exercise_routine)
        
        # Health validation
        self.register_directive_handler("validate_health_action", self._handle_validate_health_action)
        self.register_directive_handler("assess_recovery_status", self._handle_assess_recovery_status)
        
        # Cross-node communication
        self.register_directive_handler("coordinate_wealth_health", self._handle_coordinate_wealth_health)
    
    async def _handle_ingest_bio_data(self, directive: BARKDirective, message):
        """Handle biological data ingestion"""
        try:
            bio_data = directive.parameters.get('bio_data', {})
            sensor_type = directive.parameters.get('sensor_type', 'manual')
            
            # Process bio-data through Lex-Mamba kernel
            processed_data = await self._process_bio_data(bio_data, sensor_type)
            
            # Update vitality metrics
            self.current_vitality = VitalityMetrics(**processed_data)
            self.vitality_history.append(self.current_vitality)
            
            # Limit history size
            if len(self.vitality_history) > 1000:
                self.vitality_history.pop(0)
            
            # Generate immediate recommendations if needed
            recommendations = await self._generate_immediate_recommendations()
            
            response = BARKResponse(
                response_id=f"bio_ingest_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result={
                    'processed_metrics': self.current_vitality.to_dict(),
                    'recommendations': recommendations,
                    'data_quality': self._assess_data_quality(processed_data)
                }
            )
            
        except Exception as e:
            response = BARKResponse(
                response_id=f"bio_ingest_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="error",
                result={'error': str(e)}
            )
        
        return response
    
    async def _process_bio_data(self, bio_data: Dict[str, Any], sensor_type: str) -> Dict[str, float]:
        """Process raw bio-data through the Error-State Model"""
        
        # Convert bio-data to state-space input
        bio_tensor = self._bio_data_to_tensor(bio_data)
        
        # Process through Lex-Mamba kernel
        h_t, y_pred, error_signal = self.kernel.kernel.forward(bio_tensor, self.current_state)
        
        # Update current state
        self.current_state = h_t
        
        # Extract processed metrics
        processed_metrics = self._tensor_to_vitality_metrics(y_pred, bio_data)
        
        return processed_metrics
    
    def _bio_data_to_tensor(self, bio_data: Dict[str, Any]) -> torch.Tensor:
        """Convert bio-data to state-space input tensor"""
        state_dim = self.config['model']['state_dim']
        input_tensor = torch.zeros(state_dim)
        
        # Encode bio-data channels
        channels = {
            'heart_rate': bio_data.get('heart_rate', 75) / 200.0,  # Normalize
            'sleep_hours': bio_data.get('sleep_hours', 8) / 12.0,
            'exercise_minutes': bio_data.get('exercise_minutes', 30) / 300.0,
            'stress_level': bio_data.get('stress_level', 5) / 10.0,
            'nutrition_score': bio_data.get('nutrition_score', 6) / 10.0
        }
        
        # Distribute across tensor dimensions
        for i, (metric, value) in enumerate(channels.items()):
            if i < state_dim:
                input_tensor[i] = value
        
        return input_tensor.unsqueeze(0)
    
    def _tensor_to_vitality_metrics(self, tensor: torch.Tensor, raw_bio_data: Dict[str, Any]) -> Dict[str, float]:
        """Convert model output to vitality metrics"""
        tensor_np = tensor.squeeze(0).detach().numpy()
        
        # Extract and denormalize metrics
        metrics = {
            'heart_rate': raw_bio_data.get('heart_rate', 75) * (1 + tensor_np[0] * 0.1),
            'sleep_hours': raw_bio_data.get('sleep_hours', 8) * (1 + tensor_np[1] * 0.1),
            'exercise_minutes': raw_bio_data.get('exercise_minutes', 30) * (1 + tensor_np[2] * 0.1),
            'stress_level': max(1, min(10, raw_bio_data.get('stress_level', 5) * (1 + tensor_np[3] * 0.1))),
            'nutrition_score': max(1, min(10, raw_bio_data.get('nutrition_score', 6) * (1 + tensor_np[4] * 0.1))),
            'energy_level': self._calculate_energy_level(raw_bio_data),
            'recovery_score': self._calculate_recovery_score(raw_bio_data)
        }
        
        return metrics
    
    def _calculate_energy_level(self, bio_data: Dict[str, Any]) -> float:
        """Calculate energy level from bio-data"""
        # Simplified energy calculation
        sleep_score = min(1.0, bio_data.get('sleep_hours', 8) / 8.0)
        exercise_score = min(1.0, bio_data.get('exercise_minutes', 30) / 30.0)
        stress_penalty = max(0, (bio_data.get('stress_level', 5) - 5) / 5.0)
        
        energy = (sleep_score + exercise_score - stress_penalty) * 10.0 / 2.0
        return max(1.0, min(10.0, energy))
    
    def _calculate_recovery_score(self, bio_data: Dict[str, Any]) -> float:
        """Calculate recovery score"""
        sleep_hours = bio_data.get('sleep_hours', 8)
        stress_level = bio_data.get('stress_level', 5)
        
        # Recovery based on sleep and stress
        recovery = (sleep_hours / 8.0) * (1 - stress_level / 10.0) * 10.0
        return max(1.0, min(10.0, recovery))
    
    async def _generate_immediate_recommendations(self) -> List[str]:
        """Generate immediate health recommendations"""
        recommendations = []
        
        metrics = self.current_vitality.to_dict()
        
        # Check heart rate
        hr = metrics.get('heart_rate', 75)
        if hr > self.health_thresholds['heart_rate']['resting_max']:
            recommendations.append("Consider rest and stress reduction techniques")
        elif hr < self.health_thresholds['heart_rate']['resting_min']:
            recommendations.append("Check for adequate sleep and hydration")
        
        # Check sleep
        sleep = metrics.get('sleep_hours', 8)
        if sleep < self.health_thresholds['sleep']['minimum_hours']:
            recommendations.append("Prioritize additional sleep hours tonight")
        
        # Check exercise
        exercise = metrics.get('exercise_minutes', 30)
        if exercise < self.health_thresholds['exercise']['minimum_minutes']:
            recommendations.append("Schedule exercise session today")
        
        # Check stress
        stress = metrics.get('stress_level', 5)
        if stress > self.health_thresholds['stress']['moderate_max']:
            recommendations.append("Engage in stress reduction activities")
        
        # Check nutrition
        nutrition = metrics.get('nutrition_score', 6)
        if nutrition < self.health_thresholds['nutrition']['fair_max']:
            recommendations.append("Focus on nutrient-dense foods")
        
        return recommendations
    
    async def _handle_analyze_health_patterns(self, directive: BARKDirective, message):
        """Analyze health patterns over time"""
        try:
            time_period = directive.parameters.get('time_period', '7_days')
            pattern_type = directive.parameters.get('pattern_type', 'comprehensive')
            
            # Analyze patterns in vitality history
            patterns = await self._analyze_vitality_patterns(time_period, pattern_type)
            
            # Generate insights
            insights = self._generate_health_insights(patterns)
            
            response = BARKResponse(
                response_id=f"pattern_analysis_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result={
                    'patterns': patterns,
                    'insights': insights,
                    'recommendations': await self._generate_pattern_recommendations(patterns)
                }
            )
            
        except Exception as e:
            response = BARKResponse(
                response_id=f"pattern_analysis_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="error",
                result={'error': str(e)}
            )
        
        return response
    
    async def _analyze_vitality_patterns(self, time_period: str, pattern_type: str) -> Dict[str, Any]:
        """Analyze patterns in vitality data"""
        if not self.vitality_history:
            return {'error': 'No vitality history available'}
        
        # Filter by time period
        current_time = time.time()
        period_seconds = {
            '24_hours': 86400,
            '7_days': 604800,
            '30_days': 2592000,
            '90_days': 7776000
        }.get(time_period, 604800)
        
        cutoff_time = current_time - period_seconds
        recent_data = [v for v in self.vitality_history if v.timestamp > cutoff_time]
        
        if not recent_data:
            return {'error': 'No data in specified time period'}
        
        # Analyze patterns
        patterns = {
            'data_points': len(recent_data),
            'time_range': {
                'start': min(v.timestamp for v in recent_data),
                'end': max(v.timestamp for v in recent_data)
            },
            'metrics': {}
        }
        
        # Analyze each metric
        for metric in ['heart_rate', 'sleep_hours', 'exercise_minutes', 'stress_level', 'energy_level']:
            values = [getattr(v, metric, None) for v in recent_data if getattr(v, metric, None) is not None]
            if values:
                patterns['metrics'][metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'trend': self._calculate_trend(values)
                }
        
        return patterns
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # Simple linear trend
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        if abs(slope) < 0.01:
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'
    
    def _generate_health_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from health patterns"""
        insights = []
        
        metrics = patterns.get('metrics', {})
        
        # Heart rate insights
        hr_data = metrics.get('heart_rate', {})
        if hr_data:
            hr_mean = hr_data.get('mean', 0)
            if hr_mean > self.health_thresholds['heart_rate']['resting_max']:
                insights.append("Resting heart rate trend is elevated - consider stress management")
            elif hr_mean < self.health_thresholds['heart_rate']['resting_min']:
                insights.append("Resting heart rate is low - monitor for overtraining")
        
        # Sleep insights
        sleep_data = metrics.get('sleep_hours', {})
        if sleep_data:
            sleep_mean = sleep_data.get('mean', 0)
            if sleep_mean < self.health_thresholds['sleep']['minimum_hours']:
                insights.append("Sleep duration is consistently below recommended levels")
            elif sleep_mean > self.health_thresholds['sleep']['optimal_hours']:
                insights.append("Sleep duration is above optimal - monitor for sleep quality")
        
        # Exercise insights
        exercise_data = metrics.get('exercise_minutes', {})
        if exercise_data:
            exercise_mean = exercise_data.get('mean', 0)
            if exercise_mean < self.health_thresholds['exercise']['minimum_minutes']:
                insights.append("Exercise levels are consistently below minimum recommendations")
            elif exercise_mean > self.health_thresholds['exercise']['target_minutes']:
                insights.append("Exercise levels meet or exceed target recommendations")
        
        return insights
    
    async def _generate_pattern_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on patterns"""
        recommendations = []
        
        metrics = patterns.get('metrics', {})
        
        for metric, data in metrics.items():
            trend = data.get('trend', 'stable')
            
            if metric == 'stress_level' and trend == 'increasing':
                recommendations.append("Implement daily stress reduction practices")
            elif metric == 'sleep_hours' and trend == 'decreasing':
                recommendations.append("Prioritize sleep hygiene and schedule consistency")
            elif metric == 'exercise_minutes' and trend == 'decreasing':
                recommendations.append("Gradually increase physical activity levels")
            elif metric == 'energy_level' and trend == 'decreasing':
                recommendations.append("Focus on recovery and nutrition optimization")
        
        return recommendations
    
    async def _handle_generate_health_recommendations(self, directive: BARKDirective, message):
        """Generate comprehensive health recommendations"""
        try:
            recommendation_type = directive.parameters.get('type', 'comprehensive')
            priority_focus = directive.parameters.get('focus', 'overall_wellness')
            
            # Generate optimization recommendations
            optimization = await self._generate_health_optimization(recommendation_type, priority_focus)
            
            response = BARKResponse(
                response_id=f"health_rec_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result=optimization
            )
            
        except Exception as e:
            response = BARKResponse(
                response_id=f"health_rec_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="error",
                result={'error': str(e)}
            )
        
        return response
    
    async def _generate_health_optimization(self, recommendation_type: str, priority_focus: str) -> Dict[str, Any]:
        """Generate health optimization recommendations"""
        
        # Analyze current vitality state
        current_metrics = self.current_vitality.to_dict()
        
        optimization = HealthOptimization(
            recommended_actions=[],
            priority_score=0.0,
            energy_impact={},
            timeline="immediate",
            compliance_requirements=[]
        )
        
        # Generate targeted recommendations
        if priority_focus == 'energy_optimization':
            optimization = self._optimize_energy_levels(current_metrics)
        elif priority_focus == 'stress_reduction':
            optimization = self._optimize_stress_management(current_metrics)
        elif priority_focus == 'sleep_optimization':
            optimization = self._optimize_sleep_quality(current_metrics)
        elif priority_focus == 'fitness_optimization':
            optimization = self._optimize_fitness_levels(current_metrics)
        else:  # comprehensive
            optimization = self._comprehensive_health_optimization(current_metrics)
        
        return asdict(optimization)
    
    def _optimize_energy_levels(self, metrics: Dict[str, float]) -> HealthOptimization:
        """Optimize energy levels"""
        recommendations = []
        energy_impact = {}
        
        # Sleep optimization
        sleep_hours = metrics.get('sleep_hours', 8)
        if sleep_hours < 8:
            recommendations.append("Increase sleep duration to 7-9 hours")
            energy_impact['sleep_optimization'] = 0.8
        
        # Exercise optimization
        exercise_minutes = metrics.get('exercise_minutes', 30)
        if exercise_minutes < 150:  # Weekly target
            recommendations.append("Schedule moderate exercise 3-5 times per week")
            energy_impact['regular_exercise'] = 0.7
        
        # Nutrition optimization
        nutrition_score = metrics.get('nutrition_score', 6)
        if nutrition_score < 7:
            recommendations.append("Focus on balanced nutrition with adequate protein")
            energy_impact['nutrition_optimization'] = 0.6
        
        return HealthOptimization(
            recommended_actions=recommendations,
            priority_score=sum(energy_impact.values()) / len(energy_impact) if energy_impact else 0.0,
            energy_impact=energy_impact,
            timeline="2-4 weeks",
            compliance_requirements=["consistent_schedule", "progress_tracking"]
        )
    
    def _comprehensive_health_optimization(self, metrics: Dict[str, float]) -> HealthOptimization:
        """Comprehensive health optimization"""
        all_recommendations = []
        all_impacts = {}
        
        # Address all suboptimal metrics
        for metric, value in metrics.items():
            if metric in self.health_thresholds:
                threshold = self.health_thresholds[metric]
                
                if metric == 'heart_rate':
                    if value > threshold['resting_max']:
                        all_recommendations.append("Implement stress management techniques")
                        all_impacts['stress_reduction'] = 0.9
                    elif value < threshold['resting_min']:
                        all_recommendations.append("Ensure adequate hydration and check training intensity")
                        all_impacts['heart_rate_normalization'] = 0.7
                
                elif metric == 'sleep_hours':
                    if value < threshold['minimum_hours']:
                        all_recommendations.append("Prioritize sleep schedule and sleep environment")
                        all_impacts['sleep_optimization'] = 1.0
                
                elif metric == 'exercise_minutes':
                    if value < threshold['minimum_minutes']:
                        all_recommendations.append("Establish regular exercise routine")
                        all_impacts['fitness_improvement'] = 0.8
                
                elif metric == 'stress_level':
                    if value > threshold['moderate_max']:
                        all_recommendations.append("Daily stress reduction practices")
                        all_impacts['stress_management'] = 0.9
        
        return HealthOptimization(
            recommended_actions=list(set(all_recommendations)),  # Remove duplicates
            priority_score=sum(all_impacts.values()) / len(all_impacts) if all_impacts else 0.0,
            energy_impact=all_impacts,
            timeline="4-8 weeks",
            compliance_requirements=["consistent_implementation", "regular_monitoring", "adjustment_based_on_progress"]
        )
    
    def _assess_data_quality(self, processed_data: Dict[str, float]) -> Dict[str, Any]:
        """Assess quality of processed bio-data"""
        quality_score = 0.0
        quality_issues = []
        
        for metric, value in processed_data.items():
            if value is None or value < 0:
                quality_issues.append(f"{metric}: missing or negative value")
            elif metric == 'heart_rate' and (value < 40 or value > 220):
                quality_issues.append(f"{metric}: physiologically unlikely value ({value})")
            elif metric == 'sleep_hours' and (value < 0 or value > 16):
                quality_issues.append(f"{metric}: unrealistic duration ({value})")
            else:
                quality_score += 1.0
        
        total_metrics = len(processed_data)
        quality_score = quality_score / total_metrics if total_metrics > 0 else 0.0
        
        return {
            'score': quality_score,
            'issues': quality_issues,
            'total_metrics': total_metrics
        }
    
    async def _handle_coordinate_wealth_health(self, directive: BARKDirective, message):
        """Coordinate health decisions with wealth node"""
        try:
            health_request = directive.parameters.get('health_request', {})
            context = directive.parameters.get('context', {})
            
            # Analyze health impact on financial decisions
            health_impact = await self._analyze_health_financial_impact(health_request, context)
            
            response = BARKResponse(
                response_id=f"wealth_health_coord_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result=health_impact
            )
            
        except Exception as e:
            response = BARKResponse(
                response_id=f"wealth_health_coord_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="error",
                result={'error': str(e)}
            )
        
        return response
    
    async def _analyze_health_financial_impact(self, health_request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how health decisions impact financial goals"""
        
        current_metrics = self.current_vitality.to_dict()
        analysis = {
            'health_score': 0.0,
            'financial_impact': {},
            'recommendations': [],
            'risk_assessment': {}
        }
        
        # Calculate overall health score
        health_score = 0.0
        metrics_count = 0
        
        for metric, value in current_metrics.items():
            if value is not None:
                metrics_count += 1
                if metric == 'energy_level':
                    health_score += value / 10.0
                elif metric == 'recovery_score':
                    health_score += value / 10.0
                elif metric == 'stress_level':
                    health_score += (10 - value) / 10.0  # Invert stress
                else:
                    # Normalize other metrics to 0-1 range
                    if metric == 'heart_rate':
                        health_score += min(1.0, max(0, (100 - abs(value - 70)) / 50))
                    elif metric == 'sleep_hours':
                        health_score += min(1.0, value / 8.0)
                    elif metric == 'exercise_minutes':
                        health_score += min(1.0, value / 30.0)
        
        analysis['health_score'] = health_score / metrics_count if metrics_count > 0 else 0.0
        
        # Assess financial impact based on health
        if analysis['health_score'] < 0.6:
            analysis['financial_impact']['productivity_risk'] = 'high'
            analysis['recommendations'].append("Prioritize health optimization to maintain productivity")
        elif analysis['health_score'] > 0.8:
            analysis['financial_impact']['productivity_risk'] = 'low'
        
        # Long-term health costs
        if current_metrics.get('stress_level', 5) > 7:
            analysis['financial_impact']['long_term_health_costs'] = 'elevated'
            analysis['recommendations'].append("Invest in stress reduction to prevent future health costs")
        
        return analysis
    
    def get_vitality_status(self) -> Dict[str, Any]:
        """Get current vitality status"""
        return {
            'node_id': self.node_id,
            'current_metrics': self.current_vitality.to_dict(),
            'health_thresholds': self.health_thresholds,
            'data_history_size': len(self.vitality_history),
            'recommendations_count': len(self.optimization_cache),
            'vitality_score': self._calculate_overall_vitality_score()
        }
    
    def _calculate_overall_vitality_score(self) -> float:
        """Calculate overall vitality score"""
        metrics = self.current_vitality.to_dict()
        score = 0.0
        count = 0
        
        for metric, value in metrics.items():
            if value is not None and metric != 'timestamp':
                count += 1
                if metric == 'stress_level':
                    score += (10 - value) / 10.0  # Lower stress is better
                else:
                    score += min(1.0, value / 10.0)
        
        return score / count if count > 0 else 0.0

# Example usage and testing
if __name__ == "__main__":
    async def test_vitality_node():
        # Initialize vitality node
        config_path = Path("../config/lex_config.yaml")
        vit_node = LexVitalityNode(config_path, "test_vit_001")
        
        print("LEX-7 Vitality Node Test")
        print("=" * 40)
        
        # Test bio-data ingestion
        bio_data = {
            'heart_rate': 75,
            'sleep_hours': 7.5,
            'exercise_minutes': 45,
            'stress_level': 4,
            'nutrition_score': 7
        }
        
        print("\n1. Testing Bio-data Ingestion:")
        # Simulate directive processing
        from ..communication.bark_protocol import create_test_directive
        
        directive = create_test_directive("ingest_bio_data", {
            'bio_data': bio_data,
            'sensor_type': 'manual'
        })
        
        # In real implementation, this would be processed through the BARK protocol
        print(f"Would process bio-data: {bio_data}")
        
        # Test health pattern analysis
        print("\n2. Testing Health Pattern Analysis:")
        pattern_directive = create_test_directive("analyze_health_patterns", {
            'time_period': '7_days',
            'pattern_type': 'comprehensive'
        })
        
        print(f"Would analyze patterns for: {pattern_directive.parameters}")
        
        # Show current status
        print("\n3. Current Vitality Status:")
        status = vit_node.get_vitality_status()
        print(f"Health Score: {status['vitality_score']:.2f}")
        print(f"Data Points: {status['data_history_size']}")
        
        await vit_node.shutdown()
        print("\nVitality node test completed")
    
    # Run the test
    asyncio.run(test_vitality_node())
