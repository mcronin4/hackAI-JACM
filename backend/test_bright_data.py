#!/usr/bin/env python3
"""
Simple test script for Bright Data Twitter scraping
Run this to verify the API works before integrating into main app
"""

import os
import requests
import json
from datetime import datetime
import dotenv
dotenv.load_dotenv()

def test_bright_data_twitter_scraping():
    """Test Bright Data API for Twitter scraping"""
    
    # Get API key from environment
    api_key = os.getenv("BRIGHT_DATA_API_KEY")
    if not api_key:
        print("❌ Error: BRIGHT_DATA_API_KEY not found in environment variables")
        return False
    
    # Test with a well-known Twitter handle (replace with any public handle)
    test_handle = "elonmusk"  # Change this to test different handles
    
    print(f"🔍 Testing Bright Data scraping for @{test_handle}")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Bright Data API setup (using correct format)
    url = "https://api.brightdata.com/datasets/v3/scrape"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    params = {
        "dataset_id": "gd_lwxmeb2u1cniijd7t4",
        "include_errors": "true",
    }
    data = [
        {"url": f"https://x.com/{test_handle}", "max_number_of_posts": 10}
    ]
    
    try:
        print("📡 Making request to Bright Data API...")
        print(f"🔗 URL: {data[0]['url']}")
        
        response = requests.post(url, headers=headers, params=params, json=data)
    
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Bright Data API is working")
            
            # Save response to file for inspection
            output_file = f"bright_data_test_output_{test_handle}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"💾 Full response saved to: {output_file}")
            
            # Show a preview of the data structure
            print("\n📋 Data Structure Preview:")
            print(f"   - Response type: {type(result)}")
            
            if isinstance(result, dict):

                print("First post:", result['posts'][0])

                print(f"   - Top-level keys: {list(result.keys())}")
                
                # Look for common response fields
                if 'snapshot_id' in result:
                    print(f"   - Snapshot ID: {result['snapshot_id']}")
                if 'status' in result:
                    print(f"   - Status: {result['status']}")
                if 'dataset_id' in result:
                    print(f"   - Dataset ID: {result['dataset_id']}")
            
            return True
            
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out - this might be normal for Bright Data")
        print("💡 Try checking your Bright Data dashboard for the job status")
        return False
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False

def show_api_format():
    """Show the API format we're using"""
    print("\n📝 API Request Format:")
    print("URL: https://api.brightdata.com/datasets/v3/trigger")
    print("Headers: Authorization: Bearer <api-key>")
    print("Params: dataset_id=gd_lwxmeb2u1cniijd7t4")
    print("Data: [{'url': 'https://x.com/username', 'max_number_of_posts': 10}]")

if __name__ == "__main__":
    print("🚀 Bright Data Twitter Scraping Test")
    print("=" * 50)
    
    # Show API format
    show_api_format()
    
    print("\n" + "=" * 50)
    
    # Test the API
    success = test_bright_data_twitter_scraping()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("💡 Check the output JSON file to see the response structure")
        print("💡 You can now integrate Bright Data into your main application")
    else:
        print("\n❌ Test failed!")
        print("🔧 Check your API key and Bright Data configuration") 