"""
Azure AI Foundry Bing Search Grounding Integration
Replaces SearXNG with reliable Azure-hosted Bing Search
"""

import os
import asyncio
import requests
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

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
    """Azure AI Foundry Bing Search Grounding for reliable web search"""
    
    def __init__(self):
        # Azure AI Foundry Project Configuration
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID', 'f2c67079-16e2-4ab7-82ee-0c438d92b95e')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'ocp10')
        self.project_name = os.getenv('AZURE_AI_PROJECT_NAME', 'grantseeker-agents-project')
        self.endpoint = f"https://eastus2.api.azureml.ms"
        
        # Initialize Azure AI Project Client
        try:
            self.credential = DefaultAzureCredential()
            self.project_client = AIProjectClient(
                endpoint=self.endpoint,
                credential=self.credential,
                subscription_id=self.subscription_id,
                resource_group_name=self.resource_group,
                project_name=self.project_name
            )
            logging.info("🔍 Azure Bing Grounding initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Azure AI Project Client: {e}")
            self.project_client = None
        
        # Bing Search Configuration
        self.default_count = 5
        self.max_count = 10  # Conservative limit for faster responses
        self.default_market = "en-US"
        self.default_freshness = None  # No time restriction by default
        
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
        
        if not self.project_client:
            return BingSearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time,
                success=False,
                error_message="Azure AI Project Client not initialized. Check Azure credentials and project configuration."
            )
        
        try:
            # Set search parameters
            search_params = {
                "query": query,
                "count": min(count or self.default_count, self.max_count),
                "market": market or self.default_market
            }
            
            if freshness:
                search_params["freshness"] = freshness
                
            logging.info(f"Azure Bing Search: query='{query}', params={search_params}")
            
            # Create agent with Bing grounding tool
            agent = self.project_client.agents.create_agent(
                model="gpt-4o",  # Use reliable model
                name=f"search-agent-{int(time.time())}",
                instructions="You are a web search assistant. Use the Bing search tool to find information and return structured results.",
                tools=[
                    {
                        "type": "bing_grounding",
                        "bing_grounding": search_params
                    }
                ]
            )
            
            # Create thread and run search
            thread = self.project_client.agents.create_thread()
            
            # Send search request
            message = self.project_client.agents.create_message(
                thread_id=thread.id,
                role="user", 
                content=f"Search for: {query}"
            )
            
            # Execute search
            run = self.project_client.agents.create_run(
                thread_id=thread.id,
                agent_id=agent.id
            )
            
            # Wait for completion (with timeout)
            timeout = 30  # 30 second timeout
            elapsed = 0
            while run.status in ["queued", "in_progress", "running"] and elapsed < timeout:
                await asyncio.sleep(1)
                run = self.project_client.agents.get_run(
                    thread_id=thread.id,
                    run_id=run.id
                )
                elapsed += 1
            
            if run.status != "completed":
                raise Exception(f"Search run failed or timed out. Status: {run.status}, elapsed: {elapsed}s")
            
            # Get search results from run steps
            run_steps = self.project_client.agents.list_run_steps(
                thread_id=thread.id,
                run_id=run.id
            )
            
            results = []
            for step in run_steps.data:
                if hasattr(step, 'step_details') and hasattr(step.step_details, 'tool_calls'):
                    for tool_call in step.step_details.tool_calls:
                        if tool_call.type == "bing_grounding":
                            # Extract Bing search results
                            search_results = tool_call.bing_grounding.results
                            for result in search_results:
                                results.append(BingSearchResult(
                                    title=result.get('title', ''),
                                    content=result.get('snippet', ''),
                                    url=result.get('url', ''),
                                    display_url=result.get('displayUrl', '')
                                ))
            
            # Cleanup - delete temporary agent and thread
            try:
                self.project_client.agents.delete_agent(agent.id)
                self.project_client.agents.delete_thread(thread.id)
            except:
                pass  # Ignore cleanup errors
            
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