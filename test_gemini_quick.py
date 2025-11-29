"""Quick test of Gemini 2.5 Flash"""
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Testing Gemini 2.5 Flash...")
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("Say 'Gemini 2.5 Flash is working!' and nothing else.")
print(f"✓ Response: {response.text}")
