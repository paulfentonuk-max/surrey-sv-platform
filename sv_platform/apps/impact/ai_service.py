import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class VeniceAIService:
    def __init__(self):
        self.api_key = os.getenv('VENICE_API_KEY')
        self.base_url = "https://api.venice.ai/api/v1"
        self.model = "default"
        
        if self.api_key:
            print(f"API Key loaded successfully")
        else:
            print("WARNING: No API key found!")
    
    def chat(self, messages: List[Dict[str, str]], 
             system_prompt: Optional[str] = None,
             temperature: float = 0.7) -> str:
        
        if not self.api_key:
            return "Error: API key not configured."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        conversation = []
        if system_prompt:
            conversation.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            conversation.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        payload = {
            "model": self.model,
            "messages": conversation,
            "temperature": temperature,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Venice AI Error: {e}")
            return "I'm having trouble connecting right now. Please try again."
    
    def chat_with_proxies(self, message: str, history: List[Dict]) -> Dict:
        """
        Smart chat that searches proxies and includes them in context
        """
        from .models import FinancialProxy
        from django.db.models import Q
        
        # Extract keywords from message
        keywords = message.lower().split()
        search_terms = [word for word in keywords if len(word) > 3]
        
        # Search for relevant proxies
        proxies = []
        if search_terms:
            query = Q()
            for term in search_terms:
                query |= Q(outcome_name__icontains=term) | Q(category__icontains=term)
            proxies = list(FinancialProxy.objects.filter(query).values(
                'id', 'category', 'outcome_name', 'unit_of_measure', 'financial_value_gbp'
            )[:5])
        
        # Build system prompt with proxy data
        system_prompt = """You are a Social Value AI Companion with access to the Surrey Social Value Framework database.
        
You help users:
- Understand social value and SROI
- Find relevant proxy measures for their projects
- Calculate potential social impact
- Design effective interventions

When relevant proxies are available, reference them specifically with their values."""
        
        # Get AI response with proxy context
        response_text = self.chat(
            messages=history + [{"role": "user", "content": message}],
            system_prompt=system_prompt
        )
        
        return {
            'response': response_text,
            'proxies_used': proxies,
            'proxies_count': len(proxies)
        }

ai_service = VeniceAIService()
