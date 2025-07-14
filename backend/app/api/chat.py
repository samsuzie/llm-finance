from fastapi import APIRouter,Depends,HTTPException
from typing import List,Dict,Any,Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..core.databse  import get_db
from ..services.llm_service import LLMService
from ..services.rag_Service import RAGService


router = APIRouter()

class ChatMessage(BaseModel):
    message:str
    conversation_history:Optional[List[Dict[str,Any]]]=[]



class ChatResponse(BaseModel):
    response:str
    recommendations:Optional[List[str]]=[]
    charts:Optional[Dict[str,Any]]=None
    follow_up_questions:Optional[List[str]]=[]
    
