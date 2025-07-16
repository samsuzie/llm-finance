from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from ..core.database import Base


class FinancialGoal(Base):
    __tablename__ = "financial_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # savings, debt_payoff, investment, etc.
    
    # Financial targets
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), default=0)
    monthly_contribution = Column(Numeric(10, 2))
    
    # Timeline
    target_date = Column(DateTime(timezone=True))
    start_date = Column(DateTime(timezone=True), default=func.now())
    
    # Goal settings
    priority = Column(String(10), default="medium")  # low, medium, high
    is_active = Column(Boolean, default=True)
    auto_contribute = Column(Boolean, default=False)
    
    # Progress tracking
    milestones = Column(JSONB, default=list)  # Array of milestone objects
    progress_history = Column(JSONB, default=list)  # Historical progress data
    
    # AI recommendations
    recommended_monthly_amount = Column(Numeric(10, 2))
    difficulty_score = Column(Numeric(3, 2))  # 0.00-1.00 (easy to hard)
    success_probability = Column(Numeric(3, 2))  # 0.00-1.00
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="financial_goals")
    
    def __repr__(self):
        return f"<FinancialGoal(id={self.id}, title={self.title}, target_amount={self.target_amount})>"
    
    @property
    def progress_percentage(self):
        if self.target_amount and self.target_amount > 0:
            return min((float(self.current_amount) / float(self.target_amount)) * 100, 100)
        return 0
    
    @property
    def remaining_amount(self):
        return max(float(self.target_amount) - float(self.current_amount), 0)
    
    @property
    def is_completed(self):
        return self.current_amount >= self.target_amount
    
    @property
    def days_remaining(self):
        if self.target_date:
            delta = self.target_date - datetime.now(self.target_date.tzinfo)
            return max(delta.days, 0)
        return None
    
    @property
    def months_remaining(self):
        days = self.days_remaining
        return round(days / 30.44) if days is not None else None  # Average days per month
    
    def calculate_required_monthly_contribution(self):
        """Calculate monthly contribution needed to reach goal by target date"""
        if not self.target_date or self.is_completed:
            return 0
        
        months_left = self.months_remaining
        if not months_left or months_left <= 0:
            return self.remaining_amount
        
        return self.remaining_amount / months_left
    
    def add_progress_entry(self, amount, note=None):
        """Add a progress entry to the goal"""
        entry = {
            "date": datetime.now().isoformat(),
            "amount": float(amount),
            "total_after": float(self.current_amount) + float(amount),
            "note": note
        }
        
        if self.progress_history is None:
            self.progress_history = []
        
        self.progress_history.append(entry)
        self.current_amount = (self.current_amount or 0) + amount
        
        # Check if goal is completed
        if self.current_amount >= self.target_amount and not self.completed_at:
            self.completed_at = func.now()
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "target_amount": float(self.target_amount),
            "current_amount": float(self.current_amount or 0),
            "monthly_contribution": float(self.monthly_contribution) if self.monthly_contribution else None,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "priority": self.priority,
            "is_active": self.is_active,
            "auto_contribute": self.auto_contribute,
            "progress_percentage": self.progress_percentage,
            "remaining_amount": self.remaining_amount,
            "is_completed": self.is_completed,
            "days_remaining": self.days_remaining,
            "months_remaining": self.months_remaining,
            "required_monthly_contribution": self.calculate_required_monthly_contribution(),
            "recommended_monthly_amount": float(self.recommended_monthly_amount) if self.recommended_monthly_amount else None,
            "difficulty_score": float(self.difficulty_score) if self.difficulty_score else None,
            "success_probability": float(self.success_probability) if self.success_probability else None,
            "milestones": self.milestones or [],
            "progress_history": self.progress_history or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def get_categories(cls):
        """Common financial goal categories"""
        return [
            "Emergency Fund",
            "Retirement",
            "House Down Payment",
            "Vacation",
            "Car Purchase",
            "Debt Payoff",
            "Education",
            "Investment",
            "Wedding",
            "Other"
        ]