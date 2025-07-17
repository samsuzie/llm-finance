from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime
import uvicorn

from app.core.config import settings
from app.core.database import get_db, create_tables
from app.api.auth import get_current_user
from app.services.transaction_service import TransactionService
from app.services.ai_service import AIService
from app.api import transactions, analytics
from app.models.user import User
from app.models.transaction import Transaction

# Create tables on startup
create_tables()


app = FastAPI(
    title="Personal Finance Coach API",
    description="LLM-powered personal finance advisor",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    context: Optional[dict] = None

class TransactionUpload(BaseModel):
    transactions: List[dict]

class InvestmentQuery(BaseModel):
    risk_tolerance: str
    investment_horizon: str
    goals: List[str]

# Routes
@app.get("/")
async def root():
    return {"message": "Personal Finance Coach API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

