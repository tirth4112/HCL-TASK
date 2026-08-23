import json
from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL

class GroqLLMProvider:
    def __init__(self, api_key=GROQ_API_KEY, model=GROQ_MODEL):
        if not api_key:
            # We will use mock mode if no api key is present to allow testing without it
            self.mock_mode = True
        else:
            self.mock_mode = False
            self.client = Groq(api_key=api_key)
        self.model = model

    def invoke(self, prompt: str, system_prompt: str = None) -> str:
        if self.mock_mode:
            if system_prompt and "JSON" in system_prompt:
                return """```json
{
  "claim_id": "MOCK-123",
  "employee_id": "EMP-999",
  "items": [
    {
      "receipt_id": "REC-999",
      "amount": 999.0,
      "currency": "USD",
      "date": "2024-01-01",
      "category": "Mock Expense",
      "description": "This is a mock claim generated because no Groq API key was found.",
      "merchant": "Mock Merchant",
      "receipt_attached": true
    }
  ]
}
```"""
            return "This is a mock explanation because no Groq API key was provided. The reasoning follows the deterministic policy engine."
        
        default_system_prompt = "You are a Travel Reimbursement Approval Agent. Use ONLY the supplied policy context and tool results. Never invent policy. Never override deterministic calculations. Return a clear and concise explanation for the decision."
        actual_system_prompt = system_prompt if system_prompt else default_system_prompt
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": actual_system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.0
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error communicating with LLM: {str(e)}"
