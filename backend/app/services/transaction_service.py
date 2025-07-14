import pandas as pd
from typing import List,Dict,Any
from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.user import User
from app.utils.database import get_db
from app.ml.transaction_analyzer import TransactionAnalyzer



class TransactionService:
    def __init__(self):
        self.analyzer = TransactionAnalyzer()

    async def process_transactions(self,df:pd.DataFrame,user_ide:str)->List[Transaction]:
        """Process  and store transaction data"""
        processed_transactions=[]

        # clean and standardize data
        df = self._clean_transaction_data(df)
        df = await self.analyzer.categorize_transactions(df)

        with get_db() as db:
            for _,row in df.iterrows():
                transaction=Transaction(
                    user_id = user_id,
                    amount = row['amount'],
                    description = row['description'],
                    category = row['category'],
                    date = pd.to_datetime(row['date']).date(),
                    merchant=row.get('merchant', ''),
                    account_type=row.get('account_type', '')
                )
                db.add(transaction)
                processed_transactions.append(transaction)
            db.commit()
        return processed_transactions
    

    def _clean_transaction_data(self,df:pd.DataFrame)->pd.DataFrame:
        """clean and standardize transaction data"""

        df = df.drop_duplicates()
        column_mapping={
            'Amount':'amount',
            'Description':'description',
            'Date':'date',
            'Merchant':'merchant'
        }

        df = df.rename(columns=column_mapping)

        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'],errors='coerce')
        
        if 'data' in df.columns:
            df['data']= pd.to_datetime(df['date'],errors='coerce')

        df = df.dropna(subset=['amount','date'])

        return df
    
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
    