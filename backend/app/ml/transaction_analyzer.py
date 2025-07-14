import pandas as pd
import numpy as np
from typing import Dict,Any,List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import re
class TransactionAnalyzer:
    def __init__(self):
        self.category_keywords = {
            'food_dining': ['restaurant', 'food', 'dining', 'pizza', 'coffee', 'cafe', 'bar', 'pub'],
            'groceries': ['grocery', 'supermarket', 'market', 'walmart', 'costco', 'target'],
            'transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'metro', 'bus'],
            'utilities': ['electric', 'water', 'gas', 'internet', 'phone', 'utility'],
            'entertainment': ['movie', 'theater', 'netflix', 'spotify', 'game', 'entertainment'],
            'shopping': ['amazon', 'store', 'retail', 'shop', 'purchase'],
            'healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'health'],
            'education': ['school', 'university', 'education', 'tuition', 'books'],
            'insurance': ['insurance', 'premium', 'policy'],
            'investment': ['investment', 'stock', 'bond', 'mutual fund', '401k']
        }
    async def categorize_transactions(self,df:pd.DataFrame)->pd.DataFrame:
        """Categorize transactions based on desciption and merchant"""
        df['category']=df.apply(self._categorize_single_transaction,axis=1)
        return df
    def _categorize_single_transaction(self,row)->str:
        description = str(row.get('description',' ')).lower()
        merchant = str(row.get('merchant',' ')).lower()

        text = f"{description}{merchant}"

        for category,keywords in self.category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        return 'other'
    
    async def analyze_patterns(self,df:pd.DataFrame)->Dict[str,Any]:
        """analyze spendig patterns and providing insights"""
        analysis={}
        analysis['total_transactions']=len(df)
        analysis['total_amount']=df['amount'].sum()
        analysis['average_transaction']=df['amount'].mean()

        # category analysis
        category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        analysis['spending_by_category']=category_spending.to_dict()
        analysis['top_categories']=category_spending.head(5).index.to_list()


        # monthly trends
        df['month']=pd.to_datetime(df['date']).dt.to_period('M')
        monthly_spending = df.groupby('month')['amount'].sum()
        analysis['monthly_trends']=monthly_spending.to_dict()
        analysis['unusual_transactions']=self._identify_unusual_transactions(df)

        date_range = (df['date'].max()-df['date'].min()).days
        analysis['transactions_per_day']=len(df)/max(date_range,1)

        return analysis
    def _identify_unusual_transactions(self,df:pd.DataFrame)->List[Dict[str,Any]]:
        """identify transactions that are unusually large"""

        #calculating z-score for amounts
        mean_amount = df['amount'].mean()
        std_amount = df['amount'].std()

        unusual_transactions=[]
        for _,row in df.iterrows():
            z_score = abs((row['amount']-mean_amount)/std_amount) if std_amount>0 else 0
            if z_score>2:
                unusual_transactions.append({
                    'amount':row['amount'],
                    'description':row['description'],
                    'date':str(row[date]),
                    'z_score':z_score
                })
        return unusual_transactions[:10]
    