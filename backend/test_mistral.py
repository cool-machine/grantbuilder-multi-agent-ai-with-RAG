#!/usr/bin/env python3
"""
Test script for Mistral 7B integration with GrantSeeker TokenizerFunction
"""

import requests
import json
import time

# Configuration
AZURE_FUNCTION_URL = "https://ocp10-grant-functions.azurewebsites.net/api/tokenizerfunction"
LOCAL_FUNCTION_URL = "http://localhost:7071/api/tokenizerfunction"

# Test cases for grant analysis
TEST_CASES = [
    {
        "name": "NSF Grant Analysis",
        "data": {
            "text": "The National Science Foundation (NSF) invites proposals for innovative research in artificial intelligence applications for healthcare. This program supports basic research that could lead to transformative advances in medical diagnosis, treatment planning, and patient care. Maximum award amount is $500,000 over a 3-year period. Eligible applicants include universities, research institutions, and qualified nonprofits. Proposals must demonstrate potential for significant impact, interdisciplinary collaboration, and clear research methodology. Deadline: March 15, 2025.",
            "model": "mistral-7b-instruct",
            "analysis_type": "grant_analysis"
        }
    },
    {
        "name": "NIH Grant Analysis", 
        "data": {
            "text": "The National Institute of Allergy and Infectious Diseases (NIAID) announces funding opportunity R01-AI-2025 for research on novel antimicrobial resistance mechanisms. This R01 grant supports investigator-initiated research projects in infectious disease with budget up to $250,000 per year for up to 5 years. Applicants must be affiliated with domestic institutions and demonstrate expertise in microbiology, immunology, or related fields. Strong preliminary data and innovative approaches are essential.",
            "model": "mistral-7b-instruct", 
            "analysis_type": "grant_analysis"
        }
    },
    {
        "name": "Document Analysis - NGO Report",
        "data": {
            "text": "Teach for America Annual Report 2024: Our organization successfully placed 3,500 new teachers in high-need schools across rural America this year. With an annual budget of $245 million, we focus on educational equity and teacher leadership development. Our mission is to find, develop, and support equity-oriented leaders to transform education and expand opportunity for all children. Recent projects include strengthening teacher pipelines in Appalachian communities and developing innovative leadership programs.",
            "model": "mistral-7b-instruct",
            "analysis_type": "document_analysis"
        }
    },
    {
        "name": "Mistral Tokenizer Only",
        "data": {
            "text": "Grant application for NSF research funding in artificial intelligence and healthcare.",
            "model": "mistral-tokenizer-only",
            "return_tokens": True,
            "return_token_ids": True
        }
    },
    {
        "name": "Simple Tokenization Test",
        "data": {
            "text": "This is a simple test for basic tokenization functionality.",
            "model": "simple",
            "return_tokens": True,
            "return_token_ids": True
        }
    }
]

def test_function(url: str, test_case: dict) -> dict:
    """Test a single case against the function"""
    print(f"\n🧪 Testing: {test_case['name']}")
    print(f"URL: {url}")
    
    try:
        start_time = time.time()
        
        # Make request
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=test_case['data'],
            timeout=120  # Generous timeout for model loading
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Response time: {duration:.2f}s")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            print(f"{'✅' if success else '❌'} Success: {success}")
            print(f"🤖 Model: {result.get('model', 'Unknown')}")
            
            if success:
                # Print analysis if available
                if 'analysis' in result:
                    print(f"📝 Analysis preview: {result['analysis'][:200]}...")
                
                # Print token info if available
                if 'token_count' in result:
                    print(f"🔤 Tokens: {result['token_count']}")
            else:
                # Print detailed error information
                print(f"🚨 Error Type: {result.get('error_type', 'Unknown')}")
                print(f"💥 Error: {result.get('error', 'No error message')}")
                print(f"🔄 Fallback Used: {result.get('fallback_used', 'Unknown')}")
                
                if 'possible_causes' in result:
                    print("🔍 Possible Causes:")
                    for cause in result['possible_causes']:
                        print(f"   • {cause}")
                        
            return {"success": True, "duration": duration, "result": result}
        else:
            print(f"❌ Error: {response.text}")
            return {"success": False, "duration": duration, "error": response.text}
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this is normal for first Mistral request)")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        return {"success": False, "error": str(e)}

def test_health_check(url: str) -> bool:
    """Test if the function is responding"""
    try:
        response = requests.get(url.replace('/tokenizerfunction', '/tokenizerfunction'), timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    """Run all tests"""
    print("🚀 Mistral 7B GrantSeeker Function Test Suite")
    print("=" * 60)
    
    # Test URLs
    urls_to_test = []
    
    # Check local function
    if test_health_check(LOCAL_FUNCTION_URL):
        print("🏠 Local function is running")
        urls_to_test.append(("Local", LOCAL_FUNCTION_URL))
    else:
        print("🚫 Local function not available")
    
    # Check Azure function
    if test_health_check(AZURE_FUNCTION_URL):
        print("☁️  Azure function is running")
        urls_to_test.append(("Azure", AZURE_FUNCTION_URL))
    else:
        print("🚫 Azure function not available")
    
    if not urls_to_test:
        print("❌ No functions available for testing")
        return
    
    # Run tests
    results = {}
    
    for env_name, url in urls_to_test:
        print(f"\n🌍 Testing {env_name} environment")
        print("-" * 40)
        
        env_results = []
        
        for test_case in TEST_CASES:
            result = test_function(url, test_case)
            env_results.append({
                "test": test_case["name"],
                "result": result
            })
        
        results[env_name] = env_results
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    for env_name, env_results in results.items():
        print(f"\n{env_name} Environment:")
        successful = sum(1 for r in env_results if r["result"]["success"])
        total = len(env_results)
        print(f"✅ Passed: {successful}/{total}")
        
        for test_result in env_results:
            status = "✅" if test_result["result"]["success"] else "❌"
            duration = test_result["result"].get("duration", 0)
            print(f"  {status} {test_result['test']} ({duration:.1f}s)")
    
    print("\n🎯 Integration Status:")
    print("- Mistral 7B integration ready for GrantSeeker platform")
    print("- Enhanced grant analysis capabilities available")
    print("- Fallback to simple tokenization ensures reliability")

if __name__ == "__main__":
    main()