<<<<<<< HEAD
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text, Boolean
=======
from sqlalchemy import Column,String,Float,Date,DateTime,Text,ForeignKey,Boolean
>>>>>>> 75f1347 (Updates)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

<<<<<<< HEAD
class FinancialGoal(Base):
    __tablename__ = "financial_goals"
    
=======

class FinancialGoal(Base):
    __table_name__ = "financial_goals"

>>>>>>> 75f1347 (Updates)
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Goal details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(Date, nullable=True)
    category = Column(String, nullable=True)  # emergency_fund, vacation, house, etc.
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
<<<<<<< HEAD
    user = relationship("User", back_populates="financial_goals_rel")
=======
    user = relationship("User", back_populates="financial_goals_rel")
    
>>>>>>> 75f1347 (Updates)
