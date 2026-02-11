#!/usr/bin/env python3
"""Test the search API endpoint"""

import requests
import sys
import os
from pathlib import Path

# Test if backend is running
API_BASE_URL = "http://localhost:8000/api"
SEARCH_ENDPOINT = f"{API_BASE_URL}/search-face"

def test_api_connection():
    """Test if API is reachable"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_search_with_sample_image():
    """Test search with a sample image from database uploads"""
    try:
        # Find a test image
        uploads_dir = Path(__file__).parent / "backend" / "uploads"
        image_files = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.png")) + list(uploads_dir.glob("*.gif"))
        
        if not image_files:
            print("❌ No test images found in uploads directory")
            return False
        
        test_image = image_files[0]
        print(f"📁 Using test image: {test_image.name}")
        
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post(SEARCH_ENDPOINT, files=files, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Matches found: {len(data.get('matches', []))}")
            if data.get('matches'):
                for i, match in enumerate(data['matches'][:3], 1):
                    print(f"   {i}. {match['name']}: {match.get('similarity_percentage', 0)}%")
            return True
        else:
            print(f"❌ Search failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Testing FindThem Search API\n")
    
    print("Step 1: Testing API connection...")
    if not test_api_connection():
        print("\n❌ Cannot proceed - API is not running")
        sys.exit(1)
    
    print("\nStep 2: Testing search endpoint...")
    if test_search_with_sample_image():
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  Search test failed")

if __name__ == "__main__":
    main()
