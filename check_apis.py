"""
Simple diagnostic to check API status
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "=" * 60)
print("API Key Status Check")
print("=" * 60)

# Check Gemini
gemini_key = os.getenv("GEMINI_API_KEY", "")
if gemini_key and gemini_key != "your_gemini_api_key_here":
    print(f"✓ Gemini API Key: {gemini_key[:15]}...")
    
    # Test Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        
        # List available models
        print("\n  Available Gemini models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"    - {m.name}")
        
        # Try with gemini-pro
        print("\n  Testing with gemini-pro...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say hello")
        print(f"  ✓ Gemini working! Response: {response.text[:50]}...")
        
    except Exception as e:
        print(f"  ❌ Gemini error: {e}")
else:
    print("❌ Gemini API Key not configured")

# Check OpenAI
print("\n" + "-" * 60)
openai_key = os.getenv("OPENAI_API_KEY", "")
if openai_key and openai_key != "your_openai_api_key_here":
    print(f"✓ OpenAI API Key: {openai_key[:15]}...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        print("  Testing OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print(f"  ✓ OpenAI working! Response: {response.choices[0].message.content}")
        
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            print(f"  ❌ OpenAI quota exceeded - please add credits at:")
            print(f"     https://platform.openai.com/account/billing")
        else:
            print(f"  ❌ OpenAI error: {e}")
else:
    print("❌ OpenAI API Key not configured")

# Check NewsAPI
print("\n" + "-" * 60)
news_key = os.getenv("NEWS_API_KEY", "")
if news_key and news_key != "your_newsapi_key_here":
    print(f"✓ NewsAPI Key: {news_key[:15]}...")
    
    try:
        import requests
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_key}&pageSize=1"
        response = requests.get(url)
        
        if response.status_code == 200:
            print("  ✓ NewsAPI working!")
        else:
            print(f"  ❌ NewsAPI error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ NewsAPI error: {e}")
else:
    print("⚠️  NewsAPI Key not configured (optional)")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("\nNext steps:")
print("1. If Gemini shows available models, update src/config.py to use one of them")
print("2. If OpenAI shows quota error, add credits at platform.openai.com")
print("3. NewsAPI is optional for now")
print("\nOnce APIs are working, you can:")
print("  - Start the server: python3 -m uvicorn src.api:app --reload")
print("  - Test deepfake detection: Upload an image via /api/deepfake/upload")
