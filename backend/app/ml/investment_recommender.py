import numpy as np
from typing import Dict,Any,List
import yfinance as yf
from datetime import datetime,timedelta

class InvestmentRecommender:
    def __init__(self):
        self.risk_allocations={
            'conservative':{'stocks':0.3,'bonds':0.6,'cash':0.1},
            'moderate':{'stocks':0.6,'bondsd':0.3,'cash':0.1},
            'aggresive':{'stocks':0.8,'bonds':0.15,'cash':0.05}
        }

        self.recommended_etfs={
            'stocks':['VIT','VXUS','VTV','VUG'],
            'bonds':['BND','VGIT','VTEB'],
            'cash':['VOMT','SHY']
        }

    async def recommend(self,user:Any,risk_profile:Dict[str,Any])->Dict[str,Any]:
        """generate investment recommendations based on user profile"""
        risk_level = risk_profile.get('risk_level','moderate')

        allocation = self.risk_allocations.get(risk_level,self.risk_allocations['moderate'])


        recommendations={
            'allocation':allocation,
            'suggested_etfs':self._get_etf_recommendations(allocation),
            'rebalancing_schedule':'Quarterly',
            'investment_strategy':self._get_investment_strategy(risk_level),
            'next_steps':self._get_next_steps(user,risk_level)
        }
        return recommendations
    
    def _get_etf_recommendations(self,allocation:Dict[str,float])->Dict[str,List[str]]:
        """get specific etf reccomendations based on allocation"""
        recommendations={}

        for asset_class,percentage in allocation.items():
            if percentage>0:
                recommendations[asset_class]={
                    'percentage':percentage*100,
                    'etfs':self.recommended_etfs.get(asset_class,[])
                }

    
    def _get_investment_strategy(self,risk_level:str)->str:
        """get investment strategy description"""
        strategies={
            'conservative': "Focus on capital preservation with steady, modest growth. Emphasize bonds and dividend-paying stocks.",
            'moderate': "Balanced approach seeking growth while managing risk. Mix of stocks and bonds with regular rebalancing.",
            'aggressive': "Growth-focused strategy accepting higher volatility for potentially higher returns. Stock-heavy portfolio."
        }
        return strategies.get(risk_level,strategies['moderate'])
    

    def _get_next_steps(self,user:Any,risk_level:str)->List[str]:
        """recommended next steps for the user"""
        steps = [
            "Open a brokerage account if you don't have one",
            "Start with low-cost index funds or ETFs",
            "Set up automatic monthly investments",
            "Review and rebalance quarterly"
        ]
        if risk_level == 'conservative':
            steps.append("Consider Treasury I-bonds for inflation protection")
        elif risk_level == 'aggressive':
            steps.append("Consider adding small-cap and international exposure")
        
        return steps
        