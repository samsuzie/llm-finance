from typing import Dict,Any,List
import openai
from langchain.llms import openai
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from app.core.config import settings
from app.ml.investment_recommender import InvestmentRecommender
from app.ml.risk_assessor import RiskAssessor

class AIService:
    def __init__(self):
        self.llm = openai(api_key=settings.OPENAI_API_KEY)
        self.embeddings=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.vector_store = Chroma(embedding_function=self.embeddings)
        self.investment_recommender = InvestmentRecommender()
        self.risk_acessor = RiskAssessor()

    async def generate_financial_advice(
            self,
            user_query:str,
            user_context:Dict[str,Any],
            user:Any
    )->str:
        """Generate personalised financial advice using RAG"""

        # create prompt 
        prompt = self._create_advice_prompt(user_query,user_context,user)

        # generate response using LLM
        try :
            response = self.llm(prompt)
            return response
        except Exception as e:
            return f"I apologize, but I encountered an error while generating advice: {str(e)}"

    def _create_advice_prompt(
            self,
            user_query:str,
            user_context:Dict[str,Any],
            user:Any)->str:
        """create a elaborate and comphrensive prompt for financial advice"""
        context_summary=f"""
        User Financial Context:
        - Monthly Income:{user_context.get('monthly_income','Not provided')}
        - Monthly Expenses:{user_context.get('monthly_expenses','Not provided')}
        - Savings Rate :{user_context.get('savings_rate','Not provided')}%
        -Top Spending Categories:{', '.join(user_context.get('top_categories',[]))}
        -Risk Tolerance:{user.risk_tolerance if hasattr(user,'risk_tolerance')else 'Not assigned'}
        -Financial Goals:{', '.join(user.financial_goals if hasattr(user,'financial_goals')else [])}
        """

        prompt=f"""
        You are an expert personal finance advisor. Provide personalized, actionable financial advice based on the user's specific situation.
        {context_summary}

        User Question:{user_query}

        Instructions:
        1. Provide specific, actionable advice tailored to their situation
        2. Reference their spending patterns and financial data when relevant
        3. Consider their risk tolerance and goals
        4. Be encouraging but realistic
        5. Suggest concrete next steps they can take
        6. If discussing investments, emphasize the importance of diversification and risk management
        
        Response:
        """
        
        return prompt
    

    async def get_investment_recommendations(self,user:Any)->Dict[str,Any]:
        """Get personalized investment recommendation"""
        try:
            risk_profile = await self.risk_assessor.assess_risk(user)

            recommendations= await self.investment_recommender.recommend(
                user,risk_profile
            )

            return{
                "risk_profile":risk_profile,
                "recommendations":recommendations,
                "disclaimer": "This is not financial advice. Please consult with a qualified financial advisor before making investment decisions."
            }
        except Exception as e:
            return{
                "error": f"Unable to generate recommendations: {str(e)}",
                "disclaimer": "Please consult with a qualified financial advisor for investment advice."
            }
