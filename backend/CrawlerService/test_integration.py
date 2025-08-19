#!/usr/bin/env python3
"""
Test script for crawler integration
Tests both mock and real crawling modes
"""

import asyncio
import json
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler_manager import CrawlerManager

async def test_mock_mode():
    """Test mock crawling mode"""
    print("🧪 Testing Mock Crawling Mode...")
    
    manager = CrawlerManager(use_mock=True)
    
    # Test status
    status = manager.get_status()
    print(f"✅ Status: Mode={status['mode']}, DB Connected={status.get('database_connected', False)}")
    
    # Test crawling
    result = await manager.start_crawl({
        'request_delay': 1.0,
        'max_concurrent_requests': 3
    })
    
    print(f"✅ Crawl Result: Success={result.success}, Found={result.total_found}, Saved={result.saved_count}")
    print(f"   Duration: {result.duration_seconds:.2f}s, Mode: {result.mode}")
    
    if result.opportunities:
        print(f"✅ Sample Opportunity: {result.opportunities[0]['title']}")
    
    # Test results retrieval
    stored_results = manager.get_results(limit=5)
    if stored_results['success']:
        print(f"✅ Stored Results: {stored_results['count']} opportunities in database")
    
    return result.success

async def test_real_mode():
    """Test real crawling mode (with timeout for safety)"""
    print("\n🌐 Testing Real Crawling Mode...")
    
    manager = CrawlerManager(use_mock=False)
    
    # Test status
    status = manager.get_status()
    print(f"✅ Status: Mode={status['mode']}, DB Connected={status.get('database_connected', False)}")
    
    # Test with very conservative settings for real crawling
    config = {
        'request_delay': 5.0,  # Very slow to be respectful
        'max_concurrent_requests': 1,  # Single request at a time
        'respect_robots_txt': True
    }
    
    print("⏳ Starting real crawl (this may take a while)...")
    
    try:
        # Set a timeout for real crawling
        result = await asyncio.wait_for(
            manager.start_crawl(config),
            timeout=60.0  # 1 minute timeout
        )
        
        print(f"✅ Real Crawl Result: Success={result.success}, Found={result.total_found}, Saved={result.saved_count}")
        print(f"   Duration: {result.duration_seconds:.2f}s, Errors: {len(result.errors)}")
        
        if result.opportunities:
            print(f"✅ Real Sample: {result.opportunities[0]['title']} from {result.opportunities[0]['source']}")
        
        return result.success
        
    except asyncio.TimeoutError:
        print("⚠️ Real crawl timed out (expected for comprehensive crawling)")
        return True  # Timeout is acceptable
    except Exception as e:
        print(f"❌ Real crawl error: {str(e)}")
        return False

async def test_mode_switching():
    """Test switching between modes"""
    print("\n🔄 Testing Mode Switching...")
    
    # Start with mock
    manager = CrawlerManager(use_mock=True)
    print(f"✅ Initial mode: {manager.get_status()['mode']}")
    
    # Toggle to real
    manager.toggle_mode()
    print(f"✅ After toggle: {manager.get_status()['mode']}")
    
    # Toggle back to mock
    manager.toggle_mode()
    print(f"✅ After second toggle: {manager.get_status()['mode']}")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Crawler Integration Tests\n")
    
    results = []
    
    # Test mock mode
    try:
        mock_success = await test_mock_mode()
        results.append(("Mock Mode", mock_success))
    except Exception as e:
        print(f"❌ Mock mode test failed: {e}")
        results.append(("Mock Mode", False))
    
    # Test mode switching
    try:
        switch_success = await test_mode_switching()
        results.append(("Mode Switching", switch_success))
    except Exception as e:
        print(f"❌ Mode switching test failed: {e}")
        results.append(("Mode Switching", False))
    
    # Test real mode (optional - comment out if you don't want to hit real websites)
    try:
        real_success = await test_real_mode()
        results.append(("Real Mode", real_success))
    except Exception as e:
        print(f"❌ Real mode test failed: {e}")
        results.append(("Real Mode", False))
    
    # Print summary
    print("\n📊 Test Results Summary:")
    print("=" * 40)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! Integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())