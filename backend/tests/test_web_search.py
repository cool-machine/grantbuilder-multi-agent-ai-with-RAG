import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the parent directory to the path to import the module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from MultiAgentFramework import MultiAgentOrchestrator


class TestMultiTierWebSearch:
    """Test multi-tier web search with quota exhaustion scenarios"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a MultiAgentOrchestrator instance for testing"""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.user_context = {
            "ngo_profile": {"organization_name": "Test NGO"},
            "grant_context": {"title": "Test Grant"}
        }
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_google_search_success(self, orchestrator):
        """Test successful Google search (first tier)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Test Result 1",
                    "snippet": "Test snippet 1",
                    "link": "https://example1.com"
                },
                {
                    "title": "Test Result 2", 
                    "snippet": "Test snippet 2",
                    "link": "https://example2.com"
                }
            ]
        }
        
        with patch('requests.get', return_value=mock_response):
            with patch.dict(os.environ, {
                'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key',
                'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx_id'
            }):
                result = await orchestrator._perform_web_search("test query")
                
                assert "🔍 GOOGLE SEARCH RESULTS" in result
                assert "Test Result 1" in result
                assert "Test snippet 1" in result
                assert "https://example1.com" in result
                assert "🔍 SOURCE: Google Custom Search API" in result
    
    @pytest.mark.asyncio
    async def test_google_quota_exhausted_fallback_to_bing(self, orchestrator):
        """Test Google quota exhausted, fallback to Bing"""
        # Mock Google API quota exceeded (403)
        google_response = Mock()
        google_response.status_code = 403
        
        # Mock successful Bing response
        bing_response = Mock()
        bing_response.status_code = 200
        bing_response.json.return_value = {
            "webPages": {
                "value": [
                    {
                        "name": "Bing Result 1",
                        "snippet": "Bing snippet 1", 
                        "url": "https://bing1.com"
                    }
                ]
            }
        }
        
        def mock_requests_get(url, *args, **kwargs):
            if "googleapis.com" in url:
                return google_response
            elif "api.bing.microsoft.com" in url:
                return bing_response
            else:
                return Mock(status_code=404)
        
        with patch('requests.get', side_effect=mock_requests_get):
            with patch.dict(os.environ, {
                'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key',
                'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx_id',
                'BING_SEARCH_KEY': 'test_bing_key'
            }):
                result = await orchestrator._perform_web_search("test query")
                
                assert "🔍 BING SEARCH RESULTS" in result
                assert "Bing Result 1" in result
                assert "Bing snippet 1" in result
                assert "🔍 SOURCE: Bing Web Search API" in result
    
    @pytest.mark.asyncio
    async def test_google_bing_exhausted_fallback_to_brave(self, orchestrator):
        """Test Google and Bing quotas exhausted, fallback to Brave"""
        # Mock Google API quota exceeded
        google_response = Mock()
        google_response.status_code = 403
        
        # Mock Bing API quota exceeded
        bing_response = Mock()
        bing_response.status_code = 403
        
        # Mock successful Brave response
        brave_response = Mock()
        brave_response.status_code = 200
        brave_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "title": "Brave Result 1",
                        "description": "Brave description 1",
                        "url": "https://brave1.com"
                    }
                ]
            }
        }
        
        def mock_requests_get(url, *args, **kwargs):
            if "googleapis.com" in url:
                return google_response
            elif "api.bing.microsoft.com" in url:
                return bing_response
            elif "api.search.brave.com" in url:
                return brave_response
            else:
                return Mock(status_code=404)
        
        with patch('requests.get', side_effect=mock_requests_get):
            with patch.dict(os.environ, {
                'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key',
                'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx_id',
                'BING_SEARCH_KEY': 'test_bing_key',
                'BRAVE_SEARCH_API_KEY': 'test_brave_key'
            }):
                result = await orchestrator._perform_web_search("test query")
                
                assert "🔍 BRAVE SEARCH RESULTS" in result
                assert "Brave Result 1" in result
                assert "Brave description 1" in result
                assert "🔍 SOURCE: Brave Search API" in result
    
    @pytest.mark.asyncio
    async def test_all_apis_exhausted_fallback_to_intelligence(self, orchestrator):
        """Test all APIs exhausted, fallback to intelligent analysis"""
        # Mock all APIs as quota exceeded
        quota_response = Mock()
        quota_response.status_code = 403
        
        def mock_requests_get(url, *args, **kwargs):
            return quota_response
        
        with patch('requests.get', side_effect=mock_requests_get):
            with patch.dict(os.environ, {
                'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google_key',
                'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx_id',
                'BING_SEARCH_KEY': 'test_bing_key',
                'BRAVE_SEARCH_API_KEY': 'test_brave_key'
            }):
                result = await orchestrator._perform_web_search("salary research for nonprofit")
                
                assert "🔍 INTELLIGENT RESEARCH ANALYSIS" in result
                assert "💰 SALARY RESEARCH" in result
                assert "National average for related roles" in result
                assert "🔍 SOURCE: Knowledge synthesis (APIs unavailable)" in result
    
    @pytest.mark.asyncio
    async def test_google_search_different_query_types(self, orchestrator):
        """Test fallback intelligence for different query types"""
        # Mock all APIs as unavailable
        error_response = Mock()
        error_response.status_code = 500
        
        with patch('requests.get', return_value=error_response):
            # Test salary query
            salary_result = await orchestrator._perform_web_search("professional salary research")
            assert "💰 SALARY RESEARCH" in salary_result
            assert "National average for related roles: $45,000-75,000" in salary_result
            
            # Test funding query
            funding_result = await orchestrator._perform_web_search("foundation grant funding patterns")
            assert "📊 FUNDING LANDSCAPE ANALYSIS" in funding_result
            assert "Foundation grants typically range $10K-$500K" in funding_result
            
            # Test organization query
            org_result = await orchestrator._perform_web_search("nonprofit organization competitive analysis")
            assert "🏢 COMPETITIVE LANDSCAPE" in org_result
            assert "1.5M+ nonprofits compete for foundation funding" in org_result
            
            # Test budget query
            budget_result = await orchestrator._perform_web_search("budget allocation best practices")
            assert "💼 BUDGET BEST PRACTICES" in budget_result
            assert "Personnel costs: typically 65-75%" in budget_result
    
    @pytest.mark.asyncio
    async def test_api_credentials_missing(self, orchestrator):
        """Test behavior when API credentials are missing"""
        with patch.dict(os.environ, {}, clear=True):
            result = await orchestrator._perform_web_search("test query")
            
            # Should fallback to intelligent analysis when no credentials
            assert "🔍 INTELLIGENT RESEARCH ANALYSIS" in result
            assert "🔍 SOURCE: Knowledge synthesis (APIs unavailable)" in result
    
    @pytest.mark.asyncio
    async def test_google_api_invalid_credentials(self, orchestrator):
        """Test Google API with invalid credentials"""
        invalid_response = Mock()
        invalid_response.status_code = 400
        invalid_response.text = "API key not valid"
        
        with patch('requests.get', return_value=invalid_response):
            with patch.dict(os.environ, {
                'GOOGLE_CUSTOM_SEARCH_KEY': 'invalid_key',
                'GOOGLE_CUSTOM_SEARCH_CX': 'invalid_cx'
            }):
                result = await orchestrator._perform_web_search("test query")
                
                # Should contain error information or fallback
                assert ("🔍 SEARCH ERROR" in result or 
                        "🔍 INTELLIGENT RESEARCH ANALYSIS" in result)
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, orchestrator):
        """Test network timeout handling"""
        import requests
        
        def mock_timeout(*args, **kwargs):
            raise requests.exceptions.Timeout("Request timed out")
        
        with patch('requests.get', side_effect=mock_timeout):
            with patch.dict(os.environ, {
                'GOOGLE_CUSTOM_SEARCH_KEY': 'test_key',
                'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx'
            }):
                result = await orchestrator._perform_web_search("test query")
                
                # Should handle timeout gracefully and provide fallback
                assert ("🔍 SEARCH ERROR" in result or 
                        "🔍 INTELLIGENT RESEARCH ANALYSIS" in result)
    
    @pytest.mark.asyncio
    async def test_search_tier_priority(self, orchestrator):
        """Test that search APIs are tried in correct order: Google → Bing → Brave → Fallback"""
        call_order = []
        
        def mock_requests_get(url, *args, **kwargs):
            if "googleapis.com" in url:
                call_order.append("google")
                response = Mock()
                response.status_code = 403  # Quota exceeded
                return response
            elif "api.bing.microsoft.com" in url:
                call_order.append("bing")
                response = Mock()
                response.status_code = 403  # Quota exceeded
                return response
            elif "api.search.brave.com" in url:
                call_order.append("brave")
                response = Mock()
                response.status_code = 200
                response.json.return_value = {
                    "web": {"results": [{"title": "Test", "description": "Test", "url": "test.com"}]}
                }
                return response
        
        with patch('requests.get', side_effect=mock_requests_get):
            with patch.dict(os.environ, {
                'GOOGLE_CUSTOM_SEARCH_KEY': 'test_google',
                'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx',
                'BING_SEARCH_KEY': 'test_bing',
                'BRAVE_SEARCH_API_KEY': 'test_brave'
            }):
                result = await orchestrator._perform_web_search("test query")
                
                # Verify correct order: Google tried first, then Bing, then Brave succeeded
                assert call_order == ["google", "bing", "brave"]
                assert "🔍 BRAVE SEARCH RESULTS" in result
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, orchestrator):
        """Test handling of empty search results from APIs"""
        empty_response = Mock()
        empty_response.status_code = 200
        empty_response.json.return_value = {}  # Empty results
        
        with patch('requests.get', return_value=empty_response):
            with patch.dict(os.environ, {
                'GOOGLE_CUSTOM_SEARCH_KEY': 'test_key',
                'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx'
            }):
                result = await orchestrator._perform_web_search("test query")
                
                assert "🔍 GOOGLE SEARCH RESULTS" in result
                assert "No specific results found" in result
    
    def test_sync_search_wrapper(self, orchestrator):
        """Test that the search can be called from synchronous context"""
        async def run_test():
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "items": [{"title": "Test", "snippet": "Test", "link": "test.com"}]
            }
            
            with patch('requests.get', return_value=mock_response):
                with patch.dict(os.environ, {
                    'GOOGLE_CUSTOM_SEARCH_KEY': 'test_key',
                    'GOOGLE_CUSTOM_SEARCH_CX': 'test_cx'
                }):
                    result = await orchestrator._perform_web_search("test")
                    return result
        
        # Run async function in event loop
        result = asyncio.run(run_test())
        assert "🔍 GOOGLE SEARCH RESULTS" in result


if __name__ == "__main__":
    # Run tests with: python -m pytest test_web_search.py -v
    pytest.main([__file__, "-v"])