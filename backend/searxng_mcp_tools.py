"""
SearXNG MCP Tools - Privacy-respecting web search for multi-agent systems
No API keys required - uses public SearXNG instances with fallback rotation
"""

import asyncio
import requests
import random
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class SearchResult:
    """Individual search result"""
    title: str
    content: str
    url: str
    engine: str = ""
    
@dataclass 
class SearchResponse:
    """Complete search response from SearXNG"""
    query: str
    results: List[SearchResult]
    total_results: int
    instance_used: str
    engines_used: List[str]
    search_time: float
    success: bool
    error_message: str = ""

class SearXNGMCPTools:
    """SearXNG-powered MCP tools for web search and research"""
    
    def __init__(self):
        # Curated list of reliable SearXNG instances (updated 2025)
        self.searxng_instances = [
            "https://searxng.site",
            "https://search.sapti.me", 
            "https://searx.be",
            "https://searx.tiekoetter.com",
            "https://search.bus-hit.me",
            "https://searx.prvcy.eu",
            "https://search.davidovski.xyz",
            "https://searx.work",
            "https://searx.fmac.xyz",
            "https://northboot.xyz",
            "https://opnxng.com",
            "https://searx.neocities.org",
            "https://searx.moonboot.org",
            "https://search.rhscz.eu",
            "https://searx.org"
        ]
        
        self.default_engines = "google,bing,duckduckgo,startpage"
        self.default_timeout = 15
        self.max_retries = 3
        
        logging.info("🔍 SearXNG MCP Tools initialized")
        logging.info(f"   Available instances: {len(self.searxng_instances)}")
        logging.info(f"   Default engines: {self.default_engines}")
    
    async def web_search(self, query: str, engines: str = None, category: str = "general") -> SearchResponse:
        """Perform web search using SearXNG metasearch engine"""
        start_time = asyncio.get_event_loop().time()
        
        engines = engines or self.default_engines
        
        for attempt in range(self.max_retries):
            try:
                # Random instance selection for load balancing
                instance = random.choice(self.searxng_instances)
                search_url = f"{instance}/search"
                
                params = {
                    "q": query,
                    "format": "json",
                    "engines": engines,
                    "categories": category,
                    "language": "en",
                    "time_range": "",
                    "safesearch": "1"
                }
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; GrantSeekerAI/1.0; +https://grantseeker.ai)",
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.9"
                }
                
                response = requests.get(
                    search_url,
                    params=params,
                    headers=headers,
                    timeout=self.default_timeout,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        results = []
                        
                        logging.info(f"SearXNG {instance} returned {len(data.get('results', []))} results for query '{query}'")
                        
                        if "results" in data and data["results"]:
                            for result_data in data["results"]:
                                result = SearchResult(
                                    title=result_data.get("title", "").strip(),
                                    content=result_data.get("content", "").strip(),
                                    url=result_data.get("url", "").strip(),
                                    engine=result_data.get("engine", "unknown")
                                )
                                if result.title and result.url:
                                    results.append(result)
                        
                        search_time = asyncio.get_event_loop().time() - start_time
                        
                        return SearchResponse(
                            query=query,
                            results=results,
                            total_results=len(results),
                            instance_used=instance,
                            engines_used=engines.split(","),
                            search_time=search_time,
                            success=True
                        )
                        
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON decode error from {instance}: {e}. Response text: {response.text[:200]}")
                        continue
                        
                else:
                    logging.error(f"HTTP {response.status_code} from {instance}. Response headers: {dict(response.headers)}. Response text: {response.text[:200]}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed to {instance}: {type(e).__name__}: {e}. URL: {search_url}?{params}")
                continue
        
        # All attempts failed
        search_time = asyncio.get_event_loop().time() - start_time
        return SearchResponse(
            query=query,
            results=[],
            total_results=0,
            instance_used="none",
            engines_used=[],
            search_time=search_time,
            success=False,
            error_message=f"HTTP failures on all {self.max_retries} attempts across instances {self.searxng_instances[:self.max_retries]}. Check logs for specific HTTP status codes and connection errors."
        )
    
    async def grant_research(self, query: str) -> str:
        """Specialized grant research using SearXNG"""
        # Enhance query for grant-specific results
        enhanced_query = f"{query} grant funding opportunity foundation nonprofit"
        
        response = await self.web_search(enhanced_query, engines="google,bing,duckduckgo")
        
        if response.success and response.results:
            summary = f"🔍 GRANT RESEARCH RESULTS for '{query}':\n\n"
            
            for i, result in enumerate(response.results[:5], 1):
                summary += f"  {i}. {result.title}\n"
                if result.content:
                    snippet = result.content[:200] + "..." if len(result.content) > 200 else result.content
                    summary += f"     {snippet}\n"
                summary += f"     {result.url}\n\n"
            
            summary += f"🔍 SOURCE: SearXNG Metasearch ({response.instance_used})\n"
            summary += f"🌐 ENGINES: {', '.join(response.engines_used)}\n"
            summary += f"⏱️  SEARCH TIME: {response.search_time:.2f}s\n"
            summary += f"🔒 PRIVACY: No tracking, no data collection\n"
            
            return summary
        else:
            return f"ERROR: Grant research failed for query '{query}'. Response success={response.success}, total_results={response.total_results}, instance_used='{response.instance_used}', search_time={response.search_time}s, engines_used={response.engines_used}, error_message='{response.error_message}'"
    
    async def funder_research(self, funder_name: str) -> str:
        """Research specific grant funders using SearXNG"""
        query = f"{funder_name} foundation grants funding priorities recent awards"
        
        response = await self.web_search(query, engines="google,bing,duckduckgo")
        
        if response.success and response.results:
            summary = f"🏢 FUNDER RESEARCH for '{funder_name}':\n\n"
            
            for i, result in enumerate(response.results[:5], 1):
                summary += f"  {i}. {result.title}\n"
                if result.content:
                    snippet = result.content[:250] + "..." if len(result.content) > 250 else result.content
                    summary += f"     {snippet}\n"
                summary += f"     {result.url}\n\n"
            
            summary += f"🔍 SOURCE: SearXNG Funder Research ({response.instance_used})\n"
            summary += f"🌐 ENGINES: {', '.join(response.engines_used)}\n"
            summary += f"📊 RESULTS: {response.total_results} funder intelligence results\n"
            summary += f"🔒 PRIVACY: No tracking, anonymous search\n"
            
            return summary
        else:
            return f"ERROR: Funder research failed for funder '{funder_name}'. Response success={response.success}, total_results={response.total_results}, instance_used='{response.instance_used}', search_time={response.search_time}s, engines_used={response.engines_used}, error_message='{response.error_message}'"
    
    async def competitive_analysis(self, organization_type: str, focus_area: str = "") -> str:
        """Research competitive landscape using SearXNG"""
        if focus_area:
            query = f"{organization_type} {focus_area} nonprofits grants funding competitive analysis"
        else:
            query = f"{organization_type} nonprofits grants funding competitive landscape"
        
        response = await self.web_search(query, engines="google,bing,duckduckgo,startpage")
        
        if response.success and response.results:
            summary = f"🏆 COMPETITIVE ANALYSIS for '{organization_type}' organizations:\n\n"
            
            for i, result in enumerate(response.results[:4], 1):
                summary += f"  {i}. {result.title}\n"
                if result.content:
                    snippet = result.content[:200] + "..." if len(result.content) > 200 else result.content
                    summary += f"     {snippet}\n"
                summary += f"     {result.url}\n\n"
            
            summary += f"🔍 SOURCE: SearXNG Competitive Intelligence ({response.instance_used})\n"
            summary += f"🌐 ENGINES: Multi-engine aggregation\n"
            summary += f"📈 ANALYSIS: Real-time competitive landscape data\n"
            summary += f"🔒 PRIVACY: Anonymous competitive research\n"
            
            return summary
        else:
            return f"ERROR: Competitive analysis failed for organization_type '{organization_type}'. Response success={response.success}, total_results={response.total_results}, instance_used='{response.instance_used}', search_time={response.search_time}s, engines_used={response.engines_used}, error_message='{response.error_message}'"

# Global instance for easy import
searxng_tools = SearXNGMCPTools()