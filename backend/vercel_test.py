#!/usr/bin/env python3
"""
Simple test script to verify Vercel deployment works.
Run this locally after deployment to test your Vercel URL.
"""

import requests
import json
import os
from typing import Dict, Any

def test_vercel_deployment(base_url: str) -> None:
    """Test the main endpoints of the deployed API"""
    
    print(f"Testing Vercel deployment at: {base_url}")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    print()
    
    # Test 2: Health check
    print("2. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("✅ Health check working")
            health_data = response.json()
            print(f"   Services status: {len(health_data.get('services', {}))} services")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 3: API Documentation
    print("3. Testing API docs...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API docs accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")
    
    print()
    
    # Test 4: Topic extraction (lightweight test)
    print("4. Testing topic extraction...")
    try:
        test_data = {
            "text": "This is a test message about artificial intelligence and machine learning technologies."
        }
        response = requests.post(f"{base_url}/api/v1/extract-topics", json=test_data)
        if response.status_code == 200:
            print("✅ Topic extraction working")
            result = response.json()
            print(f"   Extracted {result.get('total_topics', 0)} topics")
        else:
            print(f"❌ Topic extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Topic extraction error: {e}")
    
    print()
    
    # Test 5: Platform support
    print("5. Testing platform support...")
    try:
        response = requests.get(f"{base_url}/api/v1/platforms")
        if response.status_code == 200:
            print("✅ Platform support working")
            platforms = response.json()
            print(f"   Supported platforms: {list(platforms.keys())}")
        else:
            print(f"❌ Platform support failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Platform support error: {e}")
    
    print()
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    # Replace with your actual Vercel URL
    vercel_url = input("Enter your Vercel URL (e.g., https://your-app.vercel.app): ").strip()
    
    if not vercel_url:
        print("Please provide a Vercel URL")
        exit(1)
    
    # Remove trailing slash if present
    vercel_url = vercel_url.rstrip('/')
    
    test_vercel_deployment(vercel_url) 