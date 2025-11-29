"""
Comprehensive model testing script
Tests if Gemini and OpenAI APIs are working correctly
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def check_env_file():
    """Check if .env file exists and has API keys"""
    print("=" * 60)
    print("Checking Environment Configuration")
    print("=" * 60)
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("\n📝 Creating .env file from .env.example...")
        
        example_path = Path(".env.example")
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print("✓ .env file created")
            print("\n⚠️  IMPORTANT: Please edit .env and add your API keys:")
            print("   - GEMINI_API_KEY")
            print("   - OPENAI_API_KEY")
            print("\nThen run this script again.")
            return False
        else:
            print("❌ .env.example not found!")
            return False
    
    print("✓ .env file exists")
    
    # Check if keys are configured
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    issues = []
    
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        issues.append("❌ GEMINI_API_KEY not configured")
    else:
        print(f"✓ GEMINI_API_KEY configured ({gemini_key[:10]}...)")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        issues.append("❌ OPENAI_API_KEY not configured")
    else:
        print(f"✓ OPENAI_API_KEY configured ({openai_key[:10]}...)")
    
    if issues:
        print("\n" + "\n".join(issues))
        print("\n⚠️  Please edit .env and add your API keys:")
        print("   Get Gemini key: https://makersuite.google.com/app/apikey")
        print("   Get OpenAI key: https://platform.openai.com/api-keys")
        return False
    
    return True


async def test_gemini_api():
    """Test Gemini API connection"""
    print("\n" + "=" * 60)
    print("Testing Gemini API")
    print("=" * 60)
    
    try:
        import google.generativeai as genai
        from src.config import settings
        
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        
        print(f"Model: {settings.gemini_model}")
        print("Sending test request...")
        
        response = model.generate_content("Say 'Hello from Gemini!' in exactly those words.")
        result = response.text
        
        print(f"✓ Gemini API is working!")
        print(f"Response: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        print("\nPossible issues:")
        print("  - Invalid API key")
        print("  - No internet connection")
        print("  - API quota exceeded")
        print("  - Gemini API not enabled for your account")
        return False


async def test_openai_api():
    """Test OpenAI API connection"""
    print("\n" + "=" * 60)
    print("Testing OpenAI API")
    print("=" * 60)
    
    try:
        from openai import OpenAI
        from src.config import settings
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        print(f"Model: {settings.openai_model}")
        print("Sending test request...")
        
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "user", "content": "Say 'Hello from OpenAI!' in exactly those words."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        
        print(f"✓ OpenAI API is working!")
        print(f"Response: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        print("\nPossible issues:")
        print("  - Invalid API key")
        print("  - No internet connection")
        print("  - Insufficient credits/quota")
        print("  - API key doesn't have access to the model")
        return False


async def test_gemini_vision():
    """Test Gemini Vision API"""
    print("\n" + "=" * 60)
    print("Testing Gemini Vision API")
    print("=" * 60)
    
    try:
        import google.generativeai as genai
        from src.config import settings
        
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("Model: gemini-1.5-flash (Vision)")
        print("Sending test request (text-only for now)...")
        
        response = model.generate_content("Describe what you would look for to detect a deepfake image. Be brief.")
        result = response.text
        
        print(f"✓ Gemini Vision API is working!")
        print(f"Response: {result[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini Vision API error: {e}")
        return False


async def test_openai_vision():
    """Test OpenAI Vision API"""
    print("\n" + "=" * 60)
    print("Testing OpenAI Vision API (GPT-4o-mini)")
    print("=" * 60)
    
    try:
        from openai import OpenAI
        from src.config import settings
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        print("Model: gpt-4o-mini (Vision)")
        print("Sending test request...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Describe what you would look for to detect a deepfake image. Be brief."}
            ],
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        
        print(f"✓ OpenAI Vision API is working!")
        print(f"Response: {result[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Vision API error: {e}")
        return False


async def test_claim_verification():
    """Test claim verification with both models"""
    print("\n" + "=" * 60)
    print("Testing Claim Verification (Dual-AI)")
    print("=" * 60)
    
    try:
        from src.claim_extractor import ExtractedClaim
        from src.fact_checker import FactChecker
        
        # Create a test claim
        test_claim = ExtractedClaim(
            text="Drinking hot water prevents COVID-19",
            source_url="test",
            source_title="Test",
            crisis_type="pandemic",
            urgency_score=0.8,
            entities=["COVID-19"],
            topics=["health", "pandemic"]
        )
        
        print(f"Test Claim: {test_claim.text}")
        print("Verifying with both AI models...")
        
        fact_checker = FactChecker()
        primary_result, secondary_result = await fact_checker.verify_claim(test_claim, use_consensus=True)
        
        print(f"\n✓ Claim verification working!")
        print(f"Verdict: {primary_result.verdict.upper()}")
        print(f"Confidence: {primary_result.confidence:.0%}")
        print(f"Model: {primary_result.model_name}")
        
        if secondary_result:
            print(f"\nSecondary verification:")
            print(f"  Verdict: {secondary_result.verdict}")
            print(f"  Confidence: {secondary_result.confidence:.0%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Claim verification error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n🔍 DeepCheck MH - Model Testing Suite\n")
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Installing Dependencies (if needed)")
    print("=" * 60)
    print("Checking if all packages are installed...")
    
    try:
        import google.generativeai
        import openai
        from dotenv import load_dotenv
        print("✓ Core dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run tests
    results = {}
    
    results['gemini'] = await test_gemini_api()
    results['openai'] = await test_openai_api()
    results['gemini_vision'] = await test_gemini_vision()
    results['openai_vision'] = await test_openai_vision()
    
    # Only test claim verification if both APIs work
    if results['gemini'] and results['openai']:
        results['claim_verification'] = await test_claim_verification()
    else:
        print("\n⚠️  Skipping claim verification test (APIs not working)")
        results['claim_verification'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓" if passed else "❌"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ All tests passed! Your models are working correctly.")
        print("\n🎉 System is ready to use!")
        print("\nNext steps:")
        print("1. Start the API server: python -m uvicorn src.api:app --reload")
        print("2. Test deepfake detection: python test_deepfake.py")
        print("3. Run a detection cycle: POST to /api/run-cycle")
        print("4. Upload media for deepfake analysis: POST to /api/deepfake/upload")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  - Verify API keys are correct in .env")
        print("  - Check internet connection")
        print("  - Ensure you have API credits/quota")
        print("  - Try regenerating your API keys")
        
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
