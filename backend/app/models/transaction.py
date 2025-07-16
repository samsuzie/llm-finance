from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Numeric(12, 2), nullable=False)  # Supports up to 999,999,999.99
    description = Column(Text, nullable=False)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    
    # Transaction metadata
    merchant = Column(String(255))
    account_type = Column(String(50))  # checking, savings, credit, etc.
    transaction_type = Column(String(20), default="expense")  # income, expense, transfer
    
    # Date information
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    posted_date = Column(DateTime(timezone=True))
    
    # Additional fields
    reference_number = Column(String(100))
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    
    # AI/ML fields
    confidence_score = Column(Numeric(3, 2))  # Confidence in categorization (0.00-1.00)
    is_recurring = Column(String(10), default="no")  # yes, no, maybe
    is_anomaly = Column(String(10), default="no")  # Flagged as unusual spending
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
        Index('idx_user_category', 'user_id', 'category'),
        Index('idx_user_amount', 'user_id', 'amount'),
        Index('idx_date_category', 'date', 'category'),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, description={self.description[:30]}...)>"
    
    @property
    def is_income(self):
        return float(self.amount) > 0
    
    @property
    def is_expense(self):
        return float(self.amount) < 0
    
    @property
    def absolute_amount(self):
        return abs(float(self.amount))
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "amount": float(self.amount),
            "description": self.description,
            "category": self.category,
            "subcategory": self.subcategory,
            "merchant": self.merchant,
            "account_type": self.account_type,
            "transaction_type": self.transaction_type,
            "date": self.date.isoformat() if self.date else None,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "reference_number": self.reference_number,
            "notes": self.notes,
            "tags": self.tags.split(",") if self.tags else [],
            "confidence_score": float(self.confidence_score) if self.confidence_score else None,
            "is_recurring": self.is_recurring,
            "is_anomaly": self.is_anomaly,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_categories(cls):
        """Common transaction categories"""
        return [
            "Food & Dining",
            "Groceries", 
            "Transportation",
            "Gas & Fuel",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Education",
            "Travel",
            "Insurance",
            "Investment",
            "Income",
            "Transfer",
            "Other"
        ]