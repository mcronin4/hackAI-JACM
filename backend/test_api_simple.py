#!/usr/bin/env python3
"""
Simple API test to debug the frontend connection issue
"""

import requests
import json

def test_api_health():
    """Test basic API connectivity"""
    try:
        # Test basic connectivity
        response = requests.get("http://localhost:8000", timeout=5)
        print(f"✅ Backend is running - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running")
        print("Please start the backend with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def test_generate_posts_api():
    """Test the generate posts API endpoint"""
    print("\n🧪 Testing /api/v1/generate-posts endpoint...")
    
    # Simple test request
    test_data = {
        "text": "This is a simple test message for API debugging.",
        "target_platforms": ["twitter"]
    }
    
    try:
        print(f"📤 Sending request to: http://localhost:8000/api/v1/generate-posts")
        print(f"📝 Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/api/v1/generate-posts",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📥 Response Data: {json.dumps(data, indent=2)}")
                
                # Check response structure
                if isinstance(data, dict):
                    print("\n✅ Response is a valid JSON object")
                    
                    # Check for expected fields
                    expected_fields = ['success', 'platform_posts', 'generated_posts']
                    for field in expected_fields:
                        if field in data:
                            print(f"✅ Has '{field}' field")
                        else:
                            print(f"❌ Missing '{field}' field")
                    
                    return data
                else:
                    print(f"❌ Response is not a JSON object: {type(data)}")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the backend running?")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def main():
    print("🔍 API Debugging Tool")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    if not test_api_health():
        return
    
    # Test 2: Test the generate posts endpoint
    result = test_generate_posts_api()
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 API test completed successfully!")
        print("✅ The backend is working correctly")
        print("✅ Frontend should be able to connect")
    else:
        print("❌ API test failed")
        print("🔧 Possible issues:")
        print("   - Backend not running (run: python main.py)")
        print("   - API endpoint changed")
        print("   - Missing environment variables")
        print("   - Backend error (check backend logs)")

if __name__ == "__main__":
    main() 