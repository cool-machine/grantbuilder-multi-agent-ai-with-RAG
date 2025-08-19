#!/usr/bin/env python3
"""
Local testing script for the tokenizer function
Run this to test the function locally before deployment
"""

import requests
import json
import time

# Local function URL (when running with 'func start')
LOCAL_URL = "http://localhost:7071/api/TokenizerFunction"

def test_get_request():
    """Test GET request for API information"""
    print("🧪 Testing GET request...")
    try:
        response = requests.get(LOCAL_URL)
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ GET request failed: {e}")
        return False

def test_post_request():
    """Test POST request for tokenization"""
    print("\n🧪 Testing POST request...")
    
    test_data = {
        "text": "Hello, world! How are you today?",
        "model": "gpt2",  # Using gpt2 for testing
        "options": {
            "add_special_tokens": True,
            "include_decoded": True
        }
    }
    
    try:
        print(f"Sending: {json.dumps(test_data, indent=2)}")
        response = requests.post(
            LOCAL_URL,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ POST request failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n🧪 Testing error handling...")
    
    # Test with missing text
    test_data = {"model": "gpt2"}
    
    try:
        response = requests.post(
            LOCAL_URL,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 400  # Should return bad request
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting local tokenizer function tests...")
    print("Make sure the function is running locally with 'func start'")
    print("=" * 60)
    
    # Wait a moment for any startup
    time.sleep(1)
    
    tests = [
        ("GET Request", test_get_request),
        ("POST Request", test_post_request),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print(f"{'✅ PASSED' if result else '❌ FAILED'}")
        print("-" * 40)
    
    print("\n📊 Test Results:")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the function logs.")

if __name__ == "__main__":
    main()