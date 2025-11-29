"""
Test script to verify the AI agent setup
Run this after setting up your .env file with API keys
"""
import asyncio
import sys
from src.config import settings
from src.agent import agent
from src.database import init_db


async def test_api_keys():
    """Test if API keys are configured"""
    print("=" * 60)
    print("Testing API Key Configuration")
    print("=" * 60)
    
    issues = []
    
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        issues.append("❌ Gemini API key not configured")
    else:
        print("✓ Gemini API key configured")
    
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        issues.append("❌ OpenAI API key not configured")
    else:
        print("✓ OpenAI API key configured")
    
    if settings.news_api_key and settings.news_api_key != "your_newsapi_key_here":
        print("✓ NewsAPI key configured (optional)")
    else:
        print("⚠ NewsAPI key not configured (optional)")
    
    if issues:
        print("\n" + "\n".join(issues))
        print("\nPlease configure missing API keys in .env file")
        return False
    
    return True


async def test_claim_verification():
    """Test custom claim verification"""
    print("\n" + "=" * 60)
    print("Testing Claim Verification")
    print("=" * 60)
    
    test_claim = "Drinking hot water prevents COVID-19"
    print(f"\nTest Claim: {test_claim}")
    print("\nVerifying with both AI models...")
    
    try:
        result = await agent.verify_custom_claim(test_claim, audience_level='general')
        
        print(f"\n✓ Verification completed!")
        print(f"  Verdict: {result['verdict'].upper()}")
        print(f"  Confidence: {result['confidence']:.0%}")
        print(f"  Credibility Score: {result['credibility_score']:.2f}")
        print(f"\n  Title: {result['explanation']['title']}")
        print(f"  Summary: {result['explanation']['summary'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        return False


async def test_content_monitoring():
    """Test content monitoring (just fetch, don't process)"""
    print("\n" + "=" * 60)
    print("Testing Content Monitoring")
    print("=" * 60)
    
    try:
        from src.content_monitor import ContentAggregator
        
        aggregator = ContentAggregator()
        print("\nFetching content from sources (this may take a moment)...")
        
        content_items = await aggregator.fetch_all_content()
        
        print(f"\n✓ Successfully fetched {len(content_items)} content items")
        
        if content_items:
            print("\nSample content:")
            for i, item in enumerate(content_items[:3]):
                print(f"\n  {i+1}. {item.title[:80]}...")
                print(f"     Source: {item.source}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during content monitoring: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n🔍 DeepCheck MH - System Test\n")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    print("✓ Database initialized\n")
    
    # Test API keys
    if not await test_api_keys():
        print("\n⚠ Please configure API keys before running full tests")
        sys.exit(1)
    
    # Test claim verification
    verification_ok = await test_claim_verification()
    
    # Test content monitoring
    monitoring_ok = await test_content_monitoring()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"API Keys: ✓")
    print(f"Claim Verification: {'✓' if verification_ok else '❌'}")
    print(f"Content Monitoring: {'✓' if monitoring_ok else '❌'}")
    
    if verification_ok and monitoring_ok:
        print("\n✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Start the API server: python -m uvicorn src.api:app --reload")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Run a detection cycle: POST to /api/run-cycle")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
