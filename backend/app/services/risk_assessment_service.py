import numpy as np
import pandas as pd
from typing import Dict,Any,List
from dataclasses import dataclass


@dataclass
class RiskProfile:
    risk_score:float
    risk_category:str
    volatility_tolerance:float
    time_horizon:int
    liquidity_needs:float


class RiskAssessmentService:
    def __init__(self):
        self.risk_categories={
            (0,20):"Very Conservative",
            (20,40):"Conservative",
            (40,60):"Moderate",
            (60,80):"Aggressive",
            (80,100):"Very Agressive"  
        }

    
    def assess_risk_profile(self,financial_data:Dict[str,Any],
                            user_preferences:Dict[str,Any]=None)->RiskProfile:
        """Assess user's risk profile based on financial data and preferences"""


        #calculate financial stability score
        stability_score = self._calculate_stability_score(financial_data)

        volatility_score = self._calculate_volatility_score(financial_data)

        liquidity_score = self._calculate_liquidity_score(financial_data)

        age_score = self._calculate_age_Score(user_preferences)
        debt_score = self._calculate_debt_score(financial_data)

        #combining scores
        risk_score=(
            stability_score*0.25 +
            volatility_score*0.20 +
            liquidity_score*0.20 +
            age_score*0.20+
            debt_score*0.15
        )

        #determine category
        risk_category = self._get_risk_category(risk_score)

        return RiskProfile(
            risk_score=risk_score,
            risk_category=risk_category,
            volatility_tolerance=100-volatility_score,
            time_horizon=self._calculate_time_horizon(user_preferences),
            liquidity_needs=liquidity_score
        )
    
    def _calculate_stability_score(self,financial_data:Dict[str,Any])->float:
        """calculate financial stability score"""
        monthly_income = financial_data.get('monthly_income',0)
        monthly_expenses = financial_data.get('monthly_expenses',0)
        emergency_fund = financial_data.get('emergency_fund',0)


        #emergency fund ratio
        if monthly_expenses>0:
            emergency_ratio = emergency_fund/monthly_expenses
            emergency_score = min(emergency_ratio*20,60)
        else:
            emergency_score=0

        if monthly_income>0:
            surplus_ratio = (monthly_income-monthly_expenses)/monthly_income
            surplus_score = max(0,surplus_ratio*40)
        else:
            surplus_score = 0  
        return min(emergency_score + surplus_score, 100)
    

    def _calculate_volatility_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate income volatility score"""
        income_history = financial_data.get('income_history', [])
        
        if len(income_history) < 3:
            return 50  # Default moderate volatility
        
        # Calculate coefficient of variation
        income_array = np.array(income_history)
        cv = np.std(income_array) / np.mean(income_array) if np.mean(income_array) > 0 else 0
        
        # Convert to score (higher volatility = higher score = higher risk tolerance needed)
        volatility_score = min(cv * 100, 100)
        
        return volatility_score
    
    def _calculate_liquidity_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate liquidity needs score"""
        monthly_expenses = financial_data.get('monthly_expenses', 0)
        liquid_assets = financial_data.get('liquid_assets', 0)
        dependents = financial_data.get('dependents', 0)
        
        # Base liquidity need (higher = more conservative)
        base_need = 30 + (dependents * 10)  # 30% base + 10% per dependent
        
        # Current liquidity ratio
        if monthly_expenses > 0:
            liquidity_ratio = liquid_assets / (monthly_expenses * 6)  # 6 months target
            current_liquidity = min(liquidity_ratio * 50, 50)
        else:
            current_liquidity = 25
        
        return base_need + (50 - current_liquidity)
    

    def _calculate_age_score(self, user_preferences: Dict[str, Any]) -> float:
        """Calculate age-based risk tolerance score"""
        age = user_preferences.get('age', 35) if user_preferences else 35
        
        # Younger = higher risk tolerance
        if age < 25:
            return 80
        elif age < 35:
            return 70
        elif age < 45:
            return 60
        elif age < 55:
            return 45
        elif age < 65:
            return 30
        else:
            return 15
    
    def _calculate_debt_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate debt impact score"""
        monthly_income = financial_data.get('monthly_income', 0)
        monthly_debt_payments = financial_data.get('monthly_debt_payments', 0)
        
        if monthly_income > 0:
            debt_ratio = monthly_debt_payments / monthly_income
            # Higher debt ratio = lower risk tolerance
            return max(0, 100 - (debt_ratio * 200))
        
        return 50
    

    def _calculate_time_horizon(self,user_preferences:Dict[str,Any])->int:
        """calculate investment time horizon in years"""
        age = user_preferences.get('age',35)
        investment_goal = user_preferences.get('investment_goal','retirement')
        if investment_goal == 'retirement':
            return max(1,65-age)
        elif investment_goal == 'short_term':
            return user_preferences.get('target_years',3)
        elif investment_goal == 'medium_term':
            return user_preferences.get('target_years',7)
        elif investment_goal =='long_term':
            return user_preferences.get('target_years',15)
        else:
            return max(1,min(30,65-age))
    

    def _get_risk_category(self,risk_score:float)->str:
        for(min_score,max_score), category in self.risk_categories.items():
            if min_score<=risk_score<= max_score:
                return category
            
        
        if risk_score >= 80:
            return "Very Agressive"
        
        else:
            return "Very Conservative"
        
    

    def generate_risk_report(self,risk_profile:RiskProfile,
                            financial_data:Dict[str,Any],
                            user_preferences:Dict[str,Any]=None)->Dict[str,Any]:
        """Generate a comphrensiove risk assessment report"""
        if user_preferences is None:
            user_preferences ={}

        report={
            'risk_profile': {
                'score': round(risk_profile.risk_score, 2),
                'category': risk_profile.risk_category,
                'volatility_tolerance': round(risk_profile.volatility_tolerance, 2),
                'time_horizon': risk_profile.time_horizon,
                'liquidity_needs': round(risk_profile.liquidity_needs, 2)
        },
        'recommendations': self._generate_recommendations(risk_profile),
            'asset_allocation': self._suggest_asset_allocation(risk_profile),
            'financial_metrics': {
                'stability_score': round(self._calculate_stability_score(financial_data), 2),
                'volatility_score': round(self._calculate_volatility_score(financial_data), 2),
                'liquidity_score': round(self._calculate_liquidity_score(financial_data), 2),
                'age_score': round(self._calculate_age_score(user_preferences), 2),
                'debt_score': round(self._calculate_debt_score(financial_data), 2)
            }
        }
        return report
    

    def _generate_recommendations(self,risk_profile:RiskProfile)->List[str]:
        """generate personalized recommendations based on risk profile"""
        recommendations =[]

        if risk_profile.risk_category == "Very Conservative":
            recommendations.extend([
                "Focus on capital preservation with high-grade bonds and CDs",
                "Consider Treasury securities for stability",
                "Maintain higher cash reserves for emergencies"
            ])
        elif risk_profile.risk_category == "Conservative":
            recommendations.extend([
                "Balanced approach with 20-30% "" stocks, 70-80% "" bonds",
                "Consider dividend-paying stocks for income",
                "Build emergency fund of 6-12 months expenses"
            ])
        elif risk_profile.risk_category == "Moderate":
            recommendations.extend([
                "Balanced portfolio with 40-60% "" stocks, 40-60%"" bonds",
                "Diversify across different sectors and asset classes",
                "Consider index funds for broad market exposure"
            ])
        elif risk_profile.risk_category == "Agressive":
            recommendations.extend([
                "Growth-focused portfolio with 70-80% "" stocks",
                "Consider small-cap and international stocks",
                "Regular portfolio rebalancing recommended"
            ])
        # very agressive
        else:
            recommendations.extend([
                "High-growth portfolio with 80-90%"" stocks",
                "Consider growth stocks and emerging markets",
                "Be prepared for significant volatility"
            ])
        
        return recommendations 
    


