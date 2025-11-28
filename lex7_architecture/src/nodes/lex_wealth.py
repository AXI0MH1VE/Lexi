#!/usr/bin/env python3
"""
LEX-WEALTH NODE - Financial State Management
Specialized Lex Node for financial optimization and wealth preservation
Part of the LEX-7 Sovereign Lattice - Enforces Axiom Hive financial discipline
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
class WealthMetrics:
    """Represents financial wealth metrics"""
    cash_balance: Optional[float] = None
    monthly_expenses: Optional[float] = None
    monthly_income: Optional[float] = None
    runway_months: Optional[float] = None
    investment_portfolio: Optional[float] = None
    debt_total: Optional[float] = None
    savings_rate: Optional[float] = None
    spending_velocity: Optional[float] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WealthMetrics':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class FinancialOptimization:
    """Financial optimization recommendations"""
    recommended_actions: List[str]
    priority_score: float
    runway_impact: Dict[str, float]
    timeline: str
    compliance_requirements: List[str]
    risk_assessment: Dict[str, str]

class AxiomEnforcer:
    """
    Axiom Hive Financial Rule Enforcement
    
    Enforces your sovereign financial axioms through the Error-State Model
    """
    
    def __init__(self):
        self.financial_axioms = self._load_financial_axioms()
        self.violation_history = []
    
    def _load_financial_axioms(self) -> List[Dict[str, Any]]:
        """Load financial axioms from Axiom Hive"""
        return [
            {
                "id": "runway_preservation",
                "type": "wealth_preservation",
                "rule": "never_spend_more_than_10_percent_of_runway_without_approval",
                "weight": 1.0,
                "mandatory": True,
                "threshold": 0.10
            },
            {
                "id": "emergency_fund",
                "type": "risk_management", 
                "rule": "maintain_minimum_6_months_expenses_in_emergency_fund",
                "weight": 0.9,
                "mandatory": True,
                "threshold": 6.0
            },
            {
                "id": "investment_discipline",
                "type": "wealth_building",
                "rule": "invest_only_instruments_that_preserve_principal",
                "weight": 0.8,
                "mandatory": False,
                "allowed_risk_level": "conservative"
            },
            {
                "id": "expense_optimization",
                "type": "efficiency",
                "rule": "eliminate_all_expenses_that_dont_align_with_core_objectives",
                "weight": 0.7,
                "mandatory": False,
                "efficiency_threshold": 0.8
            },
            {
                "id": "debt_elimination",
                "type": "risk_management",
                "rule": "eliminate_high_interest_debt_before_investing",
                "weight": 0.9,
                "mandatory": True,
                "max_acceptable_rate": 0.05
            }
        ]
    
    def validate_financial_action(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate financial action against axioms"""
        validation_result = {
            "valid": True,
            "violations": [],
            "warnings": [],
            "compliance_score": 1.0,
            "required_modifications": []
        }
        
        action_type = action.get("type", "")
        amount = action.get("amount", 0)
        
        # Check each axiom
        for axiom in self.financial_axioms:
            axiom_result = self._check_axiom_compliance(action, context, axiom)
            
            if not axiom_result["compliant"]:
                if axiom["mandatory"]:
                    validation_result["valid"] = False
                    validation_result["violations"].append({
                        "axiom_id": axiom["id"],
                        "rule": axiom["rule"],
                        "violation_details": axiom_result["details"]
                    })
                else:
                    validation_result["warnings"].append({
                        "axiom_id": axiom["id"],
                        "rule": axiom["rule"],
                        "warning_details": axiom_result["details"]
                    })
                    
                validation_result["compliance_score"] *= (1.0 - axiom["weight"])
            else:
                # Add suggestions for optimization
                if axiom_result.get("suggestions"):
                    validation_result["required_modifications"].extend(axiom_result["suggestions"])
        
        return validation_result
    
    def _check_axiom_compliance(self, action: Dict[str, Any], context: Dict[str, Any], axiom: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with specific axiom"""
        axiom_type = axiom["type"]
        rule = axiom["rule"]
        
        if axiom_type == "wealth_preservation":
            return self._check_runway_preservation(action, context, axiom)
        elif axiom_type == "risk_management":
            return self._check_risk_management(action, context, axiom)
        elif axiom_type == "wealth_building":
            return self._check_wealth_building(action, context, axiom)
        elif axiom_type == "efficiency":
            return self._check_efficiency(action, context, axiom)
        
        return {"compliant": True, "details": "No validation applicable"}
    
    def _check_runway_preservation(self, action: Dict[str, Any], context: Dict[str, Any], axiom: Dict[str, Any]) -> Dict[str, Any]:
        """Check runway preservation axiom"""
        if action.get("type") in ["spend", "purchase", "investment"]:
            runway_months = context.get("runway_months", float('inf'))
            amount = action.get("amount", 0)
            monthly_expenses = context.get("monthly_expenses", 1)
            
            # Calculate impact as percentage of runway
            monthly_impact = amount / monthly_expenses if monthly_expenses > 0 else 0
            runway_impact = monthly_impact / runway_months if runway_months > 0 else 0
            
            threshold = axiom["threshold"]
            if runway_impact > threshold:
                return {
                    "compliant": False,
                    "details": f"Action impact ({runway_impact:.1%}) exceeds allowable threshold ({threshold:.1%})",
                    "suggestions": [
                        f"Reduce amount to {(threshold * runway_months * monthly_expenses):.0f}",
                        "Wait for increased runway",
                        "Seek alternative lower-cost options"
                    ]
                }
        
        return {"compliant": True, "details": "Runway preservation maintained"}
    
    def _check_risk_management(self, action: Dict[str, Any], context: Dict[str, Any], axiom: Dict[str, Any]) -> Dict[str, Any]:
        """Check risk management axioms"""
        if axiom["id"] == "emergency_fund":
            emergency_fund_months = context.get("emergency_fund_months", 0)
            required_months = axiom["threshold"]
            
            if emergency_fund_months < required_months:
                return {
                    "compliant": False,
                    "details": f"Emergency fund ({emergency_fund_months:.1f} months) below required ({required_monthf} months)",
                    "suggestions": [
                        f"Prioritize building emergency fund to {required_months} months",
                        "Reduce non-essential spending",
                        "Allocate windfalls to emergency fund"
                    ]
                }
        
        elif axiom["id"] == "debt_elimination":
            if action.get("type") == "investment":
                interest_rate = action.get("interest_rate", 0)
                max_rate = axiom["max_acceptable_rate"]
                
                if interest_rate > max_rate:
                    return {
                        "compliant": False,
                        "details": f"Investment interest rate ({interest_rate:.1%}) exceeds max acceptable ({max_rate:.1%})",
                        "suggestions": [
                            "Focus on debt elimination first",
                            "Consider lower-risk alternatives",
                            "Negotiate better terms"
                        ]
                    }
        
        return {"compliant": True, "details": "Risk management criteria met"}
    
    def _check_wealth_building(self, action: Dict[str, Any], context: Dict[str, Any], axiom: Dict[str, Any]) -> Dict[str, Any]:
        """Check wealth building axioms"""
        if action.get("type") == "investment":
            risk_level = action.get("risk_level", "conservative")
            allowed_risk = axiom["allowed_risk_level"]
            
            if risk_level != allowed_risk and risk_level not in ["low", "moderate"]:
                return {
                    "compliant": False,
                    "details": f"Investment risk level ({risk_level}) exceeds conservative guidelines",
                    "suggestions": [
                        "Focus on principal-preserving investments",
                        "Diversify with lower-risk instruments",
                        "Consider index funds with conservative allocation"
                    ]
                }
        
        return {"compliant": True, "details": "Wealth building principles maintained"}
    
    def _check_efficiency(self, action: Dict[str, Any], context: Dict[str, Any], axiom: Dict[str, Any]) -> Dict[str, Any]:
        """Check efficiency axioms"""
        if action.get("type") in ["purchase", "subscription"]:
            purpose = action.get("purpose", "")
            value_score = action.get("value_score", 1.0)
            efficiency_threshold = axiom["efficiency_threshold"]
            
            if value_score < efficiency_threshold:
                return {
                    "compliant": False,
                    "details": f"Expense efficiency ({value_score:.1f}) below threshold ({efficiency_threshold:.1f})",
                    "suggestions": [
                        "Evaluate if expense aligns with core objectives",
                        "Seek more cost-effective alternatives",
                        "Negotiate better terms or discounts"
                    ]
                }
        
        return {"compliant": True, "details": "Expense efficiency criteria met"}

class LexWealthNode(LexNode):
    """
    Lex Wealth Node
    
    Specialized for financial state management and wealth preservation.
    Enforces Axiom Hive financial discipline through the Error-State Model.
    """
    
    def __init__(self, config_path: Path, node_id: str = "lex_wth_001"):
        super().__init__(config_path, node_id)
        
        # Wealth-specific state
        self.current_wealth = WealthMetrics()
        self.wealth_history: List[WealthMetrics] = []
        self.financial_goals = {}
        self.optimization_cache = {}
        
        # Financial processing capabilities
        self.axiom_enforcer = AxiomEnforcer()
        self.risk_thresholds = self._initialize_risk_thresholds()
        self.wealth_model = None
        
        # Register wealth-specific directive handlers
        self._register_wealth_handlers()
        
        logger.info(f"Lex Wealth Node {node_id} initialized")
    
    def _initialize_risk_thresholds(self) -> Dict[str, float]:
        """Initialize financial risk threshold values"""
        return {
            'runway_months': {
                'minimum_emergency': 3.0,
                'minimum_comfortable': 6.0,
                'optimal_target': 12.0,
                'conservative_target': 18.0
            },
            'debt_to_income': {
                'maximum_acceptable': 0.36,
                'conservative_maximum': 0.28,
                'optimal_target': 0.20
            },
            'savings_rate': {
                'minimum_target': 0.20,
                'optimal_target': 0.30,
                'aggressive_target': 0.50
            },
            'investment_allocation': {
                'conservative_max_equity': 0.60,
                'moderate_max_equity': 0.80,
                'aggressive_min_equity': 0.80
            }
        }
    
    def _register_wealth_handlers(self):
        """Register wealth-specific directive handlers"""
        
        # Financial data ingestion
        self.register_directive_handler("ingest_financial_data", self._handle_ingest_financial_data)
        self.register_directive_handler("update_wealth_metrics", self._handle_update_wealth_metrics)
        
        # Financial analysis
        self.register_directive_handler("analyze_spending_patterns", self._handle_analyze_spending_patterns)
        self.register_directive_handler("calculate_runway", self._handle_calculate_runway)
        self.register_directive_handler("assess_financial_risk", self._handle_assess_financial_risk)
        
        # Financial optimization
        self.register_directive_handler("optimize_expenses", self._handle_optimize_expenses)
        self.register_directive_handler("plan_investment_strategy", self._handle_plan_investment_strategy)
        self.register_directive_handler("budget_recommendations", self._handle_budget_recommendations)
        
        # Axiom enforcement
        self.register_directive_handler("validate_financial_action", self._handle_validate_financial_action)
        self.register_directive_handler("check_axiom_compliance", self._handle_check_axiom_compliance)
        
        # Cross-node coordination
        self.register_directive_handler("coordinate_health_wealth", self._handle_coordinate_health_wealth)
        self.register_directive_handler("get_financial_clearance", self._handle_get_financial_clearance)
    
    async def _handle_ingest_financial_data(self, directive: BARKDirective, message):
        """Handle financial data ingestion"""
        try:
            financial_data = directive.parameters.get('financial_data', {})
            data_source = directive.parameters.get('source', 'manual')
            
            # Process financial data through Lex-Mamba kernel
            processed_data = await self._process_financial_data(financial_data, data_source)
            
            # Update wealth metrics
            self.current_wealth = WealthMetrics(**processed_data)
            self.wealth_history.append(self.current_wealth)
            
            # Limit history size
            if len(self.wealth_history) > 1000:
                self.wealth_history.pop(0)
            
            # Validate against axioms
            axiom_compliance = self._validate_current_state()
            
            # Generate recommendations
            recommendations = await self._generate_financial_recommendations()
            
            response = BARKResponse(
                response_id=f"financial_ingest_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result={
                    'processed_metrics': self.current_wealth.to_dict(),
                    'axiom_compliance': axiom_compliance,
                    'recommendations': recommendations,
                    'data_quality': self._assess_financial_data_quality(processed_data)
                }
            )
            
        except Exception as e:
            response = BARKResponse(
                response_id=f"financial_ingest_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="error",
                result={'error': str(e)}
            )
        
        return response
    
    async def _process_financial_data(self, financial_data: Dict[str, Any], source: str) -> Dict[str, float]:
        """Process raw financial data through the Error-State Model"""
        
        # Convert financial data to state-space input
        financial_tensor = self._financial_data_to_tensor(financial_data)
        
        # Process through Lex-Mamba kernel
        h_t, y_pred, error_signal = self.kernel.kernel.forward(financial_tensor, self.current_state)
        
        # Update current state
        self.current_state = h_t
        
        # Extract processed metrics
        processed_metrics = self._tensor_to_wealth_metrics(y_pred, financial_data)
        
        return processed_metrics
    
    def _financial_data_to_tensor(self, financial_data: Dict[str, Any]) -> torch.Tensor:
        """Convert financial data to state-space input tensor"""
        state_dim = self.config['model']['state_dim']
        input_tensor = torch.zeros(state_dim)
        
        # Encode financial data channels
        channels = {
            'cash_balance': (financial_data.get('cash_balance', 10000) / 100000),  # Normalize to 100k
            'monthly_expenses': (financial_data.get('monthly_expenses', 5000) / 10000),  # Normalize to 10k
            'monthly_income': (financial_data.get('monthly_income', 8000) / 15000),  # Normalize to 15k
            'investment_portfolio': (financial_data.get('investment_portfolio', 50000) / 200000),  # Normalize to 200k
            'debt_total': (financial_data.get('debt_total', 0) / 50000)  # Normalize to 50k
        }
        
        # Distribute across tensor dimensions
        for i, (metric, value) in enumerate(channels.items()):
            if i < state_dim:
                input_tensor[i] = value
        
        return input_tensor.unsqueeze(0)
    
    def _tensor_to_wealth_metrics(self, tensor: torch.Tensor, raw_financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Convert model output to wealth metrics"""
        tensor_np = tensor.squeeze(0).detach().numpy()
        
        # Calculate derived metrics
        cash_balance = raw_financial_data.get('cash_balance', 10000)
        monthly_expenses = raw_financial_data.get('monthly_expenses', 5000)
        monthly_income = raw_financial_data.get('monthly_income', 8000)
        investment_portfolio = raw_financial_data.get('investment_portfolio', 50000)
        debt_total = raw_financial_data.get('debt_total', 0)
        
        # Runway calculation
        runway_months = cash_balance / monthly_expenses if monthly_expenses > 0 else float('inf')
        
        # Savings rate
        savings_rate = (monthly_income - monthly_expenses) / monthly_income if monthly_income > 0 else 0
        
        # Spending velocity (trend)
        spending_velocity = self._calculate_spending_velocity()
        
        metrics = {
            'cash_balance': cash_balance,
            'monthly_expenses': monthly_expenses,
            'monthly_income': monthly_income,
            'runway_months': runway_months,
            'investment_portfolio': investment_portfolio,
            'debt_total': debt_total,
            'savings_rate': max(0, min(1, savings_rate)),  # Clamp to 0-1
            'spending_velocity': spending_velocity
        }
        
        return metrics
    
    def _calculate_spending_velocity(self) -> float:
        """Calculate spending velocity trend"""
        if len(self.wealth_history) < 2:
            return 0.0
        
        # Simple spending trend calculation
        recent_expenses = [w.monthly_expenses for w in self.wealth_history[-6:] if w.monthly_expenses]
        if len(recent_expenses) < 2:
            return 0.0
        
        # Calculate trend
        x = list(range(len(recent_expenses)))
        trend = np.polyfit(x, recent_expenses, 1)[0]
        
        # Normalize trend as percentage change
        avg_expense = np.mean(recent_expenses)
        velocity = (trend / avg_expense) * 100 if avg_expense > 0 else 0
        
        return max(-20, min(20, velocity))  # Cap between -20% and +20%
    
    def _validate_current_state(self) -> Dict[str, Any]:
        """Validate current financial state against axioms"""
        validation_result = {
            "overall_compliance": 1.0,
            "violations": [],
            "warnings": [],
            "axiom_scores": {}
        }
        
        # Create synthetic action for state validation
        state_action = {"type": "state_validation", "amount": 0}
        context = self.current_wealth.to_dict()
        
        # Check each axiom
        for axiom in self.axiom_enforcer.financial_axioms:
            result = self.axiom_enforcer._check_axiom_compliance(state_action, context, axiom)
            
            compliance_score = 1.0 if result["compliant"] else (1.0 - axiom["weight"])
            validation_result["axiom_scores"][axiom["id"]] = compliance_score
            
            if not result["compliant"]:
                if axiom["mandatory"]:
                    validation_result["violations"].append({
                        "axiom_id": axiom["id"],
                        "details": result["details"]
                    })
                    validation_result["overall_compliance"] *= (1.0 - axiom["weight"])
                else:
                    validation_result["warnings"].append({
                        "axiom_id": axiom["id"],
                        "details": result["details"]
                    })
        
        return validation_result
    
    async def _generate_financial_recommendations(self) -> List[str]:
        """Generate financial recommendations based on current state"""
        recommendations = []
        
        metrics = self.current_wealth.to_dict()
        
        # Check runway
        runway = metrics.get('runway_months', 0)
        if runway < self.risk_thresholds['runway_months']['minimum_emergency']:
            recommendations.append("CRITICAL: Build emergency fund immediately - current runway is dangerously low")
        elif runway < self.risk_thresholds['runway_months']['minimum_comfortable']:
            recommendations.append("Increase emergency fund to 6 months of expenses")
        elif runway < self.risk_thresholds['runway_months']['optimal_target']:
            recommendations.append("Continue building runway toward 12-month target")
        
        # Check savings rate
        savings_rate = metrics.get('savings_rate', 0)
        if savings_rate < self.risk_thresholds['savings_rate']['minimum_target']:
            recommendations.append(f"Increase savings rate from {savings_rate:.1%} to at least {self.risk_thresholds['savings_rate']['minimum_target']:.0%}")
        
        # Check debt
        debt_total = metrics.get('debt_total', 0)
        monthly_income = metrics.get('monthly_income', 1)
        debt_to_income = debt_total / (monthly_income * 12) if monthly_income > 0 else 0
        
        if debt_to_income > self.risk_thresholds['debt_to_income']['maximum_acceptable']:
            recommendations.append("Reduce debt-to-income ratio below 36%")
        
        # Check spending velocity
        spending_velocity = metrics.get('spending_velocity', 0)
        if spending_velocity > 5:
            recommendations.append("Spending is increasing rapidly - review and optimize expenses")
        elif spending_velocity < -5:
            recommendations.append("Positive trend: spending is decreasing")
        
        return recommendations
    
    async def _handle_validate_financial_action(self, directive: BARKDirective, message):
        """Validate financial action against axioms"""
        try:
            action = directive.parameters.get('action', {})
            context = directive.parameters.get('context', self.current_wealth.to_dict())
            
            # Validate action
            validation_result = self.axiom_enforcer.validate_financial_action(action, context)
            
            # Generate compliance recommendations
            compliance_recommendations = self._generate_compliance_recommendations(validation_result)
            
            response = BARKResponse(
                response_id=f"action_validation_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result={
                    'validation': validation_result,
                    'recommendations': compliance_recommendations,
                    'risk_level': self._assess_action_risk_level(action, context)
                }
            )
            
        except Exception as e:
            response = BARKResponse(
                response_id=f"action_validation_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="error",
                result={'error': str(e)}
            )
        
        return response
    
    def _generate_compliance_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations to improve compliance"""
        recommendations = []
        
        for violation in validation_result["violations"]:
            recommendations.append(f"Address violation of {violation['axiom_id']}: {violation['rule']}")
        
        for warning in validation_result["warnings"]:
            recommendations.append(f"Consider optimization for {warning['axiom_id']}: {warning['rule']}")
        
        for modification in validation_result["required_modifications"]:
            recommendations.append(f"Recommended modification: {modification}")
        
        return recommendations
    
    def _assess_action_risk_level(self, action: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Assess risk level of financial action"""
        risk_factors = 0
        
        # Check amount relative to runway
        amount = action.get("amount", 0)
        runway_months = context.get("runway_months", float('inf'))
        monthly_expenses = context.get("monthly_expenses", 1)
        
        if runway_months < 6:
            risk_factors += 2
        elif runway_months < 12:
            risk_factors += 1
        
        # Check debt level
        debt_total = context.get("debt_total", 0)
        monthly_income = context.get("monthly_income", 1)
        debt_to_income = debt_total / (monthly_income * 12) if monthly_income > 0 else 0
        
        if debt_to_income > 0.36:
            risk_factors += 2
        elif debt_to_income > 0.28:
            risk_factors += 1
        
        # Check savings rate
        savings_rate = context.get("savings_rate", 0)
        if savings_rate < 0.20:
            risk_factors += 1
        
        # Determine risk level
        if risk_factors >= 4:
            return "high"
        elif risk_factors >= 2:
            return "moderate"
        else:
            return "low"
    
    async def _handle_coordinate_health_wealth(self, directive: BARKDirective, message):
        """Coordinate financial decisions with vitality node"""
        try:
            financial_request = directive.parameters.get('financial_request', {})
            health_context = directive.parameters.get('health_context', {})
            
            # Analyze financial impact of health decisions
            financial_impact = await self._analyze_health_financial_impact(financial_request, health_context)
            
            response = BARKResponse(
                response_id=f"health_wealth_coord_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result=financial_impact
            )
            
        except Exception as e:
            response = BARKResponse(
                response_id=f"health_wealth_coord_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="error",
                result={'error': str(e)}
            )
        
        return response
    
    async def _analyze_health_financial_impact(self, financial_request: Dict[str, Any], health_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how health decisions impact financial goals"""
        
        current_metrics = self.current_wealth.to_dict()
        analysis = {
            'financial_health_score': 0.0,
            'health_investment_priority': {},
            'cost_benefit_analysis': {},
            'recommendations': []
        }
        
        # Calculate financial health score
        financial_score = 0.0
        
        # Runway contribution
        runway = current_metrics.get('runway_months', 0)
        if runway >= 12:
            financial_score += 0.3
        elif runway >= 6:
            financial_score += 0.2
        elif runway >= 3:
            financial_score += 0.1
        
        # Savings rate contribution
        savings_rate = current_metrics.get('savings_rate', 0)
        if savings_rate >= 0.30:
            financial_score += 0.3
        elif savings_rate >= 0.20:
            financial_score += 0.2
        elif savings_rate >= 0.10:
            financial_score += 0.1
        
        # Debt level contribution
        debt_total = current_metrics.get('debt_total', 0)
        monthly_income = current_metrics.get('monthly_income', 1)
        debt_to_income = debt_total / (monthly_income * 12) if monthly_income > 0 else 0
        
        if debt_to_income <= 0.20:
            financial_score += 0.2
        elif debt_to_income <= 0.28:
            financial_score += 0.1
        
        # Emergency fund contribution
        emergency_fund_months = current_metrics.get('cash_balance', 0) / current_metrics.get('monthly_expenses', 1)
        if emergency_fund_months >= 12:
            financial_score += 0.2
        elif emergency_fund_months >= 6:
            financial_score += 0.1
        
        analysis['financial_health_score'] = min(1.0, financial_score)
        
        # Health investment priority
        health_score = health_context.get('health_score', 0.5)
        if health_score < 0.6 and financial_score > 0.7:
            analysis['health_investment_priority'] = {
                'priority': 'high',
                'rationale': 'Good financial health allows health investment',
                'budget_allocation': '5-10% of discretionary income'
            }
        elif health_score > 0.8:
            analysis['health_investment_priority'] = {
                'priority': 'maintenance',
                'rationale': 'Health is optimal, focus on maintenance',
                'budget_allocation': '3-5% of discretionary income'
            }
        
        # Cost-benefit analysis
        potential_health_cost = health_context.get('potential_future_cost', 0)
        preventive_investment = financial_request.get('preventive_investment', 0)
        
        if preventive_investment > 0:
            roi_analysis = {
                'preventive_investment': preventive_investment,
                'potential_cost_avoidance': potential_health_cost,
                'roi_estimate': (potential_health_cost - preventive_investment) / preventive_investment if preventive_investment > 0 else 0
            }
            analysis['cost_benefit_analysis'] = roi_analysis
        
        return analysis
    
    async def _handle_get_financial_clearance(self, directive: BARKDirective, message):
        """Get financial clearance for major decisions"""
        try:
            decision = directive.parameters.get('decision', {})
            context = directive.parameters.get('context', {})
            
            # Comprehensive financial clearance analysis
            clearance = await self._analyze_financial_clearance(decision, context)
            
            response = BARKResponse(
                response_id=f"clearance_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result=clearance
            )
            
        except Exception as e:
            response = BARKResponse(
                response_id=f"clearance_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="error",
                result={'error': str(e)}
            )
        
        return response
    
    async def _analyze_financial_clearance(self, decision: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial clearance for major decisions"""
        
        clearance = {
            'approved': False,
            'confidence_score': 0.0,
            'conditions': [],
            'alternative_suggestions': [],
            'risk_assessment': {}
        }
        
        # Validate against axioms
        validation_result = self.axiom_enforcer.validate_financial_action(decision, context)
        
        # Check approval criteria
        if validation_result['valid'] and validation_result['compliance_score'] >= 0.8:
            clearance['approved'] = True
            clearance['confidence_score'] = validation_result['compliance_score']
        else:
            clearance['confidence_score'] = validation_result['compliance_score']
            if not validation_result['valid']:
                clearance['conditions'].append("Address all mandatory axiom violations")
        
        # Risk assessment
        risk_level = self._assess_action_risk_level(decision, context)
        clearance['risk_assessment'] = {
            'level': risk_level,
            'factors': self._identify_risk_factors(decision, context),
            'mitigation_strategies': self._suggest_risk_mitigation(decision, context, risk_level)
        }
        
        # Alternative suggestions
        if not clearance['approved']:
            clearance['alternative_suggestions'] = self._generate_alternatives(decision, validation_result)
        
        return clearance
    
    def _identify_risk_factors(self, decision: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify risk factors for the decision"""
        risk_factors = []
        
        amount = decision.get("amount", 0)
        runway_months = context.get("runway_months", float('inf'))
        
        if amount > context.get('monthly_expenses', 1) * 2:
            risk_factors.append("Amount exceeds 2 months of expenses")
        
        if runway_months < 6:
            risk_factors.append("Insufficient runway for emergency buffer")
        
        debt_to_income = context.get('debt_total', 0) / (context.get('monthly_income', 1) * 12)
        if debt_to_income > 0.36:
            risk_factors.append("High debt-to-income ratio")
        
        return risk_factors
    
    def _suggest_risk_mitigation(self, decision: Dict[str, Any], context: Dict[str, Any], risk_level: str) -> List[str]:
        """Suggest risk mitigation strategies"""
        strategies = []
        
        if risk_level == "high":
            strategies.extend([
                "Delay decision until runway improves",
                "Reduce amount or find lower-cost alternative",
                "Build emergency fund first"
            ])
        elif risk_level == "moderate":
            strategies.extend([
                "Phase the decision over time",
                "Negotiate better terms or payment plan",
                "Monitor impact on key financial metrics"
            ])
        
        return strategies
    
    def _generate_alternatives(self, decision: Dict[str, Any], validation_result: Dict[str, Any]) -> List[str]:
        """Generate alternative approaches"""
        alternatives = []
        
        # Based on validation violations
        for violation in validation_result.get('violations', []):
            if 'runway' in violation.get('rule', ''):
                alternatives.append("Reduce amount to fit within runway limits")
            elif 'debt' in violation.get('rule', ''):
                alternatives.append("Pay down debt before proceeding")
            elif 'emergency' in violation.get('rule', ''):
                alternatives.append("Build emergency fund first")
        
        return alternatives
    
    def _assess_financial_data_quality(self, processed_data: Dict[str, float]) -> Dict[str, Any]:
        """Assess quality of processed financial data"""
        quality_score = 0.0
        quality_issues = []
        
        required_metrics = ['cash_balance', 'monthly_expenses', 'monthly_income']
        
        for metric in required_metrics:
            value = processed_data.get(metric)
            if value is None or value < 0:
                quality_issues.append(f"{metric}: missing or negative value")
            else:
                quality_score += 1.0
        
        # Additional validation
        monthly_expenses = processed_data.get('monthly_expenses', 0)
        monthly_income = processed_data.get('monthly_income', 0)
        
        if monthly_expenses > monthly_income * 2:
            quality_issues.append("Expenses exceed 2x income - may indicate data error")
        
        if monthly_expenses == 0:
            quality_issues.append("Zero monthly expenses - likely data error")
        
        total_metrics = len(required_metrics)
        quality_score = quality_score / total_metrics if total_metrics > 0 else 0.0
        
        return {
            'score': quality_score,
            'issues': quality_issues,
            'total_metrics': total_metrics
        }
    
    def get_wealth_status(self) -> Dict[str, Any]:
        """Get current wealth status"""
        return {
            'node_id': self.node_id,
            'current_metrics': self.current_wealth.to_dict(),
            'risk_thresholds': self.risk_thresholds,
            'data_history_size': len(self.wealth_history),
            'axiom_compliance': self._validate_current_state(),
            'wealth_score': self._calculate_overall_wealth_score()
        }
    
    def _calculate_overall_wealth_score(self) -> float:
        """Calculate overall wealth score"""
        metrics = self.current_wealth.to_dict()
        score = 0.0
        count = 0
        
        # Runway score (0-1)
        runway = metrics.get('runway_months', 0)
        if runway >= 18:
            runway_score = 1.0
        elif runway >= 12:
            runway_score = 0.8
        elif runway >= 6:
            runway_score = 0.6
        elif runway >= 3:
            runway_score = 0.3
        else:
            runway_score = 0.0
        
        score += runway_score
        count += 1
        
        # Savings rate score (0-1)
        savings_rate = metrics.get('savings_rate', 0)
        savings_score = min(1.0, savings_rate / 0.30)  # 30% is excellent
        
        score += savings_score
        count += 1
        
        # Debt score (0-1, lower debt is better)
        debt_total = metrics.get('debt_total', 0)
        monthly_income = metrics.get('monthly_income', 1)
        debt_to_income = debt_total / (monthly_income * 12) if monthly_income > 0 else 0
        
        if debt_to_income <= 0.20:
            debt_score = 1.0
        elif debt_to_income <= 0.28:
            debt_score = 0.7
        elif debt_to_income <= 0.36:
            debt_score = 0.4
        else:
            debt_score = 0.0
        
        score += debt_score
        count += 1
        
        return score / count if count > 0 else 0.0

# Example usage and testing
if __name__ == "__main__":
    async def test_wealth_node():
        # Initialize wealth node
        config_path = Path("../config/lex_config.yaml")
        wealth_node = LexWealthNode(config_path, "test_wth_001")
        
        print("LEX-7 Wealth Node Test")
        print("=" * 40)
        
        # Test financial data ingestion
        financial_data = {
            'cash_balance': 15000,
            'monthly_expenses': 4500,
            'monthly_income': 7500,
            'investment_portfolio': 85000,
            'debt_total': 12000
        }
        
        print("\n1. Testing Financial Data Ingestion:")
        from ..communication.bark_protocol import create_test_directive
        
        directive = create_test_directive("ingest_financial_data", {
            'financial_data': financial_data,
            'source': 'manual'
        })
        
        print(f"Would process financial data: {financial_data}")
        
        # Test action validation
        print("\n2. Testing Financial Action Validation:")
        test_action = {
            'type': 'purchase',
            'amount': 2000,
            'category': 'electronics',
            'purpose': 'work_equipment'
        }
        
        validation = wealth_node.axiom_enforcer.validate_financial_action(test_action, financial_data)
        print(f"Action validation: {validation}")
        
        # Show current status
        print("\n3. Current Wealth Status:")
        status = wealth_node.get_wealth_status()
        print(f"Wealth Score: {status['wealth_score']:.2f}")
        print(f"Runway: {status['current_metrics']['runway_months']:.1f} months")
        print(f"Compliance: {status['axiom_compliance']['overall_compliance']:.2f}")
        
        await wealth_node.shutdown()
        print("\nWealth node test completed")
    
    # Run the test
    asyncio.run(test_wealth_node())
