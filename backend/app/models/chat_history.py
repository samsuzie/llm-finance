from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Message details
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    message_type = Column(String, default="general")  # general, investment, budgeting, etc.
    
    # Context and metadata
    context_data = Column(Text, nullable=True)  # JSON string of context used
    recommendations = Column(Text, nullable=True)  # JSON string of recommendations
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")