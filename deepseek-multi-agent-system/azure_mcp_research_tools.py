"""
Azure-Powered MCP Research Tools for DeepSeek R1 Multi-Agent System
Uses Azure services with your existing credits - no additional costs!
"""

import json
import requests
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import urllib.parse
from bs4 import BeautifulSoup
import aiohttp
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

@dataclass
class CrawledContent:
    """Structured content from web crawling"""
    url: str
    title: str
    content: str
    content_type: str  # "funder_info", "grant_opportunity", "applicant_info", "competitive_intel"
    key_data: Dict[str, Any]  # Extracted structured data
    relevance_score: float
    crawl_timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class ApplicantIntelligence:
    """Intelligence gathered about grant applicants"""
    organization_name: str
    organization_type: str
    website_url: Optional[str]
    key_personnel: List[Dict[str, str]]
    recent_publications: List[Dict[str, str]]
    previous_grants: List[Dict[str, Any]]
    technical_capabilities: List[str]
    partnerships: List[str]
    competitive_advantages: List[str]
    potential_weaknesses: List[str]

@dataclass
class GrantProviderIntelligence:
    """Intelligence gathered about grant providers"""
    provider_name: str
    provider_type: str  # "federal", "foundation", "corporate", etc.
    website_url: Optional[str]
    funding_priorities: List[str]
    typical_award_amounts: Dict[str, str]
    success_rates: Optional[float]
    key_personnel: List[Dict[str, str]]
    recent_awards: List[Dict[str, Any]]
    application_requirements: List[str]
    evaluation_criteria: List[Dict[str, Any]]
    deadline_patterns: List[str]
    preferred_applicant_types: List[str]

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

    # =========================
    # ENHANCED CRAWLING METHODS
    # =========================

    async def crawl_and_analyze_url(self, url: str, content_type: str) -> Optional[CrawledContent]:
        """Crawl a specific URL and extract structured information"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; GrantSeeker Research Bot)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        return await self._extract_structured_content(url, html_content, content_type)
                    else:
                        print(f"⚠️ Failed to crawl {url}: Status {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Crawling error for {url}: {e}")
            return None

    async def _extract_structured_content(self, url: str, html: str, content_type: str) -> CrawledContent:
        """Extract structured information from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract basic info
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        # Remove scripts and styles
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Extract main content
        main_content = soup.get_text()
        clean_content = re.sub(r'\s+', ' ', main_content).strip()
        
        # Extract structured data based on content type
        key_data = {}
        if content_type == "funder_info":
            key_data = self._extract_funder_data(soup)
        elif content_type == "grant_opportunity":
            key_data = self._extract_grant_opportunity_data(soup)
        elif content_type == "applicant_info":
            key_data = self._extract_applicant_data(soup)
        elif content_type == "competitive_intel":
            key_data = self._extract_competitive_data(soup)
        
        return CrawledContent(
            url=url,
            title=title_text,
            content=clean_content[:5000],  # Limit content size
            content_type=content_type,
            key_data=key_data,
            relevance_score=self._calculate_relevance(clean_content, content_type),
            crawl_timestamp=datetime.now(),
            metadata={
                "content_length": len(clean_content),
                "links_found": len(soup.find_all('a')),
                "images_found": len(soup.find_all('img'))
            }
        )

    def _extract_funder_data(self, soup) -> Dict[str, Any]:
        """Extract funder-specific information"""
        data = {
            "contact_info": [],
            "funding_areas": [],
            "application_deadlines": [],
            "award_amounts": []
        }
        
        # Look for common patterns in funder websites
        text = soup.get_text().lower()
        
        # Extract contact emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(soup))
        data["contact_info"] = list(set(emails))
        
        # Extract funding amounts (patterns like $1M, $500,000, etc.)
        amounts = re.findall(r'\$[\d,]+(?:\.\d+)?[KMB]?(?:\s*(?:million|thousand|billion))?', text)
        data["award_amounts"] = list(set(amounts))
        
        # Extract deadline patterns
        deadline_patterns = re.findall(r'deadline|due date|application closes', text)
        data["application_deadlines"] = deadline_patterns
        
        return data

    def _extract_grant_opportunity_data(self, soup) -> Dict[str, Any]:
        """Extract grant opportunity specific information"""
        data = {
            "eligibility_criteria": [],
            "funding_amount": "",
            "deadline": "",
            "application_requirements": []
        }
        
        text = soup.get_text().lower()
        
        # Look for eligibility keywords
        eligibility_keywords = ["eligible", "qualification", "requirements", "criteria"]
        for keyword in eligibility_keywords:
            if keyword in text:
                # Find sentences containing eligibility info
                sentences = re.split(r'[.!?]', text)
                for sentence in sentences:
                    if keyword in sentence:
                        data["eligibility_criteria"].append(sentence.strip())
        
        return data

    def _extract_applicant_data(self, soup) -> Dict[str, Any]:
        """Extract applicant/competitor information"""
        data = {
            "organization_type": "",
            "key_people": [],
            "research_areas": [],
            "recent_awards": []
        }
        
        # Extract key personnel from common patterns
        people_sections = soup.find_all(['div', 'section'], class_=re.compile(r'(team|people|staff|faculty)', re.I))
        for section in people_sections:
            names = re.findall(r'Dr\.\s+[A-Z][a-z]+\s+[A-Z][a-z]+|[A-Z][a-z]+\s+[A-Z][a-z]+,\s+Ph\.?D', section.get_text())
            data["key_people"].extend(names)
        
        return data

    def _extract_competitive_data(self, soup) -> Dict[str, Any]:
        """Extract competitive intelligence"""
        data = {
            "project_outcomes": [],
            "success_metrics": [],
            "partnership_info": []
        }
        
        text = soup.get_text().lower()
        
        # Look for success indicators
        success_indicators = re.findall(r'(\d+%|\d+\.\d+%)\s*(success|completion|achievement)', text)
        data["success_metrics"] = success_indicators
        
        return data

    def _calculate_relevance(self, content: str, content_type: str) -> float:
        """Calculate relevance score based on content and type"""
        # Simple relevance scoring based on keyword presence
        relevance_keywords = {
            "funder_info": ["grant", "funding", "award", "application", "deadline"],
            "grant_opportunity": ["opportunity", "solicitation", "rfp", "proposal", "eligibility"],
            "applicant_info": ["research", "university", "institution", "team", "expertise"],
            "competitive_intel": ["awarded", "successful", "funded", "winner", "selected"]
        }
        
        content_lower = content.lower()
        keywords = relevance_keywords.get(content_type, [])
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        
        return min(matches / len(keywords), 1.0) if keywords else 0.5

    async def research_grant_applicants(self, competitor_names: List[str]) -> List[ApplicantIntelligence]:
        """Research potential competitors/collaborators"""
        applicant_intel = []
        
        for org_name in competitor_names:
            try:
                # Search for organization website
                search_results = self.web_search(f"{org_name} official website", count=3)
                
                if search_results:
                    # Crawl the organization website
                    main_url = search_results[0].url
                    crawled_content = await self.crawl_and_analyze_url(main_url, "applicant_info")
                    
                    if crawled_content:
                        intel = ApplicantIntelligence(
                            organization_name=org_name,
                            organization_type="",  # To be extracted
                            website_url=main_url,
                            key_personnel=[],
                            recent_publications=[],
                            previous_grants=[],
                            technical_capabilities=[],
                            partnerships=[],
                            competitive_advantages=[],
                            potential_weaknesses=[]
                        )
                        
                        # Extract additional intelligence
                        intel = await self._enhance_applicant_intelligence(intel, crawled_content)
                        applicant_intel.append(intel)
                        
                        print(f"✅ Researched applicant: {org_name}")
                        
            except Exception as e:
                print(f"❌ Failed to research {org_name}: {e}")
        
        return applicant_intel

    async def research_grant_providers(self, provider_names: List[str]) -> List[GrantProviderIntelligence]:
        """Research grant providers/funders"""
        provider_intel = []
        
        for provider_name in provider_names:
            try:
                # Search for provider website and grant information
                search_results = self.web_search(f"{provider_name} grants funding opportunities", count=5)
                
                if search_results:
                    # Crawl provider websites
                    provider_urls = [result.url for result in search_results[:3]]
                    crawled_contents = []
                    
                    for url in provider_urls:
                        content = await self.crawl_and_analyze_url(url, "funder_info")
                        if content:
                            crawled_contents.append(content)
                    
                    if crawled_contents:
                        intel = GrantProviderIntelligence(
                            provider_name=provider_name,
                            provider_type="",  # To be extracted
                            website_url=provider_urls[0] if provider_urls else None,
                            funding_priorities=[],
                            typical_award_amounts={},
                            success_rates=None,
                            key_personnel=[],
                            recent_awards=[],
                            application_requirements=[],
                            evaluation_criteria=[],
                            deadline_patterns=[],
                            preferred_applicant_types=[]
                        )
                        
                        # Enhance with crawled data
                        intel = await self._enhance_provider_intelligence(intel, crawled_contents)
                        provider_intel.append(intel)
                        
                        print(f"✅ Researched provider: {provider_name}")
                        
            except Exception as e:
                print(f"❌ Failed to research {provider_name}: {e}")
        
        return provider_intel

    async def _enhance_applicant_intelligence(self, intel: ApplicantIntelligence, content: CrawledContent) -> ApplicantIntelligence:
        """Enhance applicant intelligence with crawled content"""
        # Extract key personnel from content
        if content.key_data.get("key_people"):
            intel.key_personnel = [{"name": person, "role": "Unknown"} for person in content.key_data["key_people"]]
        
        # Extract capabilities from content
        content_text = content.content.lower()
        capability_keywords = ["ai", "machine learning", "data science", "research", "development", "innovation"]
        intel.technical_capabilities = [kw for kw in capability_keywords if kw in content_text]
        
        return intel

    async def _enhance_provider_intelligence(self, intel: GrantProviderIntelligence, contents: List[CrawledContent]) -> GrantProviderIntelligence:
        """Enhance provider intelligence with multiple crawled contents"""
        for content in contents:
            # Combine funding amounts from all sources
            if content.key_data.get("award_amounts"):
                for amount in content.key_data["award_amounts"]:
                    intel.typical_award_amounts[f"range_{len(intel.typical_award_amounts)}"] = amount
            
            # Combine contact information
            if content.key_data.get("contact_info"):
                for contact in content.key_data["contact_info"]:
                    intel.key_personnel.append({"email": contact, "role": "Unknown"})
        
        return intel

    async def enhanced_competitive_analysis(self, context: ResearchContext, competitor_orgs: List[str] = None) -> Dict[str, Any]:
        """Enhanced competitive analysis with web crawling"""
        analysis = {
            "competitor_intelligence": [],
            "market_trends": [],
            "success_factors": [],
            "funding_landscape": {}
        }
        
        try:
            # Research competitors if provided
            if competitor_orgs:
                print(f"🔍 Researching {len(competitor_orgs)} competitors...")
                analysis["competitor_intelligence"] = await self.research_grant_applicants(competitor_orgs)
            
            # Research funding landscape
            funding_search = self.web_search(f"{context.domain} funding trends {datetime.now().year}", count=10)
            
            # Crawl funding trend articles
            trend_contents = []
            for result in funding_search[:5]:
                content = await self.crawl_and_analyze_url(result.url, "competitive_intel")
                if content:
                    trend_contents.append(content)
            
            # Extract market trends from crawled content
            for content in trend_contents:
                if content.key_data.get("success_metrics"):
                    analysis["success_factors"].extend(content.key_data["success_metrics"])
            
            print(f"✅ Enhanced competitive analysis complete: {len(analysis['competitor_intelligence'])} competitors analyzed")
            
        except Exception as e:
            print(f"❌ Enhanced competitive analysis failed: {e}")
        
        return analysis

    async def enhanced_funder_research(self, funder_name: str, context: ResearchContext = None) -> Dict[str, Any]:
        """Enhanced funder research with comprehensive web crawling"""
        research_results = {
            "provider_intelligence": [],
            "recent_awards": [],
            "application_insights": {},
            "success_patterns": []
        }
        
        try:
            print(f"🔍 Enhanced research on funder: {funder_name}")
            
            # Research the provider
            provider_intel = await self.research_grant_providers([funder_name])
            if provider_intel:
                research_results["provider_intelligence"] = provider_intel
            
            # Search for recent awards and successful applications
            awards_search = self.web_search(f"{funder_name} recent awards funded projects {datetime.now().year}", count=10)
            
            # Crawl award announcements
            for result in awards_search[:5]:
                content = await self.crawl_and_analyze_url(result.url, "competitive_intel")
                if content:
                    research_results["recent_awards"].append({
                        "title": content.title,
                        "url": content.url,
                        "insights": content.key_data
                    })
            
            print(f"✅ Enhanced funder research complete: {len(research_results['recent_awards'])} recent awards found")
            
        except Exception as e:
            print(f"❌ Enhanced funder research failed: {e}")
        
        return research_results

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