from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import io
from ..core.database import get_db
from ..services.transaction_service import TransactionService
from ..services.file_processor import FileProcessor


router = APIRouter()
@router.post("/upload")
async def upload_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process transaction file"""
    try:
        if not file.filename.endswith(('.csv', '.xlsx', '.json')):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload CSV, XLSX or JSON files."
            )
            
        content = await file.read()
        
        # Process file based on type
        processor = FileProcessor()
        if file.filename.endswith('.csv'):
            df = processor.process_csv(io.StringIO(content.decode('utf-8')))
        elif file.filename.endswith('.xlsx'):
            df = processor.process_excel(io.BytesIO(content))
        elif file.filename.endswith('.json'):
            df = processor.process_json(io.StringIO(content.decode('utf-8')))
        
        transaction_service = TransactionService(db)
        result = transaction_service.bulk_create_transactions(df)
        
        return {
            "message": "Transactions uploaded successfully",
            "total_transactions": len(df),
            "processed_transactions": result["created"],
            "skipped_duplicates": result["skipped"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/")
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """get filtered transactions"""
    service = TransactionService(db)
    transactions = service.get_filtered_transactions(
        skip=skip,
        limit=limit,
        category=category,
        start_date=start_date,
        end_date=end_date
    )
    return transactions

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories of transactions"""
    service = TransactionService(db)
    return service.get_categories()

@router.get("/summary")
async def get_transaction_summary(
    period: str = "30d",
    db: Session = Depends(get_db)
):
    """Get transaction summary for a period"""
    service = TransactionService(db)
    return service.get_summary(period)