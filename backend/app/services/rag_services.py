import chromadb
from typing import Dict,List,Any
import pandas as pd
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..core.config import settings

class RAGService:
    def __init__(self,db,Session):
        self.db=db
        # Persisten Client tells chromadb to store the vector data persistently on disk not just in memory 
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        # creates or acess a chroma appication named financial data
        # a collection in chroma is a table -it stores a set of documents +their vector embeddings
        self.collection = self.client.get_or_create_collection("financial_data")

    def get_relevant_context(self,query:str)->Dict[str,Any]:
        """getting relevant financial context for relevant info"""
        # querying the database for relevant info
        results= self.collection.query(
            query_texts=[query],
            n_results=5
        )
        # recent transaction history
        recent_transactions = self._get_recent_transaction_summary()
        # spending patternsa
        spending_patterns = self._get_spending_patterns()

        financial_metrics=self._get_financial_metrics()
        # by doing the below thing we are collecting all the required context in one
        # place in form of key-value pair such that we can feed it into any llm such that 
        # we can provide all the rquired context to our llm
        return {
            "recent_transactions":recent_transactions,
            "spending_patterns":spending_patterns,
            "financial_metrics":financial_metrics,
            "relevant_documents":results.get()
        }
    
    def _get_recent_transaction_summary(self)->Dict[str,Any]:
        """Get summary of recent transactions"""

        #Get last 30 days of transactions
        transactions = self.db.query(Transaction).limit(100).all()
        if not transactions:
            return{"message":"No transaction data available"}
        
        df = pd.DataFrame([{
            "amount":t.amount,
            "category":t.category,
            "desccription":t.description,
            "date":t.date
        }for t in transactions])
        return {
            "total_transactions": len(df),
            "total_spent": df[df["amount"] < 0]["amount"].sum(),
            "total_income": df[df["amount"] > 0]["amount"].sum(),
            "top_categories": df.groupby("category")["amount"].sum().to_dict(),
            "average_transaction": df["amount"].mean()
        }
    
    def _get_spending_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns"""
        transactions = self.db.query(Transaction).filter(Transaction.amount < 0).limit(200).all()
        
        if not transactions:
            return {"message": "No spending data available"}
        
        df = pd.DataFrame([{
            "amount": abs(t.amount),
            "category": t.category,
            "date": t.date
        } for t in transactions])
        
        # Group by category
        category_spending = df.groupby("category")["amount"].agg(['sum', 'mean', 'count']).to_dict()
        
        return {
            "category_analysis": category_spending,
            "highest_spending_category": df.groupby("category")["amount"].sum().idxmax(),
            "most_frequent_category": df["category"].mode().iloc[0] if not df["category"].mode().empty else None
        }
    
    def _get_financial_metrics(self) -> Dict[str, Any]:
        """Calculate key financial metrics"""
        # This would integrate with your analytics service
        return {
            "monthly_burn_rate": 0,  # Calculate from transactions
            "savings_rate": 0,       # Calculate from income vs expenses
            "debt_to_income": 0,     # If debt data is available
            "emergency_fund_ratio": 0 # If savings data is available
        }
