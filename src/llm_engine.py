import os
import requests
from dotenv import load_dotenv

# Load the .env file immediately
load_dotenv()

class LLMEngine:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.model = "nvidia/llama-3.1-nemotron-nano-8b-v1"

    def ask_nemotron(self, context, question):
        if not self.api_key:
            return "Error: NVIDIA API Key is missing. Check your .env file."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Prompt Engineering: We tell the model to be a document assistant
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant. Answer the question based ONLY on the provided Context. If the answer is not in the context, say 'I cannot find that information in the document.'"
                },
                {
                    "role": "user", 
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ],
            "temperature": 0.2, # Low temperature = more factual
            "max_tokens": 1024,
            "stream": False
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status() # Raises error for 400/500 codes
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error connecting to NVIDIA API: {str(e)}"