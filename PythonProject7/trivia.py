import os
import requests

api_key = os.getenv("GROQ_API_KEY")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "groq-llm",
    "messages": [
        {"role": "user", "content": "Generate a multiple-choice trivia question about science."}
    ],
    "temperature": 0.7
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
question = response.json()
