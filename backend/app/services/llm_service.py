import openai
from typing import List, Dict, Any
import json
from ..core.config import settings
from ..utils.prompts import FinancialCoachPrompts

class LLMService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.prompts = FinancialCoachPrompts()
    
    async def generate_response(
        self,
        message: str,
        context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate AI response for financial coaching"""
        
        # Build conversation context
        messages = [
            {"role": "system", "content": self.prompts.get_system_prompt()},
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                if msg.get('type') == 'user':
                    messages.append({"role": "user", "content": msg.get('content', '')})
                elif msg.get('type') == 'bot':
                    messages.append({"role": "assistant", "content": msg.get('content', '')})
        
        # Add current message with context
        user_message = self.prompts.format_user_message(message, context)
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Generate response
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                functions=[
                    {
                        "name": "provide_financial_advice",
                        "description": "Provide structured financial advice with recommendations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "response": {
                                    "type": "string",
                                    "description": "Main response to the user"
                                },
                                "recommendations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of actionable recommendations"
                                },
                                "follow_up_questions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Suggested follow-up questions"
                                }
                            },
                            "required": ["response"]
                        }
                    }
                ],
                function_call="auto"
            )
            
            # Parse response
            if response.choices[0].message.function_call:
                function_response = json.loads(response.choices[0].message.function_call.arguments)
                return function_response
            else:
                return {
                    "response": response.choices[0].message.content,
                    "recommendations": [],
                    "follow_up_questions": []
                }
                
        except Exception as e:
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "recommendations": [],
                "follow_up_questions": []
            }
