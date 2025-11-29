"""Check OpenAI API status in detail"""
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Checking OpenAI API status...")
print("=" * 60)

try:
    # Try a minimal request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=5
    )
    print("✓ OpenAI API is working!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    error_str = str(e)
    print(f"❌ Error: {error_str}")
    
    if "quota" in error_str.lower() or "insufficient" in error_str.lower():
        print("\n📊 This means:")
        print("  - Your API key is valid")
        print("  - But you have no credits/quota available")
        print("\n💡 Solutions:")
        print("  1. Check your usage: https://platform.openai.com/usage")
        print("  2. Add credits: https://platform.openai.com/account/billing")
        print("  3. Free trial credits may have expired")
        print("\n⚠️  For now, the system works perfectly with just Gemini!")
        print("     You can add OpenAI credits later for dual-AI mode.")
        
    elif "api_key" in error_str.lower() or "authentication" in error_str.lower():
        print("\n❌ API key issue - please check your key")
        
    else:
        print(f"\n❓ Unexpected error: {error_str}")
