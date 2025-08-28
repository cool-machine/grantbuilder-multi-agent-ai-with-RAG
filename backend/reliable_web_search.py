"""
Reliable Web Search API Integration
Google Custom Search (primary) with Brave Search (fallback)
Replaces unreliable Azure Bing Search Grounding due to subscription restrictions
"""

import os
import asyncio
import requests
import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class WebSearchResult:
    """Individual web search result"""
    title: str
    content: str
    url: str
    display_url: str
    source: str = ""  # Google, Brave, etc.
    
@dataclass 
class WebSearchResponse:
    """Complete web search response"""
    query: str
    results: List[WebSearchResult]
    total_results: int
    search_time: float
    success: bool
    error_message: str = ""
    source_used: str = ""  # Which API was used (Google/Brave)
    requests_made: int = 0  # Number of API requests made
    quota_usage: str = ""  # Usage info (e.g., "Google: 15/100 today, Brave: 5/2000 month")

class ReliableWebSearch:
    """Google Custom Search (primary) with Brave Search (fallback) implementation"""
    
    def __init__(self):
        # Google Custom Search Configuration
        self.google_api_key = os.getenv('GOOGLE_CUSTOM_SEARCH_KEY', '')
        self.google_cx = os.getenv('GOOGLE_CUSTOM_SEARCH_CX', '')
        self.google_endpoint = "https://www.googleapis.com/customsearch/v1"
        
        # Brave Search Configuration  
        self.brave_api_key = os.getenv('BRAVE_SEARCH_API_KEY', '')
        self.brave_endpoint = "https://api.search.brave.com/res/v1/web/search"
        
        # Search Configuration
        self.default_count = 5
        self.max_count = 10
        
        # Request tracking (simple in-memory - resets on restart)
        self.google_requests_today = 0
        self.brave_requests_month = 0
        
        # Log initialization status with quota info
        if self.google_api_key and self.google_cx:
            logging.info("🔍 Google Custom Search initialized (FREE: 100/day)")
        else:
            logging.warning("⚠️ Google Custom Search not configured")
            
        if self.brave_api_key:
            logging.info("🦁 Brave Search initialized (FREE: 2,000/month)")
        else:
            logging.warning("⚠️ Brave Search not configured")
            
        if not (self.google_api_key and self.google_cx) and not self.brave_api_key:
            logging.error("❌ No web search APIs configured - will return empty results")
        
    async def web_search(self, query: str, count: int = None, market: str = None, freshness: str = None) -> WebSearchResponse:
        """
        Perform web search using Google Custom Search (primary) with Brave Search (fallback)
        
        Args:
            query: Search query string
            count: Number of results (default 5, max 10)
            market: Market/language preference (e.g., 'en-US')
            freshness: Time filter - 'Day', 'Week', 'Month' (Google only)
        """
        start_time = time.time()
        count = min(count or self.default_count, self.max_count)
        
        # Try Google Custom Search first
        if self.google_api_key and self.google_cx:
            try:
                logging.info(f"🔍 Trying Google Custom Search for: '{query}'")
                result = await self._google_search(query, count, market, freshness)
                if result.success:
                    result.source_used = "Google Custom Search"
                    result.requests_made = 1
                    result.quota_usage = self._get_quota_usage()
                    logging.info(f"✅ Google search succeeded: {result.total_results} results in {result.search_time:.2f}s")
                    return result
                else:
                    logging.warning(f"⚠️ Google search failed: {result.error_message}")
            except Exception as e:
                logging.error(f"❌ Google search exception: {e}")
        
        # Fallback to Brave Search
        if self.brave_api_key:
            try:
                logging.info(f"🦁 Falling back to Brave Search for: '{query}'")
                result = await self._brave_search(query, count, market)
                if result.success:
                    result.source_used = "Brave Search (fallback)"
                    result.requests_made = 1
                    result.quota_usage = self._get_quota_usage()
                    logging.info(f"✅ Brave search succeeded: {result.total_results} results in {result.search_time:.2f}s")
                    return result
                else:
                    logging.warning(f"⚠️ Brave search failed: {result.error_message}")
            except Exception as e:
                logging.error(f"❌ Brave search exception: {e}")
        
        # Both failed or not configured
        search_time = time.time() - start_time
        return WebSearchResponse(
            query=query,
            results=[],
            total_results=0,
            search_time=search_time,
            success=False,
            error_message="DEBUG: No web search APIs available. Both Google Custom Search and Brave Search failed or not configured.",
            source_used="none",
            requests_made=0,
            quota_usage=self._get_quota_usage()
        )
    
    async def _google_search(self, query: str, count: int, market: str = None, freshness: str = None) -> WebSearchResponse:
        """Perform Google Custom Search"""
        start_time = time.time()
        
        try:
            # Build search parameters
            params = {
                'key': self.google_api_key,
                'cx': self.google_cx,
                'q': query,
                'num': count,
                'safe': 'medium'
            }
            
            # Add language/market if specified
            if market:
                params['lr'] = f'lang_{market.split("-")[0]}'
                params['gl'] = market.split("-")[1] if "-" in market else market
            
            # Add date restriction if freshness specified
            if freshness:
                date_restrict = {
                    'Day': 'd1',
                    'Week': 'w1', 
                    'Month': 'm1'
                }.get(freshness)
                if date_restrict:
                    params['dateRestrict'] = date_restrict
            
            logging.info(f"DEBUG: Google Custom Search API call: {params['q']}, num={params['num']}")
            
            # Make API request
            response = requests.get(self.google_endpoint, params=params, timeout=30)
            self.google_requests_today += 1
            
            logging.info(f"DEBUG: Google API response status: {response.status_code}")
            
            if response.status_code != 200:
                raise Exception(f"Google API returned status {response.status_code}: {response.text}")
            
            data = response.json()
            
            # Parse results
            results = []
            if 'items' in data:
                for item in data['items']:
                    results.append(WebSearchResult(
                        title=item.get('title', ''),
                        content=item.get('snippet', ''),
                        url=item.get('link', ''),
                        display_url=item.get('displayLink', ''),
                        source="Google"
                    ))
            
            search_time = time.time() - start_time
            
            return WebSearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                success=True,
                source_used="Google Custom Search"
            )
            
        except Exception as e:
            search_time = time.time() - start_time
            logging.error(f"DEBUG: Google Custom Search failed: {e}")
            
            return WebSearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=search_time,
                success=False,
                error_message=f"DEBUG: Google Custom Search failed: {e}"
            )
    
    async def _brave_search(self, query: str, count: int, market: str = None) -> WebSearchResponse:
        """Perform Brave Search"""
        start_time = time.time()
        
        try:
            # Build search parameters
            params = {
                'q': query,
                'count': count
            }
            
            # Add market/country if specified
            if market:
                if "-" in market:
                    params['country'] = market.split("-")[1].upper()
                params['search_lang'] = market.split("-")[0] if "-" in market else market
            
            # Headers for Brave Search API
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': self.brave_api_key
            }
            
            logging.info(f"DEBUG: Brave Search API call: {params['q']}, count={params['count']}")
            
            # Make API request
            response = requests.get(self.brave_endpoint, params=params, headers=headers, timeout=30)
            self.brave_requests_month += 1
            
            logging.info(f"DEBUG: Brave API response status: {response.status_code}")
            
            if response.status_code != 200:
                raise Exception(f"Brave API returned status {response.status_code}: {response.text}")
            
            data = response.json()
            
            # Parse results
            results = []
            if 'web' in data and 'results' in data['web']:
                for item in data['web']['results']:
                    results.append(WebSearchResult(
                        title=item.get('title', ''),
                        content=item.get('description', ''),
                        url=item.get('url', ''),
                        display_url=item.get('url', '').replace('https://', '').replace('http://', ''),
                        source="Brave"
                    ))
            
            search_time = time.time() - start_time
            
            return WebSearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                success=True,
                source_used="Brave Search"
            )
            
        except Exception as e:
            search_time = time.time() - start_time
            logging.error(f"DEBUG: Brave Search failed: {e}")
            
            return WebSearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=search_time,
                success=False,
                error_message=f"DEBUG: Brave Search failed: {e}"
            )
    
    def _get_quota_usage(self) -> str:
        """Get quota usage information"""
        google_quota = f"Google: {self.google_requests_today}/100 today" if (self.google_api_key and self.google_cx) else "Google: not configured"
        brave_quota = f"Brave: {self.brave_requests_month}/2000 month" if self.brave_api_key else "Brave: not configured"
        return f"{google_quota}, {brave_quota}"
    
    async def grant_research(self, query: str) -> str:
        """Specialized grant research using reliable web search"""
        enhanced_query = f"{query} grant funding opportunity foundation nonprofit"
        
        response = await self.web_search(enhanced_query, count=5, freshness="Month")
        
        if response.success and response.results:
            summary = f"🔍 RELIABLE WEB SEARCH GRANT RESEARCH for '{query}':\\n\\n"
            
            for i, result in enumerate(response.results, 1):
                summary += f"  {i}. {result.title}\\n"
                if result.content:
                    snippet = result.content[:200] + "..." if len(result.content) > 200 else result.content
                    summary += f"     {snippet}\\n"
                summary += f"     {result.url}\\n\\n"
            
            summary += f"🔍 SOURCE: {response.source_used}\\n"
            summary += f"⏱️  SEARCH TIME: {response.search_time:.2f}s\\n"
            summary += f"📊 RESULTS: {response.total_results} results\\n"
            summary += f"📈 REQUESTS: {response.requests_made}\\n"
            summary += f"📊 QUOTA: {response.quota_usage}\\n"
            summary += f"🔒 RELIABILITY: Direct API access (99%+ uptime)\\n"
            
            return summary
        else:
            return f"ERROR: Reliable web search grant research failed for query '{query}'. Response success={response.success}, total_results={response.total_results}, search_time={response.search_time}s, source_used={response.source_used}, error_message='{response.error_message}'"

# Global instance for easy import (backward compatibility)
reliable_web_search = ReliableWebSearch()

# Export global instance for easy import
__all__ = ['ReliableWebSearch', 'WebSearchResult', 'WebSearchResponse', 'reliable_web_search']