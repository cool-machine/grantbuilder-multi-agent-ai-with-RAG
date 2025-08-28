"""
Enhanced Multi-Agent Orchestrator with DeepSeek R1 + Web Crawling Capabilities
Integrates the enhanced research system with debugging visualization
"""

import azure.functions as func
import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the DeepSeek multi-agent system to the path
sys.path.append('/home/site/wwwroot/deepseek-multi-agent-system')

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Enhanced Multi-Agent Orchestrator with DeepSeek R1 + Debugging
    """
    logging.info('🚀 Enhanced Multi-Agent Orchestrator triggered')
    
    try:
        # Handle GET requests (health check with debug info)
        if req.method == 'GET':
            return func.HttpResponse(
                json.dumps({
                    "orchestrator_status": "healthy",
                    "service": "Enhanced DeepSeek R1 Multi-Agent System",
                    "capabilities": [
                        "DeepSeek R1 Multi-Agent Architecture (671B params, 37B active)",
                        "Enhanced web crawling and intelligence gathering",
                        "Dual research: Applicant + Grant Provider analysis", 
                        "LangGraph orchestration with state management",
                        "Inter-agent communication and debugging",
                        "Three-way document processing",
                        "Real-time competitive intelligence"
                    ],
                    "agents_available": {
                        "general_manager": "DeepSeek R1 (37B active)",
                        "research_agent": "DeepSeek R1 + Web Crawling",
                        "budget_agent": "DeepSeek R1 + Financial Analysis",
                        "impact_agent": "DeepSeek R1 + Evaluation Framework",
                        "writing_agent": "DeepSeek R1 + Professional Writing",
                        "networking_agent": "DeepSeek R1 + Partnership Intelligence"
                    },
                    "enhanced_features": {
                        "web_crawling": "BeautifulSoup + aiohttp",
                        "intelligence_gathering": "Applicant research + Grant provider analysis",
                        "debugging": "Agent dialogue visualization",
                        "processing_modes": "Azure+DeepSeek, o3-ready, Quick Fill"
                    },
                    "debug_capabilities": [
                        "Agent internal reasoning visualization",
                        "Step-by-step decision tracking", 
                        "Web crawling results inspection",
                        "Inter-agent communication logs"
                    ],
                    "version": "2025.1-Enhanced",
                    "upgrade_from": "Basic AgentOrchestrator"
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        # Handle POST requests (enhanced processing)
        elif req.method == 'POST':
            try:
                # Get request body
                req_body = req.get_json()
                if not req_body:
                    return func.HttpResponse(
                        json.dumps({"error": "No JSON body provided", "success": False}),
                        status_code=400,
                        mimetype="application/json"
                    )
                
                # Extract request parameters
                prompt = req_body.get('prompt', '')
                debug_mode = req_body.get('debug', False)  # Enable agent dialogue visualization
                max_tokens = req_body.get('max_tokens', req_body.get('max_new_tokens', 300))
                
                logging.info(f'📝 Processing enhanced request with debug_mode={debug_mode}')
                
                # Process with Enhanced DeepSeek R1 Multi-Agent System
                result = process_with_enhanced_multiagent_system(
                    prompt=prompt,
                    debug_mode=debug_mode,
                    max_tokens=max_tokens,
                    request_data=req_body
                )
                
                return func.HttpResponse(
                    json.dumps(result),
                    status_code=200,
                    mimetype="application/json"
                )
                
            except Exception as e:
                logging.error(f'❌ Enhanced processing error: {str(e)}')
                return func.HttpResponse(
                    json.dumps({
                        "error": f"Enhanced processing failed: {str(e)}",
                        "success": False,
                        "service": "Enhanced DeepSeek R1 Multi-Agent System",
                        "debug_info": {
                            "error_type": type(e).__name__,
                            "error_location": "process_with_enhanced_multiagent_system"
                        }
                    }),
                    status_code=500,
                    mimetype="application/json"
                )
        
        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed", "allowed": ["GET", "POST"]}),
                status_code=405,
                mimetype="application/json"
            )
            
    except Exception as e:
        logging.error(f'❌ Enhanced Agent Orchestrator error: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "error": f"Enhanced orchestrator error: {str(e)}",
                "success": False,
                "debug_info": {
                    "error_type": type(e).__name__,
                    "error_location": "main"
                }
            }),
            status_code=500,
            mimetype="application/json"
        )

def process_with_enhanced_multiagent_system(prompt: str, debug_mode: bool, max_tokens: int, request_data: Dict) -> Dict:
    """
    Process request using Enhanced DeepSeek R1 Multi-Agent System with debugging
    """
    try:
        logging.info('🤖 Loading Enhanced DeepSeek R1 Multi-Agent System...')
        
        # Import the enhanced system components - NO FALLBACKS
        from integrated_deepseek_mcp_system import IntegratedDeepSeekMCPSystem
        from azure_mcp_research_tools import AzureMCPResearchTools, ResearchContext
        from deepseek_r1_langgraph_workflow import DeepSeekR1Client
        
        logging.info('✅ Enhanced system components loaded successfully')
        
        # Initialize the enhanced system with debugging
        enhanced_system = IntegratedDeepSeekMCPSystem(debug_mode=debug_mode)
        
        # Create research context from request
        research_context = create_research_context_from_request(request_data)
        
        # Process with full enhanced capabilities
        if debug_mode:
            logging.info('🔍 Debug mode enabled - will capture agent dialogue')
        
        result = enhanced_system.process_grant_request(
            prompt=prompt,
            context=research_context,
            max_tokens=max_tokens,
            enable_web_crawling=True,
            enable_debugging=debug_mode
        )
        
        # Add debugging information if requested
        if debug_mode:
            result["debug_info"] = {
                "agent_dialogue": enhanced_system.get_agent_dialogue(),
                "decision_tree": enhanced_system.get_decision_tree(),
                "web_crawling_results": enhanced_system.get_crawling_results(),
                "research_intelligence": enhanced_system.get_research_intelligence()
            }
        
        return {
            "success": True,
            "generated_text": result.get("response", ""),
            "model": "enhanced_deepseek_r1_multiagent",
            "service": "Enhanced DeepSeek R1 Multi-Agent System",
            "agents_used": result.get("agents_used", []),
            "processing_time": result.get("processing_time", 0),
            "enhanced_features": {
                "web_crawling_enabled": True,
                "intelligence_gathering": True,
                "multi_agent_coordination": True,
                "debugging_enabled": debug_mode
            },
            **result
        }
        
    except Exception as e:
        logging.error(f"❌ Enhanced multi-agent system failed: {str(e)}")
        
        # NO FALLBACKS - surface the error explicitly
        raise Exception(f"Enhanced multi-agent system failed: {str(e)}")

# NO FALLBACK FUNCTIONS - Enhanced system must work or fail explicitly

def create_research_context_from_request(request_data: Dict) -> Dict:
    """
    Create a research context for the enhanced system from the request - NO FALLBACKS
    """
    from azure_mcp_research_tools import ResearchContext
    
    # Extract relevant information from request
    context_data = request_data.get('context', {})
    
    return ResearchContext(
        query=request_data.get('prompt', 'Grant application assistance'),
        domain=context_data.get('focus_area', 'general'),
        organization=context_data.get('organization_name', 'Organization'),
        funding_amount=context_data.get('max_amount', '50000')
    )