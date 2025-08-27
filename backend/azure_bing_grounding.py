"""
Azure Bing Search API Integration
Direct Bing Search API implementation (simplified from AI Projects SDK)
"""

import os
import asyncio
import requests
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class BingSearchResult:
    """Individual Bing search result"""
    title: str
    content: str
    url: str
    display_url: str
    
@dataclass 
class BingSearchResponse:
    """Complete Bing search response"""
    query: str
    results: List[BingSearchResult]
    total_results: int
    search_time: float
    success: bool
    error_message: str = ""

class AzureBingGrounding:
    """Direct Azure Bing Search API implementation"""
    
    def __init__(self):
        # Direct Bing Search API Configuration
        self.bing_search_key = os.getenv('BING_SEARCH_KEY', '')
        self.bing_search_endpoint = "https://api.bing.microsoft.com/v7.0/search"
        
        # Bing Search Configuration
        self.default_count = 5
        self.max_count = 10
        self.default_market = "en-US"
        self.default_freshness = None
        
        if self.bing_search_key:
            logging.info("🔍 Azure Bing Search API initialized successfully")
        else:
            logging.warning("🔍 Bing Search API key not found - search will be limited")
        
    async def web_search(self, query: str, count: int = None, market: str = None, freshness: str = None) -> BingSearchResponse:
        """
        Perform web search using Azure AI Foundry Bing Grounding
        
        Args:
            query: Search query string
            count: Number of results (default 5, max 10 for performance)
            market: Market code like 'en-US' 
            freshness: Time filter - 'Day', 'Week', 'Month'
        """
        import time
        start_time = time.time()
        
        if not self.bing_search_key:
            return BingSearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time,
                success=False,
                error_message="DEBUG: BING_SEARCH_KEY environment variable not set. Azure Bing Search API key required."
            )
        
        try:
            # Set search parameters
            search_params = {
                "q": query,
                "count": min(count or self.default_count, self.max_count),
                "mkt": market or self.default_market,
                "responseFilter": "Webpages"
            }
            
            if freshness:
                search_params["freshness"] = freshness
                
            logging.info(f"DEBUG: Direct Bing Search API call: query='{query}', endpoint='{self.bing_search_endpoint}', params={search_params}")
            
            # Headers for Bing Search API
            headers = {
                "Ocp-Apim-Subscription-Key": self.bing_search_key,
                "Content-Type": "application/json"
            }
            
            # Make direct API call to Bing Search
            response = requests.get(
                self.bing_search_endpoint,
                headers=headers,
                params=search_params,
                timeout=30
            )
            
            logging.info(f"DEBUG: Bing Search API response status: {response.status_code}")
            
            if response.status_code != 200:
                raise Exception(f"Bing Search API returned status {response.status_code}: {response.text}")
            
            search_data = response.json()
            
            # Extract webpages from response
            results = []
            if "webPages" in search_data and "value" in search_data["webPages"]:
                for result in search_data["webPages"]["value"]:
                    results.append(BingSearchResult(
                        title=result.get('name', ''),
                        content=result.get('snippet', ''),
                        url=result.get('url', ''),
                        display_url=result.get('displayUrl', '')
                    ))
            
            logging.info(f"DEBUG: Bing Search extracted {len(results)} results")
            
            search_time = time.time() - start_time
            
            return BingSearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                success=True
            )
            
        except Exception as e:
            search_time = time.time() - start_time
            logging.error(f"Azure Bing Search error for query '{query}': {type(e).__name__}: {e}")
            
            return BingSearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=search_time,
                success=False,
                error_message=f"Azure Bing Search failed: {type(e).__name__}: {e}"
            )
    
    async def grant_research(self, query: str) -> str:
        """Specialized grant research using Azure Bing Search"""
        enhanced_query = f"{query} grant funding opportunity foundation nonprofit"
        
        response = await self.web_search(enhanced_query, count=5, freshness="Month")
        
        if response.success and response.results:
            summary = f"🔍 AZURE BING GRANT RESEARCH for '{query}':\\n\\n"
            
            for i, result in enumerate(response.results, 1):
                summary += f"  {i}. {result.title}\\n"
                if result.content:
                    snippet = result.content[:200] + "..." if len(result.content) > 200 else result.content
                    summary += f"     {snippet}\\n"
                summary += f"     {result.url}\\n\\n"
            
            summary += f"🔍 SOURCE: Azure AI Foundry Bing Search Grounding\\n"
            summary += f"⏱️  SEARCH TIME: {response.search_time:.2f}s\\n"
            summary += f"📊 RESULTS: {response.total_results} results\\n"
            summary += f"🔒 RELIABILITY: Enterprise Azure hosting\\n"
            
            return summary
        else:
            return f"ERROR: Azure Bing grant research failed for query '{query}'. Response success={response.success}, total_results={response.total_results}, search_time={response.search_time}s, error_message='{response.error_message}'"
    
    async def funder_research(self, funder_name: str) -> str:
        """Research specific funders using Azure Bing Search"""
        query = f"{funder_name} foundation grants funding priorities recent awards"
        
        response = await self.web_search(query, count=5, freshness="Month")
        
        if response.success and response.results:
            summary = f"🏢 AZURE BING FUNDER RESEARCH for '{funder_name}':\\n\\n"
            
            for i, result in enumerate(response.results, 1):
                summary += f"  {i}. {result.title}\\n"
                if result.content:
                    snippet = result.content[:250] + "..." if len(result.content) > 250 else result.content
                    summary += f"     {snippet}\\n"
                summary += f"     {result.url}\\n\\n"
            
            summary += f"🔍 SOURCE: Azure AI Foundry Bing Search\\n"
            summary += f"📊 RESULTS: {response.total_results} funder intelligence results\\n"
            summary += f"🔒 RELIABILITY: Enterprise-grade search\\n"
            
            return summary
        else:
            return f"ERROR: Azure Bing funder research failed for funder '{funder_name}'. Response success={response.success}, total_results={response.total_results}, search_time={response.search_time}s, error_message='{response.error_message}'"
    
    async def competitive_analysis(self, organization_type: str, focus_area: str = "") -> str:
        """Research competitive landscape using Azure Bing Search"""
        if focus_area:
            query = f"{organization_type} {focus_area} nonprofits grants funding competitive analysis"
        else:
            query = f"{organization_type} nonprofits grants funding competitive landscape"
        
        response = await self.web_search(query, count=6, freshness="Month")
        
        if response.success and response.results:
            summary = f"🏆 AZURE BING COMPETITIVE ANALYSIS for '{organization_type}' organizations:\\n\\n"
            
            for i, result in enumerate(response.results, 1):
                summary += f"  {i}. {result.title}\\n"
                if result.content:
                    snippet = result.content[:200] + "..." if len(result.content) > 200 else result.content
                    summary += f"     {snippet}\\n"
                summary += f"     {result.url}\\n\\n"
            
            summary += f"🔍 SOURCE: Azure AI Foundry Bing Grounding\\n"
            summary += f"📈 ANALYSIS: Real-time competitive intelligence\\n"
            summary += f"🔒 RELIABILITY: Enterprise Azure search\\n"
            
            return summary
        else:
            return f"ERROR: Azure Bing competitive analysis failed for organization_type '{organization_type}'. Response success={response.success}, total_results={response.total_results}, search_time={response.search_time}s, error_message='{response.error_message}'"

# Global instance for easy import
azure_bing_grounding = AzureBingGrounding()