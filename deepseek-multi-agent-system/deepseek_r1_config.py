# DeepSeek R1 Configuration for LangGraph Multi-Agent System
# Load configuration from environment variables
import os

# DeepSeek R1 Serverless Endpoint (671B parameters)
DEEPSEEK_R1_ENDPOINT = os.getenv('DEEPSEEK_R1_ENDPOINT', 'https://deepseek-r1-reasoning.eastus2.models.ai.azure.com')
DEEPSEEK_R1_API_KEY = os.getenv('DEEPSEEK_R1_API_KEY', '')

# Azure OpenAI Endpoints (Existing)
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY', '')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', 'https://eastus2.api.cognitive.microsoft.com/')

# Model Assignments for Multi-Agent Architecture - ALL DEEPSEEK R1
AGENT_MODELS = {
    "general_manager": "deepseek-r1",     # DeepSeek R1 - Strategic reasoning & workflow orchestration
    "research_agent": "deepseek-r1",      # DeepSeek R1 - Deep research analysis & fact verification
    "budget_agent": "deepseek-r1",        # DeepSeek R1 - Advanced numerical reasoning & calculations
    "writing_agent": "deepseek-r1",       # DeepSeek R1 - Professional grant writing & language optimization
    "impact_agent": "deepseek-r1",        # DeepSeek R1 - Impact analysis & outcome projections
    "networking_agent": "deepseek-r1"     # DeepSeek R1 - Relationship mapping & partnership strategy
}

# Simplified Model Endpoints - SINGLE DEEPSEEK R1 ENDPOINT
MODEL_ENDPOINTS = {
    "deepseek-r1": {
        "endpoint": DEEPSEEK_R1_ENDPOINT,
        "key": DEEPSEEK_R1_API_KEY,
        "type": "deepseek_serverless",
        "model_name": "DeepSeek-R1",
        "parameters": "671B total, 37B active (MoE)",
        "context_window": "128K tokens",
        "capabilities": ["reasoning", "coding", "math", "writing", "analysis"]
    }
}

print("DeepSeek R1 configuration loaded successfully!")
print(f"General Manager Agent: {AGENT_MODELS['general_manager']}")
print(f"DeepSeek R1 Endpoint: {DEEPSEEK_R1_ENDPOINT}")