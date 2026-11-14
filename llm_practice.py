import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
print("Key loaded:", api_key is not None)

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
    messages=[
        {"role": "system", "content": "You are a support ticket assistant. Reply in one short sentence."},
        {"role": "user", "content": "A customer says: I was charged twice for my order. What should we do first?"},
    ],
    temperature=1.0,
)

print(response.choices[0].message.content)