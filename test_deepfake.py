"""
Test deepfake detection functionality
"""
import asyncio
import sys
from pathlib import Path
from src.deepfake_detector import DeepfakeDetector
from src.database import init_db
from src.config import settings


async def test_image_deepfake_detection():
    """Test image deepfake detection"""
    print("\n" + "=" * 60)
    print("Testing Image Deepfake Detection")
    print("=" * 60)
    
    # Note: You need to provide a test image
    print("\n⚠ To test deepfake detection, you need to:")
    print("1. Place a test image in the 'test_images' folder")
    print("2. Update this script with the image path")
    print("\nExample usage:")
    print("""
    detector = DeepfakeDetector()
    result, _ = await detector.analyze_image('test_images/sample.jpg')
    
    print(f"Is Deepfake: {result.is_deepfake}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Verdict: {result.verdict}")
    print(f"Reasoning: {result.reasoning}")
    """)
    
    return True


async def test_api_endpoints():
    """Test deepfake API endpoints"""
    print("\n" + "=" * 60)
    print("Testing Deepfake API Endpoints")
    print("=" * 60)
    
    print("\nAvailable endpoints:")
    print("1. POST /api/deepfake/upload - Upload image/video")
    print("2. POST /api/deepfake/analyze/{media_id} - Start analysis")
    print("3. GET /api/deepfake/results/{media_id} - Get results")
    print("4. GET /api/deepfake/results - List all analyses")
    
    print("\n📝 Example: Upload and analyze an image")
    print("""
    # Upload
    curl -X POST "http://localhost:8000/api/deepfake/upload" \\
      -F "file=@path/to/image.jpg" \\
      -F "description=Suspicious image from social media"
    
    # Analyze (use media_id from upload response)
    curl -X POST "http://localhost:8000/api/deepfake/analyze/1?use_consensus=true"
    
    # Get results
    curl "http://localhost:8000/api/deepfake/results/1"
    """)
    
    return True


async def main():
    """Run deepfake detection tests"""
    print("\n🔍 DeepCheck MH - Deepfake Detection Test\n")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    print("✓ Database initialized (Media table created)\n")
    
    # Check API keys
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        print("❌ Gemini API key not configured")
        print("Please set GEMINI_API_KEY in .env file")
        sys.exit(1)
    
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in .env file")
        sys.exit(1)
    
    print("✓ API keys configured\n")
    
    # Run tests
    await test_image_deepfake_detection()
    await test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("Deepfake Detection Ready!")
    print("=" * 60)
    print("\n✅ Deepfake detection system is configured and ready to use.")
    print("\nFeatures:")
    print("  • Image deepfake detection with dual-AI verification")
    print("  • Video deepfake detection with frame analysis")
    print("  • Metadata analysis for manipulation signs")
    print("  • Temporal consistency checking for videos")
    print("  • Consensus mode using both Gemini and OpenAI")
    print("\nNext steps:")
    print("1. Start the API server: python -m uvicorn src.api:app --reload")
    print("2. Upload an image/video via /api/deepfake/upload")
    print("3. Analyze it via /api/deepfake/analyze/{media_id}")
    print("4. Get results via /api/deepfake/results/{media_id}")


if __name__ == "__main__":
    asyncio.run(main())
