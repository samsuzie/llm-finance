import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from ..models.transaction import Transaction
from ..models.user import User
from ..ml.transaction_analyzer import TransactionAnalyzer
import uuid



class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = TransactionAnalyzer()

    def bulk_create_transactions(self, df: pd.DataFrame, user_id: str = None) -> Dict[str, int]:
        """Bulk create transactions from DataFrame"""
        processed_transactions = []
        skipped_count = 0

        # Clean and categorize data
        df = self._clean_transaction_data(df)
        df = self.analyzer.categorize_transactions(df)

        for _, row in df.iterrows():
            # Check for duplicates
            existing = self.db.query(Transaction).filter(
                and_(
                    Transaction.amount == row['amount'],
                    Transaction.description == row['description'],
                    Transaction.date == pd.to_datetime(row['date']).date()
                )
            ).first()
            
            if existing:
                skipped_count += 1
                continue
                
            transaction = Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id or "default_user",
                amount=float(row['amount']),
                description=str(row['description']),
                category=row.get('category', 'Other'),
                date=pd.to_datetime(row['date']).date(),
                merchant=row.get('merchant', ''),
                account_type=row.get('account_type', '')
            )
            self.db.add(transaction)
            processed_transactions.append(transaction)
        
        self.db.commit()
        return {
            "created": len(processed_transactions),
            "skipped": skipped_count
        }
    

    def get_filtered_transactions(
        self, 
        skip: int = 0, 
        limit: int = 100,
        category: str = None,
        start_date: str = None,
        end_date: str = None,
        user_id: str = None
    ) -> List[Transaction]:
        """Get filtered transactions"""
        query = self.db.query(Transaction)
        
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        
        if category:
            query = query.filter(Transaction.category == category)
            
        if start_date:
            query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
            
        if end_date:
            query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        return query.offset(skip).limit(limit).all()

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = self.db.query(Transaction.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]

    def get_summary(self, period: str = "30d", user_id: str = None) -> Dict[str, Any]:
        """Get transaction summary for a period"""
        end_date = datetime.now().date()
        start_date = self._get_start_date_from_period(period, end_date)
        
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        )
        
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        
        transactions = query.all()
        
        if not transactions:
            return {
                "total_transactions": 0,
                "total_income": 0,
                "total_expenses": 0,
                "net_amount": 0,
                "categories": {}
            }
        
        df = pd.DataFrame([{
            'amount': t.amount,
            'category': t.category or 'Other'
        } for t in transactions])
        
        income = df[df['amount'] > 0]['amount'].sum()
        expenses = abs(df[df['amount'] < 0]['amount'].sum())
        
        return {
            "total_transactions": len(transactions),
            "total_income": float(income),
            "total_expenses": float(expenses),
            "net_amount": float(income - expenses),
            "categories": df.groupby('category')['amount'].sum().to_dict()
        }

    def _clean_transaction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """clean and standardize transaction data"""
        df = df.drop_duplicates()
        
        column_mapping = {
            'Amount': 'amount',
            'Description': 'description', 
            'Date': 'date',
            'Merchant': 'merchant'
        }
        df = df.rename(columns=column_mapping)
        
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
        df = df.dropna(subset=['amount', 'date'])
        return df

    def _get_start_date_from_period(self, period: str, end_date) -> datetime.date:
        """Convert period string to start date"""
        if period == "7d":
            return end_date - timedelta(days=7)
        elif period == "30d":
            return end_date - timedelta(days=30)
        elif period == "90d":
            return end_date - timedelta(days=90)
        elif period == "1y":
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)
    
    async def analyze_spending_patterns(self,user_id:str,period:str)->Dict[str,Any]:
        """Analyze user spending patterns"""

        transactions = self._get_user_transactions(user_id,period)

        if not  transactions:
            return{"message":"no transactions found for analysis"}
        
        df = pd.DataFrame([{
            'amount':t.amount,
            'category':t.category,
            'date':t.date,
            'desccription':t.description
        }for t in transactions])

        # perform analysis
        analysis = await self.analyzer.analyze_patterns(df)
        return analysis
    


    def _get_user_transactions(self,user_id:str,period:str)->List[Transaction]:
        """Get user trasactions for a specific period"""

        end_date= datetime.now().date()
        if period == "1m":
            start_date = end_date-timedelta(days=30)

        elif period=="3m":
            start_date = end_date-timedelta(days=90)

        elif period=="6m":
            start_date = end_date - timedelta(days=180)
        
        elif period=="1y":
            start_date = end_date - timedelta(days=365)

        else:
            start_date = end_date - timedelta(days=180)  #defaulting to 6 months

        with get_db() as db:
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.date>= start_date,
                Transaction.date<=end_date
            ).all()
        return transactions
    