"""
Azure-Powered MCP Research Tools for DeepSeek R1 Multi-Agent System
Uses Azure services with your existing credits - no additional costs!
"""

import json
import requests
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.search.websearch import WebSearchClient
from msrest.authentication import CognitiveServicesCredentials

@dataclass
class SearchResult:
    """Standardized search result structure"""
    title: str
    url: str
    snippet: str
    relevance_score: float
    source_type: str  # "web", "database", "document"
    metadata: Dict[str, Any]
    timestamp: datetime

@dataclass
class ResearchContext:
    """Context for research queries"""
    query: str
    domain: str  # "grants", "funding", "research", etc.
    organization: str
    funding_amount: Optional[str] = None
    deadline: Optional[datetime] = None
    requirements: List[str] = None

class AzureMCPResearchTools:
    """MCP Research Tools powered by Azure services"""
    
    def __init__(self):
        # Azure service credentials (using your Azure credits)
        self.bing_subscription_key = os.getenv('AZURE_BING_SEARCH_KEY', '')
        self.cognitive_search_key = os.getenv('AZURE_SEARCH_KEY', '')
        self.cognitive_search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT', '')
        
        # Initialize Azure clients
        self.web_search_client = None
        self.search_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Azure service clients"""
        try:
            # Bing Web Search (covered by Azure credits)
            if self.bing_subscription_key:
                self.web_search_client = WebSearchClient(
                    endpoint="https://api.cognitive.microsoft.com/bing/v7.0/search",
                    credentials=CognitiveServicesCredentials(self.bing_subscription_key)
                )
                print("✅ Azure Bing Search client initialized")
            
            # Azure Cognitive Search (covered by Azure credits)
            if self.cognitive_search_key and self.cognitive_search_endpoint:
                self.search_client = SearchClient(
                    endpoint=self.cognitive_search_endpoint,
                    index_name="grants-knowledge-base",
                    credential=AzureKeyCredential(self.cognitive_search_key)
                )
                print("✅ Azure Cognitive Search client initialized")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize some Azure clients: {e}")
    
    def web_search(self, query: str, context: ResearchContext = None, count: int = 10) -> List[SearchResult]:
        """
        MCP Tool: Azure Bing Web Search
        Uses your Azure credits - no additional cost
        """
        if not self.web_search_client:
            return self._fallback_web_search(query, count)
        
        try:
            # Enhance query with context
            enhanced_query = self._enhance_query(query, context)
            
            # Perform Bing search using Azure credits
            web_data = self.web_search_client.web.search(
                query=enhanced_query,
                count=count,
                market='en-US',
                safe_search='Moderate'
            )
            
            results = []
            if web_data.web_pages and web_data.web_pages.value:
                for page in web_data.web_pages.value:
                    result = SearchResult(
                        title=page.name,
                        url=page.url,
                        snippet=page.snippet or "",
                        relevance_score=1.0,  # Bing doesn't provide scores
                        source_type="web",
                        metadata={
                            "date_last_crawled": getattr(page, 'date_last_crawled', None),
                            "display_url": getattr(page, 'display_url', ''),
                            "language": "en"
                        },
                        timestamp=datetime.now()
                    )
                    results.append(result)
            
            print(f"🔍 Azure Bing Search: Found {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            print(f"❌ Azure Bing Search error: {e}")
            return self._fallback_web_search(query, count)
    
    def knowledge_base_search(self, query: str, context: ResearchContext = None) -> List[SearchResult]:
        """
        MCP Tool: Azure Cognitive Search for Grant Knowledge Base
        Uses your Azure credits - no additional cost
        """
        if not self.search_client:
            return self._create_mock_knowledge_results(query)
        
        try:
            # Enhanced search with semantic ranking (Azure credits)
            search_text = self._enhance_query(query, context)
            
            results = self.search_client.search(
                search_text=search_text,
                top=10,
                include_total_count=True,
                highlight_fields="content,title",
                select="title,content,url,funding_amount,deadline,requirements",
                order_by=["search.score() desc"]
            )
            
            search_results = []
            for doc in results:
                result = SearchResult(
                    title=doc.get('title', 'Unknown Title'),
                    url=doc.get('url', ''),
                    snippet=doc.get('content', '')[:300] + "...",
                    relevance_score=doc.get('@search.score', 0.0),
                    source_type="database",
                    metadata={
                        "funding_amount": doc.get('funding_amount'),
                        "deadline": doc.get('deadline'),
                        "requirements": doc.get('requirements', []),
                        "highlights": doc.get('@search.highlights', {})
                    },
                    timestamp=datetime.now()
                )
                search_results.append(result)
            
            print(f"📊 Azure Knowledge Base: Found {len(search_results)} results")
            return search_results
            
        except Exception as e:
            print(f"❌ Azure Knowledge Base error: {e}")
            return self._create_mock_knowledge_results(query)
    
    def funder_research(self, funder_name: str, context: ResearchContext = None) -> Dict[str, Any]:
        """
        MCP Tool: Comprehensive Funder Research
        Combines web search + knowledge base using Azure credits
        """
        print(f"🎯 Researching funder: {funder_name}")
        
        # Multi-source research using Azure services
        research_queries = [
            f"{funder_name} grant opportunities 2025",
            f"{funder_name} funding priorities requirements",
            f"{funder_name} successful applications examples",
            f"{funder_name} application deadlines budget limits"
        ]
        
        all_results = []
        for query in research_queries:
            # Use Azure Bing Search (covered by credits)
            web_results = self.web_search(query, context, count=5)
            all_results.extend(web_results)
            
            # Use Azure Knowledge Base (covered by credits)
            kb_results = self.knowledge_base_search(query, context)
            all_results.extend(kb_results)
        
        # Analyze results with structure
        funder_profile = {
            "name": funder_name,
            "funding_opportunities": [],
            "requirements": [],
            "preferences": [],
            "recent_awards": [],
            "application_tips": [],
            "contact_information": {},
            "research_timestamp": datetime.now().isoformat(),
            "total_sources": len(all_results),
            "azure_services_used": ["Bing Search", "Cognitive Search"]
        }
        
        # Extract structured information from results
        for result in all_results:
            # Use simple keyword extraction (can be enhanced with Azure AI Language)
            if "funding" in result.snippet.lower():
                funder_profile["funding_opportunities"].append({
                    "source": result.title,
                    "url": result.url,
                    "description": result.snippet[:200],
                    "relevance": result.relevance_score
                })
            
            if any(word in result.snippet.lower() for word in ["requirement", "eligibility", "criteria"]):
                funder_profile["requirements"].append({
                    "source": result.title,
                    "requirement": result.snippet[:150],
                    "url": result.url
                })
        
        print(f"📈 Funder research complete: {len(funder_profile['funding_opportunities'])} opportunities found")
        return funder_profile
    
    def competitive_analysis(self, context: ResearchContext) -> Dict[str, Any]:
        """
        MCP Tool: Competitive Grant Analysis
        Uses Azure services to analyze competitive landscape
        """
        print(f"🏆 Analyzing competitive landscape for: {context.domain}")
        
        # Research competitive grants in the same domain
        search_queries = [
            f"{context.domain} grants awarded 2024 2025",
            f"successful {context.domain} grant applications examples",
            f"{context.funding_amount} {context.domain} funding winners"
        ]
        
        competitive_data = {
            "domain": context.domain,
            "analysis_date": datetime.now().isoformat(),
            "successful_projects": [],
            "common_themes": [],
            "funding_ranges": [],
            "success_factors": [],
            "competitive_advantage_opportunities": []
        }
        
        all_results = []
        for query in search_queries:
            results = self.web_search(query, context, count=8)
            all_results.extend(results)
        
        # Analyze competitive patterns
        for result in all_results:
            if any(word in result.snippet.lower() for word in ["awarded", "funded", "successful"]):
                competitive_data["successful_projects"].append({
                    "title": result.title,
                    "description": result.snippet[:200],
                    "source": result.url,
                    "relevance": result.relevance_score
                })
        
        print(f"🎯 Competitive analysis complete: {len(competitive_data['successful_projects'])} examples found")
        return competitive_data
    
    def _enhance_query(self, query: str, context: ResearchContext = None) -> str:
        """Enhance search queries with context"""
        if not context:
            return query
        
        enhanced = query
        if context.domain:
            enhanced += f" {context.domain}"
        if context.funding_amount:
            enhanced += f" {context.funding_amount}"
        if context.organization:
            enhanced += f" {context.organization}"
        
        return enhanced
    
    def _fallback_web_search(self, query: str, count: int) -> List[SearchResult]:
        """Fallback search when Azure services unavailable"""
        print("⚠️ Using fallback search - configure Azure Bing Search for full functionality")
        
        # Mock results for development
        return [
            SearchResult(
                title=f"Sample Result for: {query}",
                url="https://example.com",
                snippet=f"This is a sample search result for '{query}'. Configure Azure Bing Search for real results.",
                relevance_score=0.8,
                source_type="web",
                metadata={"fallback": True},
                timestamp=datetime.now()
            )
        ]
    
    def _create_mock_knowledge_results(self, query: str) -> List[SearchResult]:
        """Mock knowledge base results for development"""
        print("⚠️ Using mock knowledge base - configure Azure Cognitive Search for full functionality")
        
        return [
            SearchResult(
                title=f"Knowledge Base: {query}",
                url="https://internal-kb.com",
                snippet=f"Internal knowledge base result for '{query}'. Configure Azure Cognitive Search for real data.",
                relevance_score=0.9,
                source_type="database",
                metadata={"mock": True, "funding_amount": "$100,000"},
                timestamp=datetime.now()
            )
        ]

# MCP Tool Registry for DeepSeek R1 Agents
RESEARCH_TOOLS = {
    "web_search": {
        "name": "Azure Web Search",
        "description": "Search the web using Azure Bing Search API",
        "parameters": ["query", "context", "count"],
        "azure_service": "Bing Search",
        "cost": "Covered by Azure credits"
    },
    
    "knowledge_base_search": {
        "name": "Grant Knowledge Base Search", 
        "description": "Search internal grant database using Azure Cognitive Search",
        "parameters": ["query", "context"],
        "azure_service": "Cognitive Search",
        "cost": "Covered by Azure credits"
    },
    
    "funder_research": {
        "name": "Comprehensive Funder Research",
        "description": "Multi-source research on grant funders",
        "parameters": ["funder_name", "context"],
        "azure_service": "Multiple (Bing + Cognitive Search)",
        "cost": "Covered by Azure credits"
    },
    
    "competitive_analysis": {
        "name": "Competitive Grant Analysis",
        "description": "Analyze competitive landscape and successful projects", 
        "parameters": ["context"],
        "azure_service": "Bing Search + AI Analysis",
        "cost": "Covered by Azure credits"
    }
}

def create_research_tools():
    """Initialize Azure-powered MCP research tools"""
    tools = AzureMCPResearchTools()
    
    print("🔍 Azure MCP Research Tools initialized:")
    for tool_name, tool_info in RESEARCH_TOOLS.items():
        print(f"  ✅ {tool_info['name']} - {tool_info['azure_service']}")
    
    return tools

if __name__ == "__main__":
    # Test the research tools
    tools = create_research_tools()
    
    # Test context
    context = ResearchContext(
        query="AI research grants",
        domain="artificial intelligence",
        organization="University Research Lab",
        funding_amount="$500,000"
    )
    
    print("🧪 Testing Azure MCP Research Tools...")
    results = tools.web_search("AI research funding opportunities", context, count=3)
    print(f"✅ Found {len(results)} web search results")
    
    kb_results = tools.knowledge_base_search("machine learning grants", context)
    print(f"✅ Found {len(kb_results)} knowledge base results")
    
    print("🚀 Azure MCP Research Tools ready for DeepSeek R1 agents!")