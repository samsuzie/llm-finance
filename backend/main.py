from fastapi import FastAPI,HTTPException,Depends,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime
import uvicorn

from app.core.config import settings
from app.api.auth import get_current_user
from app.services.transaction_service import TransactionService
from app.services.ai_service import AIService
from app.models.user import User
from app.models.transaction import Transaction



app = FastAPI(
    title="Personal Finance Coach API",
    description="LLM-powered personal finance advisor",
    version="1.0.0"
)

# middleware - asking the backend to be flexible a little bit only with the specified localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
transaction_service = transaction_service()
ai_service=AIService()


# Pydantic models
class ChatMessage(BaseModel):
    message :str
    context :Optional[dict]=None


class TransactionUpload(BaseModel):
    transactions:List[dict]

class InvestmentQuery(BaseModel):
    risk_tolerance:str
    investment_horizon:str
    goals:List[str]

# Routes
@app.get("/")
async def root():
    return {"message":"Personal Finance Coach API"}


@app.post("/api/transactions/upload")
async def upload_transactions(
    file:UploadFile=File(...),
    current_user:User = Depends(get_current_user)
):
    """Uploads and process transaction data
    """
    try:
        contents=await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        processed_transactions= await transaction_service.process_transactions(
            df, current_user.id
        )
        return{
            "status":"sucess",
            "processed_count":len(processed_transactions),
            "message": "Transactions uploaded and processed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    
@app.get("/api/analysis/spending-patterns")
async def get_spending_patterns(
    period: str="6m",
    current_user :User = Depends(get_current_user)
):
    """spending pattern analysis"""
    try:
        patterns = await transaction_service.analyze_spending_patterns(
            current_user.id,period
        )
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    


@app.post("/api/chat/message")
async def chat_message(
    message:ChatMessage,
    current_user :User = Depends(get_current_user)
):
    try:
        user_context = await transaction_service.get_user_financial_context(
            current_user.id
        )

        respose = await ai_service.generate_financial_advice(
            message.message,
            user_context,
            current_user
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.get("/api/recommendatioons/investments")
async def get_investment_recommendations(
    current_user :User = Depends(get_current_user)
):
    try:
        recommendations = await ai_service.get_investment_recommendations(
            current_user
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@app.post("/api/goals/create")
async def create_financial_goal(
    goal_data :dict,
    current_user : User=Depends(get_current_user)):
    try:
        goal = await transaction_service.create_financial_goal(
            goal_data,
            current_user.id
        )
        return goal
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.get("/api/dashboard/summary")
async def get_dashboard_summary(
    current_user:User=Depends(get_current_user)
):
    try:
        summary= await transaction_service.get_dashboard_summary(current_user.id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    


if __name__ =="__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)

