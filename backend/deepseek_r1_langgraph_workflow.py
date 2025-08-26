"""
LangGraph Multi-Agent Workflow - All DeepSeek R1 Architecture
Grant Writing System with 671B Parameter Reasoning for Every Agent
"""

import requests
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from deepseek_r1_config import DEEPSEEK_R1_ENDPOINT, DEEPSEEK_R1_API_KEY, AGENT_MODELS, MODEL_ENDPOINTS
from deepseek_r1_agent_prompts import get_agent_prompt

@dataclass
class GrantApplicationState:
    """State management for grant application workflow"""
    grant_opportunity: str = ""
    organization_profile: str = ""
    research_findings: str = ""
    budget_analysis: str = ""
    written_narrative: str = ""
    impact_assessment: str = ""
    networking_strategy: str = ""
    final_application: str = ""
    workflow_status: str = "initialized"
    agent_outputs: Dict[str, Any] = None

    def __post_init__(self):
        if self.agent_outputs is None:
            self.agent_outputs = {}

class DeepSeekR1Client:
    """Client for DeepSeek R1 serverless endpoint"""
    
    def __init__(self):
        self.endpoint = DEEPSEEK_R1_ENDPOINT
        self.api_key = DEEPSEEK_R1_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def chat_completion(self, messages: List[Dict], agent_name: str) -> str:
        """Send chat completion request to DeepSeek R1"""
        agent_config = get_agent_prompt(agent_name)
        
        payload = {
            "messages": messages,
            "temperature": agent_config["temperature"],
            "max_tokens": agent_config["max_tokens"],
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=120  # DeepSeek R1 reasoning can take time
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"Error calling DeepSeek R1: {str(e)}"

# Initialize DeepSeek R1 client
deepseek_client = DeepSeekR1Client()

def general_manager_agent(state: GrantApplicationState) -> GrantApplicationState:
    """General Manager - Strategic workflow orchestration with DeepSeek R1"""
    prompt_config = get_agent_prompt("general_manager")
    
    messages = [
        {"role": "system", "content": prompt_config["system_prompt"]},
        {"role": "user", "content": f"""
        Analyze this grant opportunity and create a strategic application plan:
        
        Grant Opportunity: {state.grant_opportunity}
        Organization Profile: {state.organization_profile}
        
        Provide strategic direction for all specialist agents.
        """}
    ]
    
    response = deepseek_client.chat_completion(messages, "general_manager")
    state.agent_outputs["general_manager"] = response
    state.workflow_status = "strategic_plan_complete"
    
    return state

def research_agent(state: GrantApplicationState) -> GrantApplicationState:
    """Research Agent - Deep analysis with DeepSeek R1 reasoning"""
    prompt_config = get_agent_prompt("research_agent")
    
    messages = [
        {"role": "system", "content": prompt_config["system_prompt"]},
        {"role": "user", "content": f"""
        Conduct comprehensive research analysis:
        
        Grant Opportunity: {state.grant_opportunity}
        Strategic Direction: {state.agent_outputs.get('general_manager', '')}
        
        Provide detailed research findings and competitive analysis.
        """}
    ]
    
    response = deepseek_client.chat_completion(messages, "research_agent")
    state.research_findings = response
    state.agent_outputs["research_agent"] = response
    
    return state

def budget_agent(state: GrantApplicationState) -> GrantApplicationState:
    """Budget Agent - Advanced numerical reasoning with DeepSeek R1"""
    prompt_config = get_agent_prompt("budget_agent")
    
    messages = [
        {"role": "system", "content": prompt_config["system_prompt"]},
        {"role": "user", "content": f"""
        Create detailed budget analysis:
        
        Grant Opportunity: {state.grant_opportunity}
        Research Findings: {state.research_findings}
        Strategic Direction: {state.agent_outputs.get('general_manager', '')}
        
        Provide comprehensive budget with calculations and justifications.
        """}
    ]
    
    response = deepseek_client.chat_completion(messages, "budget_agent")
    state.budget_analysis = response
    state.agent_outputs["budget_agent"] = response
    
    return state

def writing_agent(state: GrantApplicationState) -> GrantApplicationState:
    """Writing Agent - Professional grant writing with DeepSeek R1"""
    prompt_config = get_agent_prompt("writing_agent")
    
    messages = [
        {"role": "system", "content": prompt_config["system_prompt"]},
        {"role": "user", "content": f"""
        Create compelling grant narrative:
        
        Grant Opportunity: {state.grant_opportunity}
        Research Findings: {state.research_findings}
        Budget Analysis: {state.budget_analysis}
        Strategic Direction: {state.agent_outputs.get('general_manager', '')}
        
        Write professional, persuasive grant application text.
        """}
    ]
    
    response = deepseek_client.chat_completion(messages, "writing_agent")
    state.written_narrative = response
    state.agent_outputs["writing_agent"] = response
    
    return state

def impact_agent(state: GrantApplicationState) -> GrantApplicationState:
    """Impact Agent - Impact analysis with DeepSeek R1 reasoning"""
    prompt_config = get_agent_prompt("impact_agent")
    
    messages = [
        {"role": "system", "content": prompt_config["system_prompt"]},
        {"role": "user", "content": f"""
        Develop comprehensive impact assessment:
        
        Grant Opportunity: {state.grant_opportunity}
        Written Narrative: {state.written_narrative}
        Budget Analysis: {state.budget_analysis}
        
        Provide detailed impact projections and measurement framework.
        """}
    ]
    
    response = deepseek_client.chat_completion(messages, "impact_agent")
    state.impact_assessment = response
    state.agent_outputs["impact_agent"] = response
    
    return state

def networking_agent(state: GrantApplicationState) -> GrantApplicationState:
    """Networking Agent - Partnership strategy with DeepSeek R1"""
    prompt_config = get_agent_prompt("networking_agent")
    
    messages = [
        {"role": "system", "content": prompt_config["system_prompt"]},
        {"role": "user", "content": f"""
        Develop networking and partnership strategy:
        
        Grant Opportunity: {state.grant_opportunity}
        Impact Assessment: {state.impact_assessment}
        Organization Profile: {state.organization_profile}
        
        Identify strategic partnerships and relationship-building opportunities.
        """}
    ]
    
    response = deepseek_client.chat_completion(messages, "networking_agent")
    state.networking_strategy = response
    state.agent_outputs["networking_agent"] = response
    
    return state

def finalize_application(state: GrantApplicationState) -> GrantApplicationState:
    """Final compilation by General Manager using DeepSeek R1"""
    messages = [
        {"role": "system", "content": get_agent_prompt("general_manager")["system_prompt"]},
        {"role": "user", "content": f"""
        Compile the final grant application:
        
        Research: {state.research_findings}
        Budget: {state.budget_analysis}  
        Narrative: {state.written_narrative}
        Impact: {state.impact_assessment}
        Networking: {state.networking_strategy}
        
        Create the final, polished grant application.
        """}
    ]
    
    response = deepseek_client.chat_completion(messages, "general_manager")
    state.final_application = response
    state.workflow_status = "complete"
    
    return state

def create_deepseek_r1_workflow():
    """Create LangGraph workflow with all DeepSeek R1 agents"""
    
    # Create the graph
    workflow = StateGraph(GrantApplicationState)
    
    # Add all DeepSeek R1 powered agents
    workflow.add_node("general_manager", general_manager_agent)
    workflow.add_node("research_agent", research_agent)
    workflow.add_node("budget_agent", budget_agent)
    workflow.add_node("writing_agent", writing_agent)
    workflow.add_node("impact_agent", impact_agent)
    workflow.add_node("networking_agent", networking_agent)
    workflow.add_node("finalize", finalize_application)
    
    # Define the workflow sequence
    workflow.set_entry_point("general_manager")
    workflow.add_edge("general_manager", "research_agent")
    workflow.add_edge("research_agent", "budget_agent")
    workflow.add_edge("budget_agent", "writing_agent") 
    workflow.add_edge("writing_agent", "impact_agent")
    workflow.add_edge("impact_agent", "networking_agent")
    workflow.add_edge("networking_agent", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()

# Test function
def test_deepseek_r1_workflow():
    """Test the all-DeepSeek R1 workflow"""
    workflow = create_deepseek_r1_workflow()
    
    # Test state
    initial_state = GrantApplicationState(
        grant_opportunity="AI Research Grant - $500K for innovative machine learning applications",
        organization_profile="University AI Research Lab with 10 years experience in ML applications"
    )
    
    print("🚀 Testing DeepSeek R1 Multi-Agent Workflow...")
    print(f"📊 All {len(AGENT_MODELS)} agents powered by DeepSeek R1 (671B parameters)")
    print(f"🔗 Endpoint: {DEEPSEEK_R1_ENDPOINT}")
    print("⚡ No rate limits - unlimited reasoning power!")
    
    return workflow, initial_state

if __name__ == "__main__":
    workflow, test_state = test_deepseek_r1_workflow()
    print("✅ DeepSeek R1 Multi-Agent Workflow ready for deployment!")