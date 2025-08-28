"""
Comprehensive Tests for Reliable Web Search (Google Custom Search + Brave Search)
Tests both success and failure scenarios, quota tracking, and source attribution
"""

import asyncio
import json
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import requests
from reliable_web_search import ReliableWebSearch, WebSearchResult, WebSearchResponse

class TestReliableWebSearch:
    """Test suite for ReliableWebSearch class"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock environment variables
        self.mock_env = {
            'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key',
            'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx',
            'BRAVE_SEARCH_API_KEY': 'test_brave_key'
        }
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    def test_initialization_success(self):
        """Test successful initialization with all API keys"""
        search = ReliableWebSearch()
        
        assert search.google_api_key == 'test_google_key'
        assert search.google_cx == 'test_google_cx'
        assert search.brave_api_key == 'test_brave_key'
        assert search.default_count == 5
        assert search.max_count == 10
        assert search.google_requests_today == 0
        assert search.brave_requests_month == 0
        
    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_no_keys(self):
        """Test initialization with no API keys configured"""
        search = ReliableWebSearch()
        
        assert search.google_api_key == ''
        assert search.google_cx == ''
        assert search.brave_api_key == ''
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_google_search_success(self, mock_get):
        """Test successful Google Custom Search"""
        # Mock successful Google API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'title': 'Test Result 1',
                    'snippet': 'This is a test result',
                    'link': 'https://example.com/1',
                    'displayLink': 'example.com'
                },
                {
                    'title': 'Test Result 2', 
                    'snippet': 'This is another test result',
                    'link': 'https://example.com/2',
                    'displayLink': 'example.com'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        search = ReliableWebSearch()
        result = await search.web_search("test query", count=2)
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'q' in call_args[1]['params']
        assert call_args[1]['params']['q'] == 'test query'
        assert call_args[1]['params']['num'] == 2
        
        # Verify response
        assert result.success == True
        assert result.source_used == "Google Custom Search"
        assert result.total_results == 2
        assert len(result.results) == 2
        assert result.results[0].title == "Test Result 1"
        assert result.results[0].source == "Google"
        assert result.requests_made == 1
        assert "Google: 1/100 today" in result.quota_usage
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_google_search_failure_brave_fallback(self, mock_get):
        """Test Google failure with successful Brave fallback"""
        # Mock Google failure, then Brave success
        google_response = MagicMock()
        google_response.status_code = 429  # Rate limited
        google_response.text = "Rate limit exceeded"
        
        brave_response = MagicMock()
        brave_response.status_code = 200
        brave_response.json.return_value = {
            'web': {
                'results': [
                    {
                        'title': 'Brave Result 1',
                        'description': 'This is a Brave search result',
                        'url': 'https://brave-example.com/1'
                    }
                ]
            }
        }
        
        mock_get.side_effect = [google_response, brave_response]
        
        search = ReliableWebSearch()
        result = await search.web_search("test query", count=3)
        
        # Verify both APIs were called
        assert mock_get.call_count == 2
        
        # Verify Brave fallback worked
        assert result.success == True
        assert result.source_used == "Brave Search (fallback)"
        assert result.total_results == 1
        assert result.results[0].title == "Brave Result 1"
        assert result.results[0].source == "Brave"
        assert result.requests_made == 1
        assert "Brave: 1/2000 month" in result.quota_usage
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_both_apis_fail(self, mock_get):
        """Test both Google and Brave APIs failing"""
        # Mock both APIs failing
        failure_response = MagicMock()
        failure_response.status_code = 500
        failure_response.text = "Internal Server Error"
        
        mock_get.return_value = failure_response
        
        search = ReliableWebSearch()
        result = await search.web_search("test query")
        
        # Verify both APIs were attempted
        assert mock_get.call_count == 2
        
        # Verify failure response
        assert result.success == False
        assert result.source_used == "none"
        assert result.total_results == 0
        assert len(result.results) == 0
        assert "No web search APIs available" in result.error_message
        assert result.requests_made == 0
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_brave_search_success(self, mock_get):
        """Test successful Brave Search"""
        # Mock Google failure to force Brave usage
        google_response = MagicMock()
        google_response.status_code = 403
        
        brave_response = MagicMock()
        brave_response.status_code = 200
        brave_response.json.return_value = {
            'web': {
                'results': [
                    {
                        'title': 'Brave Grant Result',
                        'description': 'Foundation grants for nonprofit organizations',
                        'url': 'https://foundation.org/grants'
                    },
                    {
                        'title': 'Funding Opportunities',
                        'description': 'Latest funding opportunities for NGOs',
                        'url': 'https://funding.gov/opportunities'
                    }
                ]
            }
        }
        
        mock_get.side_effect = [google_response, brave_response]
        
        search = ReliableWebSearch()
        result = await search.web_search("nonprofit grants", count=5)
        
        # Verify Brave API was called with correct parameters
        brave_call = mock_get.call_args_list[1]
        assert 'count' in brave_call[1]['params']
        assert brave_call[1]['params']['q'] == 'nonprofit grants'
        assert brave_call[1]['params']['count'] == 5
        assert 'X-Subscription-Token' in brave_call[1]['headers']
        
        # Verify response
        assert result.success == True
        assert result.source_used == "Brave Search (fallback)"
        assert result.total_results == 2
        assert result.results[0].title == "Brave Grant Result"
        assert result.results[1].url == "https://funding.gov/opportunities"
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_market_and_freshness_parameters(self, mock_get):
        """Test market and freshness parameter handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response
        
        search = ReliableWebSearch()
        result = await search.web_search("test query", market="en-US", freshness="Week")
        
        # Verify parameters were passed correctly
        call_args = mock_get.call_args[1]['params']
        assert 'lr' in call_args
        assert call_args['lr'] == 'lang_en'
        assert 'gl' in call_args
        assert call_args['gl'] == 'US'
        assert 'dateRestrict' in call_args
        assert call_args['dateRestrict'] == 'w1'
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_grant_research_success(self, mock_get):
        """Test specialized grant research function"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'title': 'Environmental Grant Program',
                    'snippet': 'This foundation provides grants for environmental conservation projects across the United States.',
                    'link': 'https://envfoundation.org/grants',
                    'displayLink': 'envfoundation.org'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        search = ReliableWebSearch()
        result = await search.grant_research("environmental conservation")
        
        # Verify enhanced query was used
        call_args = mock_get.call_args[1]['params']
        assert "grant funding opportunity foundation nonprofit" in call_args['q']
        assert "environmental conservation" in call_args['q']
        
        # Verify summary format
        assert "🔍 RELIABLE WEB SEARCH GRANT RESEARCH" in result
        assert "Environmental Grant Program" in result
        assert "https://envfoundation.org/grants" in result
        assert "Google Custom Search" in result
        assert "RELIABILITY: Direct API access" in result
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_quota_tracking(self, mock_get):
        """Test quota usage tracking functionality"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response
        
        search = ReliableWebSearch()
        
        # Make multiple requests
        await search.web_search("query 1")
        await search.web_search("query 2")
        await search.web_search("query 3")
        
        # Check quota tracking
        quota_info = search._get_quota_usage()
        assert "Google: 3/100 today" in quota_info
        assert search.google_requests_today == 3
        
    @patch.dict(os.environ, {}, clear=True)
    @pytest.mark.asyncio
    async def test_no_apis_configured(self):
        """Test behavior when no APIs are configured"""
        search = ReliableWebSearch()
        result = await search.web_search("test query")
        
        assert result.success == False
        assert result.source_used == "none"
        assert result.total_results == 0
        assert "No web search APIs available" in result.error_message
        assert "Google: not configured" in result.quota_usage
        assert "Brave: not configured" in result.quota_usage
        
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_request_timeout_handling(self, mock_get):
        """Test timeout handling for API requests"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        search = ReliableWebSearch()
        result = await search.web_search("test query")
        
        # Should try both APIs and fail
        assert mock_get.call_count == 2
        assert result.success == False
        assert "Request timed out" in result.error_message or "Timeout" in result.error_message
        
    def test_count_parameter_limits(self):
        """Test count parameter is properly limited"""
        search = ReliableWebSearch()
        
        # Test default count
        assert search.default_count == 5
        assert search.max_count == 10
        
        # Count should be limited to max_count
        with patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test', 'GOOGLE_CUSTOM_SEARCH_CX': 'test'}):
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'items': []}
                mock_get.return_value = mock_response
                
                # Test count > max_count gets limited
                asyncio.run(search.web_search("test", count=20))
                call_args = mock_get.call_args[1]['params']
                assert call_args['num'] == 10  # Should be limited to max_count


# Performance and integration tests
class TestWebSearchIntegration:
    """Integration tests for web search functionality"""
    
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @pytest.mark.asyncio
    async def test_response_time_tracking(self):
        """Test that search time is properly tracked"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'items': []}
            mock_get.return_value = mock_response
            
            search = ReliableWebSearch()
            result = await search.web_search("test query")
            
            # Verify search time was tracked
            assert result.search_time > 0
            assert isinstance(result.search_time, float)
            
    @patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_google_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave_key'})
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent search requests"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'items': []}
            mock_get.return_value = mock_response
            
            search = ReliableWebSearch()
            
            # Make concurrent requests
            tasks = [
                search.web_search("query 1"),
                search.web_search("query 2"), 
                search.web_search("query 3")
            ]
            results = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for result in results:
                assert result.success == True
            
            # Should have made 3 Google API calls
            assert mock_get.call_count == 3
            assert search.google_requests_today == 3


if __name__ == "__main__":
    # Run basic functionality test
    import sys
    print("🧪 Running basic web search functionality tests...")
    
    # Test initialization
    with patch.dict(os.environ, {'GOOGLE_CUSTOM_SEARCH_KEY': 'test_key', 'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx', 'BRAVE_SEARCH_API_KEY': 'test_brave'}):
        search = ReliableWebSearch()
        print(f"✅ Initialization test passed")
        print(f"   - Google API: {'✅ Configured' if search.google_api_key else '❌ Missing'}")
        print(f"   - Brave API: {'✅ Configured' if search.brave_api_key else '❌ Missing'}")
        print(f"   - Quota tracking: Google={search.google_requests_today}/100, Brave={search.brave_requests_month}/2000")
    
    print("\n🚀 To run full test suite:")
    print("   pip install pytest pytest-asyncio")
    print("   pytest test_reliable_web_search.py -v")
    
    print("\n📊 Test Coverage:")
    print("   ✅ Google Custom Search success/failure scenarios")
    print("   ✅ Brave Search fallback functionality")  
    print("   ✅ Quota tracking and request counting")
    print("   ✅ Error handling and timeout scenarios")
    print("   ✅ Market/freshness parameter handling")
    print("   ✅ Grant research specialized functionality")
    print("   ✅ Concurrent request handling")
    print("   ✅ API configuration validation")