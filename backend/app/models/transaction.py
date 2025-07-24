<<<<<<< HEAD
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text, Index
=======
from sqlalchemy import Column,String,Float,Date,DateTime,ForeignKey,Text,Index
>>>>>>> 75f1347 (Updates)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
<<<<<<< HEAD
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    merchant = Column(String, nullable=True)
    account_type = Column(String, nullable=True)
    
    # Dates
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
        Index('idx_user_category', 'user_id', 'category'),
        Index('idx_date_amount', 'date', 'amount'),
=======
    id = Column(String,primary_key=True,index=True)
    user_id = Column(String,ForeignKey("users.id"),nullable=False)
    
    amount = Column(Float,nullable=False)
    description = Column(Text,nullable=False)
    category = Column(String,nullable=True)
    merchant = Column(String,nullable=True)
    account_type = Column(String,nullable=True)


    #Dates
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    user = relationship("User",back_populates="transactions")
    # Indexing for better query performance
    __table_args__=(
        Index('idx_user_date','user_id','date'),
        Index('idx_user_category','user_id','category'),
        Index('idx_date_amount','date','amount')
>>>>>>> 75f1347 (Updates)
    )