from fastapi import APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from typing import Dict,Any
from ..core.database import get_db
from ..services.analytics_service import AnalyticsService


router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    period:str="30d",
    db:Session=Depends(get_db)
):
    """Get dashboard analytics data"""
    try:
        service = AnalyticsService(db)
        return service.get_dashboard_data(period)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@router.get("/spending-trends")
async def get_spending_trends(
    period:str="90d",
    category:str=None,
    db:Session=Depends(get_db)
):
    service = AnalyticsService(db)
    return service.get_spending_trends(period,category)

@router.get("/predictions")
async def get_financial_predictions(
    horizon:int=30,
    db:Session=Depends(get_db)
):
    service = AnalyticsService(db)
    return service.get_predictions(horizon)
    
@router.get("/insights")
async def get_financial_insights(db:Session=Depends(get_db)):
    service = AnalyticsService(db)
    return service.get_insights()