from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..models.transaction import Transaction
import pandas as pd

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_data(self, period: str = "30d") -> Dict[str, Any]:
        """Get comprehensive dashboard analytics data"""
        end_date = datetime.now().date()
        start_date = self._get_start_date(period, end_date)
        
        # Get transactions for the period
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).all()
        
        if not transactions:
            return self._empty_dashboard_data()
        
        df = pd.DataFrame([{
            'amount': float(t.amount),
            'category': t.category or 'Other',
            'date': t.date,
            'description': t.description
        } for t in transactions])
        
        # Calculate key metrics
        total_income = df[df['amount'] > 0]['amount'].sum()
        total_expenses = abs(df[df['amount'] < 0]['amount'].sum())
        net_income = total_income - total_expenses
        
        # Monthly calculations (approximate)
        days_in_period = (end_date - start_date).days
        monthly_multiplier = 30 / days_in_period if days_in_period > 0 else 1
        
        monthly_income = total_income * monthly_multiplier
        monthly_expenses = total_expenses * monthly_multiplier
        savings_rate = (net_income / total_income * 100) if total_income > 0 else 0
        
        # Spending trend (daily aggregation)
        daily_spending = df[df['amount'] < 0].groupby('date')['amount'].sum().abs()
        spending_trend = [
            {'date': str(date), 'amount': float(amount)}
            for date, amount in daily_spending.items()
        ]
        
        # Category breakdown (expenses only)
        expense_categories = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()
        category_breakdown = [
            {'name': category, 'value': float(amount)}
            for category, amount in expense_categories.items()
        ]
        
        return {
            'totalBalance': float(net_income),
            'monthlyIncome': float(monthly_income),
            'monthlyExpenses': float(monthly_expenses),
            'savingsRate': float(savings_rate),
            'spendingTrend': spending_trend,
            'categoryBreakdown': category_breakdown,
            'totalTransactions': len(transactions),
            'period': period
        }

    def get_spending_trends(self, period: str = "90d", category: str = None) -> Dict[str, Any]:
        """Get detailed spending trends analysis"""
        end_date = datetime.now().date()
        start_date = self._get_start_date(period, end_date)
        
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.amount < 0  # Only expenses
            )
        )
        
        if category:
            query = query.filter(Transaction.category == category)
        
        transactions = query.all()
        
        if not transactions:
            return {'trends': [], 'summary': {}}
        
        df = pd.DataFrame([{
            'amount': abs(float(t.amount)),
            'category': t.category or 'Other',
            'date': t.date
        } for t in transactions])
        
        # Weekly trends
        df['week'] = pd.to_datetime(df['date']).dt.to_period('W')
        weekly_trends = df.groupby('week')['amount'].sum()
        
        trends = [
            {'period': str(week), 'amount': float(amount)}
            for week, amount in weekly_trends.items()
        ]
        
        # Summary statistics
        summary = {
            'total_spent': float(df['amount'].sum()),
            'average_weekly': float(weekly_trends.mean()),
            'highest_week': float(weekly_trends.max()),
            'lowest_week': float(weekly_trends.min()),
            'trend_direction': self._calculate_trend_direction(weekly_trends)
        }
        
        return {'trends': trends, 'summary': summary}

    def get_predictions(self, horizon: int = 30) -> Dict[str, Any]:
        """Get financial predictions (simplified version)"""
        # Get last 90 days of data for prediction base
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).all()
        
        if not transactions:
            return {'predictions': [], 'confidence': 0}
        
        df = pd.DataFrame([{
            'amount': float(t.amount),
            'date': t.date
        } for t in transactions])
        
        # Simple moving average prediction
        daily_spending = df[df['amount'] < 0].groupby('date')['amount'].sum().abs()
        avg_daily_spending = daily_spending.mean()
        
        # Generate predictions for next 'horizon' days
        predictions = []
        for i in range(horizon):
            future_date = end_date + timedelta(days=i+1)
            predicted_amount = float(avg_daily_spending)
            predictions.append({
                'date': str(future_date),
                'predicted_spending': predicted_amount,
                'confidence': 0.7  # Static confidence for now
            })
        
        return {
            'predictions': predictions,
            'total_predicted_spending': float(avg_daily_spending * horizon),
            'confidence': 0.7,
            'method': 'moving_average'
        }

    def get_insights(self) -> Dict[str, Any]:
        """Get financial insights and recommendations"""
        # Get last 30 days of data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).all()
        
        if not transactions:
            return {'insights': [], 'recommendations': []}
        
        df = pd.DataFrame([{
            'amount': float(t.amount),
            'category': t.category or 'Other',
            'date': t.date
        } for t in transactions])
        
        insights = []
        recommendations = []
        
        # Spending insights
        expenses = df[df['amount'] < 0]
        if not expenses.empty:
            top_category = expenses.groupby('category')['amount'].sum().abs().idxmax()
            top_amount = expenses.groupby('category')['amount'].sum().abs().max()
            
            insights.append(f"Your highest spending category is {top_category} with ${top_amount:.2f}")
            
            if top_amount > 500:
                recommendations.append(f"Consider reviewing your {top_category} expenses for potential savings")
        
        # Income insights
        income = df[df['amount'] > 0]
        if not income.empty:
            total_income = income['amount'].sum()
            total_expenses = abs(expenses['amount'].sum())
            savings_rate = (total_income - total_expenses) / total_income * 100
            
            insights.append(f"Your current savings rate is {savings_rate:.1f}%")
            
            if savings_rate < 20:
                recommendations.append("Try to increase your savings rate to at least 20%")
            elif savings_rate > 30:
                recommendations.append("Great job! You're saving more than 30% of your income")
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'period': '30 days'
        }

    def _get_start_date(self, period: str, end_date) -> datetime.date:
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

    def _empty_dashboard_data(self) -> Dict[str, Any]:
        """Return empty dashboard data structure"""
        return {
            'totalBalance': 0,
            'monthlyIncome': 0,
            'monthlyExpenses': 0,
            'savingsRate': 0,
            'spendingTrend': [],
            'categoryBreakdown': [],
            'totalTransactions': 0
        }

    def _calculate_trend_direction(self, series) -> str:
        """Calculate if trend is increasing, decreasing, or stable"""
        if len(series) < 2:
            return 'stable'
        
        first_half = series[:len(series)//2].mean()
        second_half = series[len(series)//2:].mean()
        
        if second_half > first_half * 1.1:
            return 'increasing'
        elif second_half < first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'