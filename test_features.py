"""
Test script for Deepfake Detection and Detection Cycle
"""
import requests
import time
import json
from PIL import Image, ImageDraw
import os

BASE_URL = "http://localhost:8000/api"

def create_test_image(filename="test_image.jpg"):
    """Create a simple test image"""
    print(f"🎨 Creating test image: {filename}...")
    img = Image.new('RGB', (512, 512), color='red')
    d = ImageDraw.Draw(img)
    d.text((10,10), "Test Image for DeepCheck", fill=(255,255,0))
    img.save(filename)
    return filename

def test_deepfake_detection():
    print("\n" + "="*50)
    print("🧪 Testing Deepfake Detection")
    print("="*50)
    
    # 1. Create Image
    filename = create_test_image()
    
    # 2. Upload
    print("📤 Uploading image...")
    with open(filename, 'rb') as f:
        files = {'file': f}
        data = {'description': 'Automated test image'}
        response = requests.post(f"{BASE_URL}/deepfake/upload", files=files, data=data)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return
    
    upload_data = response.json()
    media_id = upload_data['media_id']
    print(f"✅ Upload successful! Media ID: {media_id}")
    
    # 3. Analyze
    print(f"🔍 Starting analysis for Media ID {media_id}...")
    # Note: use_consensus=False is default in config now, but explicit doesn't hurt
    response = requests.post(f"{BASE_URL}/deepfake/analyze/{media_id}?use_consensus=false")
    
    if response.status_code != 200:
        print(f"❌ Analysis start failed: {response.text}")
        return
        
    print("⏳ Analysis started, waiting for results...")
    
    # 4. Poll for results
    for i in range(10):
        time.sleep(2)
        response = requests.get(f"{BASE_URL}/deepfake/results/{media_id}")
        result = response.json()
        
        status = result.get('analysis_status')
        print(f"   Status: {status}")
        
        if status == 'completed':
            print("\n✅ Analysis Completed!")
            print(f"   Verdict: {result.get('verdict')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Is Deepfake: {result.get('is_deepfake')}")
            print(f"   Report: {result.get('analysis_report')[:100]}...")
            break
        elif status == 'failed':
            print(f"❌ Analysis failed: {result.get('analysis_report')}")
            break
            
    # Cleanup
    if os.path.exists(filename):
        os.remove(filename)

def test_detection_cycle():
    print("\n" + "="*50)
    print("🔄 Testing Detection Cycle")
    print("="*50)
    
    print("🚀 Triggering detection cycle...")
    response = requests.post(f"{BASE_URL}/run-cycle")
    
    if response.status_code != 200:
        print(f"❌ Failed to trigger cycle: {response.text}")
        return
        
    data = response.json()
    print(f"✅ Cycle triggered! Message: {data.get('message')}")
    
    print("⏳ Waiting for cycle to process (this may take 10-20 seconds)...")
    # The run-cycle endpoint is async background task, so we need to poll /api/stats or /api/claims
    
    # Wait a bit for processing
    time.sleep(15)
    
    print("📊 Checking for new claims...")
    response = requests.get(f"{BASE_URL}/claims")
    claims = response.json()
    
    # claims is a list directly
    print(f"✅ Found {len(claims)} claims in database")
    
    if claims:
        print("\nLatest Claim:")
        latest = claims[0]
        print(f"   Text: {latest.get('text')}")
        print(f"   Verdict: {latest.get('latest_verification', {}).get('verdict')}")
        print(f"   Source: {latest.get('source', {}).get('name')}")

if __name__ == "__main__":
    try:
        test_deepfake_detection()
        test_detection_cycle()
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
