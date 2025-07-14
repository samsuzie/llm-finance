from typing import Dict,Any
import numpy as np
class RiskAssessor:
    def __init__(self):
        self.risk_factors={
            'age':{'weight':0.3,'ranges':[(18,30,0.8),(31,45,0.6), (46, 60, 0.4), (61, 100, 0.2)]},
            'income_stability':{'weight':0.2},
            'emergency_fund': {'weight': 0.2},
            'investment_experience': {'weight': 0.15},
            'time_horizon': {'weight': 0.15}
        }
    
    async def assess_risk(self,user:Any)->Dict[str,Any]:
        """assesing user risk tolerance and capapcity"""

        risk_score = self._calculate_risk_score(user)
        risk_level = self._determine_risk_level(risk_score)

        return {
            'risk_score':risk_score,
            'risk_level':risk_level,
            'risk_capacity':self._assess_risk_capacity(user),
            'recommendations':self._get_risk_recommendations(risk_level)
        }
    def _calculate_risk_score(self,user:Any)->float:
        """calculate overall risk score"""
        base_score=0.5  #medium risk as default
        #adjust based on user attributes if available
        if hasattr(user,'age'):
            if user.age<35:
                base_score += 0.2
            elif user.age>55:
                base_score -= 0.2

        if hasattr(user,'income') and user.income>100000:
            base_score += 0.1
        
        return max(0.1,min(0.9,base_score))
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level category"""
        if risk_score < 0.4:
            return 'conservative'
        elif risk_score < 0.7:
            return 'moderate'
        else:
            return 'aggressive'

    def _assess_risk_capacity(self,user:Any)->Dict[str,Any]:
        """Assess user's capacity to take risk"""
        return {
            'emergency_fund_months': 6,  # Example data
            'debt_to_income_ratio': 0.3,
            'investment_timeline': '10+ years'
        }
    
    def _get_risk_recommendations(self, risk_level: str) -> List[str]:
        """Get recommendations based on risk level"""
        recommendations = {
            'conservative': [
                "Focus on capital preservation",
                "Consider high-grade bonds and CDs",
                "Limit stock exposure to 30-40%",
                "Maintain larger emergency fund"
            ],
            'moderate': [
                "Balanced portfolio of stocks and bonds",
                "Consider target-date funds",
                "Regular rebalancing is important",
                "Dollar-cost averaging for stock investments"
            ],
            'aggressive': [
                "Higher allocation to growth stocks",
                "Consider international diversification",
                "Accept short-term volatility for long-term gains",
                "Regular monitoring and rebalancing"
            ]
        }
        
        return recommendations.get(risk_level, recommendations['moderate'])
