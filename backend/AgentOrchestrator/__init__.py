import azure.functions as func
import requests
import json
import logging
import os
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to orchestrate AI Foundry Agent Service for grant writing
    
    Replaces ModelProxy with intelligent multi-agent system:
    - General Manager Agent: Orchestrates and makes decisions
    - Specialist Agents: Research, Budget, Writing, Impact, Networking
    
    This provides superior results compared to single GPT model approach.
    """
    logging.info('🤖 AI Foundry Agent Orchestrator triggered')
    
    try:
        # Handle GET requests (health check)
        if req.method == 'GET':
            return func.HttpResponse(
                json.dumps({
                    "orchestrator_status": "healthy",
                    "service": "AI Foundry Agent Service",
                    "capabilities": [
                        "Multi-agent coordination",
                        "General Manager decision-making", 
                        "Specialist agent deployment",
                        "Grant writing optimization"
                    ],
                    "agents_available": {
                        "general_manager": "gpt-4o",    # Strategic reasoning (o3 not available in region)
                        "research_agent": "o3-mini",    # Light reasoning for analysis  
                        "budget_agent": "o3-mini",      # Light reasoning for calculations
                        "impact_agent": "o3-mini",      # Light reasoning for evaluation
                        "writing_agent": "gpt-4o",      # Superior language + multimodal
                        "networking_agent": "gpt-4o"   # Communication + relationship skills
                    },
                    "version": "2025.1",
                    "upgrade_from": "ModelProxy (single GPT model)"
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        # Handle POST requests (grant processing)
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
                task_type = req_body.get('task_type', 'general')
                max_tokens = req_body.get('max_tokens', req_body.get('max_new_tokens', 300))
                
                # Handle PDF file upload for multimodal o3 processing
                pdf_data = None
                if 'pdf_file' in req_body:
                    pdf_result = process_pdf_upload(req_body['pdf_file'])
                    if pdf_result['success']:
                        pdf_data = {
                            "base64": pdf_result['pdf_base64'],
                            "type": "application/pdf",
                            "size": pdf_result['size_bytes']
                        }
                        logging.info(f'📄 PDF ready for o3 multimodal analysis: {pdf_result["size_bytes"]} bytes')
                    else:
                        logging.warning(f'⚠️ PDF processing failed: {pdf_result["error"]}')
                
                logging.info(f'📝 Processing task type: {task_type}')
                
                # Route to appropriate agent workflow with PDF data for multimodal analysis
                if task_type in ['grant_application', 'full_grant']:
                    result = process_full_grant_application(prompt, req_body, pdf_data)
                elif task_type in ['research', 'grant_search']:
                    result = process_research_task(prompt, max_tokens, pdf_data)
                elif task_type in ['budget', 'financial']:
                    result = process_budget_task(prompt, max_tokens, pdf_data)
                elif task_type in ['writing', 'proposal']:
                    result = process_writing_task(prompt, max_tokens, pdf_data)
                elif task_type in ['impact', 'evaluation']:
                    result = process_impact_task(prompt, max_tokens, pdf_data)
                else:
                    # General task - use General Manager with o3
                    result = process_general_task(prompt, max_tokens, pdf_data)
                
                return func.HttpResponse(
                    json.dumps(result),
                    status_code=200,
                    mimetype="application/json"
                )
                
            except Exception as e:
                logging.error(f'❌ Processing error: {str(e)}')
                return func.HttpResponse(
                    json.dumps({
                        "error": f"Processing failed: {str(e)}",
                        "success": False,
                        "service": "AI Foundry Agent Service"
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
        logging.error(f'❌ Agent Orchestrator error: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "error": f"Orchestrator error: {str(e)}",
                "success": False
            }),
            status_code=500,
            mimetype="application/json"
        )

def create_agent(name: str, model: str, instructions: str, tools: List[str] = None) -> Dict:
    """Create an AI Foundry Agent"""
    
    # Get Azure ML access token
    token = get_azure_ml_token()
    if not token:
        raise Exception("Failed to get Azure ML authentication token")
    
    agent_data = {
        "name": name,
        "model": model,
        "instructions": instructions,
        "tools": tools or []
    }
    
    # AI Foundry Agent Service endpoint
    endpoint = f"https://eastus.api.azureml.ms/agents/v1.0/subscriptions/{get_subscription_id()}/resourceGroups/ocp10/providers/Microsoft.MachineLearningServices/workspaces/grantseeker-agents/agents"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{endpoint}?api-version=2025-05-01",
            json=agent_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            return {"success": True, "agent": response.json()}
        else:
            logging.warning(f"Agent creation returned {response.status_code}: {response.text}")
            return {"success": False, "error": f"Agent creation failed: {response.status_code}"}
            
    except Exception as e:
        logging.error(f"Error creating agent: {str(e)}")
        return {"success": False, "error": str(e)}

def run_agent(agent_id: str, message: str) -> Dict:
    """Run an AI Foundry Agent with a message"""
    
    token = get_azure_ml_token()
    if not token:
        raise Exception("Failed to get Azure ML authentication token")
    
    base_endpoint = f"https://eastus.api.azureml.ms/agents/v1.0/subscriptions/{get_subscription_id()}/resourceGroups/ocp10/providers/Microsoft.MachineLearningServices/workspaces/grantseeker-agents"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Create thread
        thread_response = requests.post(
            f"{base_endpoint}/threads?api-version=2025-05-01",
            json={},
            headers=headers,
            timeout=30
        )
        
        if thread_response.status_code != 201:
            return {"success": False, "error": f"Thread creation failed: {thread_response.status_code}"}
        
        thread_id = thread_response.json()["id"]
        
        # Add message to thread
        message_response = requests.post(
            f"{base_endpoint}/threads/{thread_id}/messages?api-version=2025-05-01",
            json={
                "role": "user",
                "content": message
            },
            headers=headers,
            timeout=30
        )
        
        if message_response.status_code != 201:
            return {"success": False, "error": f"Message creation failed: {message_response.status_code}"}
        
        # Run the agent
        run_response = requests.post(
            f"{base_endpoint}/threads/{thread_id}/runs?api-version=2025-05-01",
            json={
                "assistant_id": agent_id
            },
            headers=headers,
            timeout=30
        )
        
        if run_response.status_code != 201:
            return {"success": False, "error": f"Run creation failed: {run_response.status_code}"}
        
        run_id = run_response.json()["id"]
        
        # Wait for completion and get result
        import time
        max_wait = 60  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            status_response = requests.get(
                f"{base_endpoint}/threads/{thread_id}/runs/{run_id}?api-version=2025-05-01",
                headers=headers,
                timeout=30
            )
            
            if status_response.status_code == 200:
                run_status = status_response.json()
                if run_status["status"] == "completed":
                    # Get messages
                    messages_response = requests.get(
                        f"{base_endpoint}/threads/{thread_id}/messages?api-version=2025-05-01",
                        headers=headers,
                        timeout=30
                    )
                    
                    if messages_response.status_code == 200:
                        messages = messages_response.json()["data"]
                        if messages:
                            assistant_message = next((msg for msg in messages if msg["role"] == "assistant"), None)
                            if assistant_message:
                                return {
                                    "success": True,
                                    "response": assistant_message["content"][0]["text"]["value"],
                                    "thread_id": thread_id,
                                    "run_id": run_id
                                }
                    break
                elif run_status["status"] in ["failed", "cancelled", "expired"]:
                    return {"success": False, "error": f"Run {run_status['status']}: {run_status.get('last_error', 'Unknown error')}"}
            
            time.sleep(2)
            wait_time += 2
        
        return {"success": False, "error": "Agent execution timeout"}
        
    except Exception as e:
        logging.error(f"Error running agent: {str(e)}")
        return {"success": False, "error": str(e)}

def process_full_grant_application(prompt: str, request_data: Dict, pdf_data: Dict = None) -> Dict:
    """Process full grant application using General Manager + Specialists"""
    
    logging.info('🧠 Processing full grant application with multi-agent system')
    
    # Step 1: General Manager analyzes task and creates strategy
    gm_prompt = f"""
    You are a General Manager for grant applications. Analyze this grant writing request and create a comprehensive strategy.
    
    Request: {prompt}
    Additional context: {json.dumps(request_data.get('context', {}), indent=2)}
    
    Provide:
    1. Task analysis and requirements
    2. Which specialist agents are needed
    3. Coordination strategy and sequence
    4. Success factors and key considerations
    5. Expected deliverables
    
    Be strategic and comprehensive.
    """
    
    # Use GPT-4o for strategic reasoning with multimodal capabilities
    gm_result = call_ai_foundry_model("gpt-4o", gm_prompt, reasoning_level="high", pdf_data=pdf_data)
    
    if not gm_result.get("success"):
        return {
            "success": False,
            "error": f"General Manager failed: {gm_result.get('error')}",
            "service": "AI Foundry Agent Service"
        }
    
    strategy = gm_result["response"]
    
    # Step 2: Deploy specialist agents based on strategy
    specialists_needed = determine_specialists_needed(strategy)
    specialist_results = {}
    
    for specialist in specialists_needed:
        specialist_prompt = create_specialist_prompt(specialist, prompt, strategy, request_data)
        model = get_specialist_model(specialist)
        
        logging.info(f'🎯 Deploying {specialist} agent with model {model}')
        
        result = call_ai_foundry_model(model, specialist_prompt)
        specialist_results[specialist] = result
    
    # Step 3: General Manager synthesizes final response
    synthesis_prompt = f"""
    As General Manager, synthesize the specialist results into a comprehensive grant application response.
    
    Original Request: {prompt}
    Strategy: {strategy}
    
    Specialist Results:
    {json.dumps(specialist_results, indent=2)}
    
    Create a cohesive, professional response that integrates all specialist insights.
    """
    
    final_result = call_ai_foundry_model("gpt-4o", synthesis_prompt, reasoning_level="high", pdf_data=pdf_data)
    
    return {
        "success": True,
        "generated_text": final_result.get("response", ""),
        "strategy": strategy,
        "specialist_results": specialist_results,
        "model": "multi_agent_system",
        "agents_used": ["general_manager"] + specialists_needed,
        "service": "AI Foundry Agent Service",
        "reasoning_level": "advanced_multi_agent"
    }

def process_general_task(prompt: str, max_tokens: int, pdf_data: Dict = None) -> Dict:
    """Process general task with General Manager agent"""
    
    gm_prompt = f"""
    You are an expert General Manager AI for grant writing and research with advanced multimodal capabilities.
    
    Task: {prompt}
    {f"Note: A PDF document has been provided for analysis." if pdf_data else ""}
    
    Provide a comprehensive, professional response drawing on your expertise in:
    - Grant writing and applications
    - Research methodology
    - Project management
    - Strategic planning
    - Academic and professional writing
    
    Be thorough and actionable.
    """
    
    result = call_ai_foundry_model("o3", gm_prompt, max_tokens=max_tokens, pdf_data=pdf_data)
    
    return {
        "success": result.get("success", False),
        "generated_text": result.get("response", ""),
        "model": "general_manager_gpt_4o",
        "service": "AI Foundry Agent Service",
        "agent_type": "general_manager"
    }

def process_research_task(prompt: str, max_tokens: int, pdf_data: Dict = None) -> Dict:
    """Process research task with specialized Research agent"""
    
    research_prompt = f"""
    You are a specialized Research Agent for grant opportunities and academic research with advanced multimodal capabilities.
    
    Research Task: {prompt}
    {f"Note: A grant document PDF has been provided for detailed analysis." if pdf_data else ""}
    
    Your expertise includes:
    - Grant opportunity identification and analysis
    - Funding landscape research
    - Eligibility requirements analysis
    - Competitive analysis
    - Strategic positioning
    
    Provide detailed, actionable research insights.
    """
    
    result = call_ai_foundry_model("o3-mini", research_prompt, max_tokens=max_tokens, pdf_data=pdf_data)
    
    return {
        "success": result.get("success", False),
        "generated_text": result.get("response", ""),
        "model": "research_agent_o3_mini",
        "service": "AI Foundry Agent Service",
        "agent_type": "research_specialist"
    }

def process_budget_task(prompt: str, max_tokens: int, pdf_data: Dict = None) -> Dict:
    """Process budget task with specialized Budget agent"""
    
    budget_prompt = f"""
    You are a specialized Budget Agent for grant applications and financial planning with efficient reasoning capabilities.
    
    Budget Task: {prompt}
    {f"Note: A grant document PDF has been provided for budget analysis." if pdf_data else ""}
    
    Your expertise includes:
    - Detailed budget creation and justification
    - Cost analysis and optimization
    - Financial sustainability planning  
    - Budget narrative development
    - Cost-effectiveness analysis
    
    Provide comprehensive financial analysis and recommendations.
    """
    
    result = call_ai_foundry_model("o3-mini", budget_prompt, max_tokens=max_tokens, pdf_data=pdf_data)
    
    return {
        "success": result.get("success", False),
        "generated_text": result.get("response", ""),
        "model": "budget_agent_o3_mini", 
        "service": "AI Foundry Agent Service",
        "agent_type": "budget_specialist"
    }

def process_writing_task(prompt: str, max_tokens: int, pdf_data: Dict = None) -> Dict:
    """Process writing task with specialized Writing agent"""
    
    writing_prompt = f"""
    You are a specialized Technical Writing Agent for grant proposals and academic writing with superior multimodal capabilities.
    
    Writing Task: {prompt}
    {f"Note: A grant document PDF has been provided for comprehensive writing analysis." if pdf_data else ""}
    
    Your expertise includes:
    - Proposal writing and structure
    - Technical and academic writing
    - Methodology development  
    - Literature review and citations
    - Compliance with funding guidelines
    
    Create professional, compelling, and compliant content.
    """
    
    result = call_ai_foundry_model("gpt-4o", writing_prompt, max_tokens=max_tokens, pdf_data=pdf_data)
    
    return {
        "success": result.get("success", False),
        "generated_text": result.get("response", ""),
        "model": "writing_agent_gpt_4o",
        "service": "AI Foundry Agent Service", 
        "agent_type": "writing_specialist"
    }

def process_impact_task(prompt: str, max_tokens: int, pdf_data: Dict = None) -> Dict:
    """Process impact assessment task with specialized Impact agent"""
    
    impact_prompt = f"""
    You are a specialized Impact Assessment Agent for grant applications and program evaluation with efficient analytical reasoning.
    
    Impact Task: {prompt}
    {f"Note: A grant document PDF has been provided for impact analysis." if pdf_data else ""}
    
    Your expertise includes:
    - Impact measurement and evaluation frameworks
    - Outcome and output identification
    - Logic model development
    - Performance indicator creation
    - Long-term sustainability planning
    
    Develop comprehensive impact assessment strategies.
    """
    
    result = call_ai_foundry_model("o3-mini", impact_prompt, max_tokens=max_tokens, pdf_data=pdf_data)
    
    return {
        "success": result.get("success", False),
        "generated_text": result.get("response", ""),
        "model": "impact_agent_o3_mini",
        "service": "AI Foundry Agent Service",
        "agent_type": "impact_specialist"
    }

def call_ai_foundry_model(model: str, prompt: str, max_tokens: int = 500, reasoning_level: str = "medium", pdf_data: Dict = None) -> Dict:
    """
    Call AI Foundry models directly using serverless API
    This bypasses the need for individual agent creation for simple calls
    """
    
    try:
        # For now, use Azure OpenAI connection until Agent Service API is fully working
        # This provides the same models (o3-mini, o4-mini, etc.) through connected OpenAI resource
        
        api_key = os.environ.get('AZURE_ML_GPT_OSS_KEY', '')
        endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT', 'https://grantseeker-app.openai.azure.com/openai/deployments')
        
        # Map AI Foundry models to available deployments in your Azure OpenAI resource
        model_mapping = {
            "o3": "o3",                       # Use o3 reasoning model for advanced multimodal tasks
            "o3-mini": "o3-mini",            # Use o3-mini for efficient reasoning
            "gpt-4o": "gpt-4o",              # Use GPT-4o multimodal for vision tasks
            "gpt-4.1": "gpt-4-1106-Preview", # Fallback to GPT-4 Turbo if needed
            "gpt-5": "o3"                    # Use o3 as best available reasoning model
        }
        
        deployment_model = model_mapping.get(model, "o3")  # Default to o3 for advanced reasoning
        
        # Enhance prompt for reasoning models and strategic tasks
        if model in ["o3", "o3-mini"]:
            enhanced_prompt = f"""
            You are an advanced reasoning AI model with sophisticated multimodal and analytical capabilities.
            For o3 model specifically: Use your advanced reasoning to think deeply and systematically.
            
            Reasoning Level: {reasoning_level}
            Task Context: Grant writing and document analysis
            
            {prompt}
            
            Provide detailed step-by-step reasoning and comprehensive analysis.
            For complex grant documents, use both visual and textual understanding.
            """
        elif model == "gpt-4o" and reasoning_level == "high":
            enhanced_prompt = f"""
            You are a strategic General Manager AI with multimodal capabilities.
            Think strategically and provide comprehensive analysis.
            
            Strategic Focus: {reasoning_level} level strategic planning
            
            {prompt}
            
            Provide strategic reasoning and actionable recommendations.
            """
        else:
            enhanced_prompt = prompt
        
        # Prepare message content for multimodal processing
        if pdf_data and model in ["o3", "o3-mini", "gpt-4o"]:
            # Multimodal message with PDF content for o3 reasoning models
            message_content = [
                {
                    "type": "text",
                    "text": enhanced_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{pdf_data['type']};base64,{pdf_data['base64']}"
                    }
                }
            ]
            logging.info(f'🖼️ Sending multimodal request to {model} with PDF ({pdf_data["size"]} bytes)')
        else:
            # Text-only message
            message_content = enhanced_prompt
            if pdf_data:
                logging.info(f'⚠️ PDF provided but {model} may not support multimodal - sending text only')

        payload = {
            "messages": [
                {"role": "user", "content": message_content}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{endpoint}/{deployment_model}/chat/completions?api-version=2024-02-01",
            json=payload,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json"
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return {
                    "success": True,
                    "response": result['choices'][0]['message']['content'],
                    "model_used": deployment_model,
                    "requested_model": model
                }
        
        return {
            "success": False,
            "error": f"API call failed: {response.status_code} - {response.text}",
            "model": model
        }
        
    except Exception as e:
        logging.error(f"Error calling AI Foundry model: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model
        }

def determine_specialists_needed(strategy: str) -> List[str]:
    """Determine which specialist agents are needed based on GM strategy"""
    
    specialists = []
    strategy_lower = strategy.lower()
    
    if any(word in strategy_lower for word in ['research', 'find', 'search', 'opportunity', 'identify']):
        specialists.append('research')
    
    if any(word in strategy_lower for word in ['budget', 'financial', 'cost', 'money', 'funding']):
        specialists.append('budget')
    
    if any(word in strategy_lower for word in ['write', 'proposal', 'document', 'methodology', 'narrative']):
        specialists.append('writing')
    
    if any(word in strategy_lower for word in ['impact', 'outcome', 'evaluation', 'assessment', 'measure']):
        specialists.append('impact')
    
    # Always include at least writing for any grant application
    if not specialists:
        specialists = ['writing']
    
    return specialists

def create_specialist_prompt(specialist: str, original_prompt: str, strategy: str, request_data: Dict) -> str:
    """Create specialized prompts for each agent type"""
    
    base_context = f"""
    Original Request: {original_prompt}
    Strategic Context: {strategy}
    Additional Data: {json.dumps(request_data.get('context', {}), indent=2)}
    """
    
    specialist_instructions = {
        'research': f"""
        As the Research Specialist, focus on:
        1. Grant opportunity analysis
        2. Eligibility and requirements assessment  
        3. Competitive landscape analysis
        4. Strategic positioning recommendations
        
        {base_context}
        
        Provide comprehensive research insights and recommendations.
        """,
        
        'budget': f"""
        As the Budget Specialist, focus on:
        1. Detailed budget breakdown and justification
        2. Cost analysis and optimization
        3. Financial sustainability planning
        4. Budget narrative development
        
        {base_context}
        
        Create comprehensive financial analysis and budget recommendations.
        """,
        
        'writing': f"""
        As the Technical Writing Specialist, focus on:
        1. Professional proposal structure and content
        2. Methodology and approach development
        3. Compliance with funding guidelines
        4. Compelling narrative creation
        
        {base_context}
        
        Create professional, compelling proposal content.
        """,
        
        'impact': f"""
        As the Impact Assessment Specialist, focus on:
        1. Impact measurement framework development
        2. Outcome and output identification
        3. Performance indicator creation
        4. Evaluation methodology design
        
        {base_context}
        
        Develop comprehensive impact assessment strategy.
        """
    }
    
    return specialist_instructions.get(specialist, base_context)

def get_specialist_model(specialist: str) -> str:
    """Get optimal model for each specialist agent"""
    
    model_mapping = {
        'research': 'o3-mini',      # Light reasoning for research tasks
        'budget': 'o3-mini',        # Light reasoning for numerical analysis
        'writing': 'gpt-4o',        # Superior language + multimodal
        'impact': 'o3-mini',        # Light reasoning for structured analysis
        'networking': 'gpt-4o'      # Communication + relationship skills
    }
    
    return model_mapping.get(specialist, 'o3-mini')

def get_azure_ml_token() -> Optional[str]:
    """Get Azure ML access token for AI Foundry API calls"""
    try:
        import subprocess
        result = subprocess.run(
            ['az', 'account', 'get-access-token', '--resource', 'https://ml.azure.com', '--query', 'accessToken', '-o', 'tsv'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logging.error(f"Failed to get token: {result.stderr}")
            return None
            
    except Exception as e:
        logging.error(f"Error getting Azure ML token: {str(e)}")
        return None

def get_subscription_id() -> str:
    """Get Azure subscription ID"""
    return "f2c67079-16e2-4ab7-82ee-0c438d92b95e"

def process_pdf_upload(pdf_data: Dict) -> Dict:
    """
    Process uploaded PDF file for multimodal o3 analysis
    Prepares PDF data for direct multimodal processing (no text extraction needed)
    """
    try:
        if 'base64' in pdf_data:
            # Handle base64 encoded PDF
            pdf_base64 = pdf_data['base64']
            if pdf_base64.startswith('data:application/pdf;base64,'):
                pdf_base64 = pdf_base64.split(',')[1]
            
            # Validate base64 data
            try:
                pdf_bytes = base64.b64decode(pdf_base64)
                if len(pdf_bytes) == 0:
                    return {"success": False, "error": "Invalid or empty PDF data"}
                
                # For multimodal processing, we return the original base64 data
                return {
                    "success": True,
                    "pdf_base64": pdf_base64,
                    "pdf_type": "base64",
                    "size_bytes": len(pdf_bytes),
                    "message": "PDF ready for multimodal o3 analysis"
                }
            except Exception as decode_error:
                return {"success": False, "error": f"Invalid base64 PDF data: {str(decode_error)}"}
            
        elif 'content' in pdf_data:
            # Handle raw PDF bytes
            pdf_content = pdf_data['content']
            if len(pdf_content) == 0:
                return {"success": False, "error": "Empty PDF content"}
            
            # Convert to base64 for multimodal processing
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            return {
                "success": True,
                "pdf_base64": pdf_base64,
                "pdf_type": "converted_to_base64", 
                "size_bytes": len(pdf_content),
                "message": "PDF converted to base64 for multimodal o3 analysis"
            }
            
        else:
            return {"success": False, "error": "No valid PDF data found (expected 'base64' or 'content' field)"}
        
    except Exception as e:
        logging.error(f"PDF processing error: {str(e)}")
        return {
            "success": False,
            "error": f"PDF processing failed: {str(e)}"
        }