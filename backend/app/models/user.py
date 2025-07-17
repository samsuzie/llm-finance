from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Profile information
    age = Column(Integer, nullable=True)
    income = Column(Integer, nullable=True)
    risk_tolerance = Column(String, nullable=True)  # conservative, moderate, aggressive
    financial_goals = Column(Text, nullable=True)  # JSON string of goals
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    financial_goals_rel = relationship("FinancialGoal", back_populates="user")