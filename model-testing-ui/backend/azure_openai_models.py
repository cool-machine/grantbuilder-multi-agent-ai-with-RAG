#!/usr/bin/env python3
"""
Azure OpenAI Integration for Model Testing UI
Replace local model loading with Azure OpenAI API calls
"""

import os
import time
import logging
from openai import AzureOpenAI
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AzureOpenAIManager:
    """Manage Azure OpenAI API calls"""
    
    def __init__(self):
        self.client = None
        self.available_models = {
            "gpt-35-turbo": {
                "id": "gpt-35-turbo",
                "name": "GPT-3.5 Turbo",
                "size": "175B",
                "type": "Large Language Model",
                "description": "OpenAI's GPT-3.5 Turbo - excellent for grant writing",
                "ram_required": 0,  # API-based, no local RAM needed
                "cost_per_1k": 0.50
            },
            "gpt-4": {
                "id": "gpt-4", 
                "name": "GPT-4",
                "size": "1.76T",
                "type": "Large Language Model",
                "description": "OpenAI's most capable model - premium quality",
                "ram_required": 0,
                "cost_per_1k": 15.00
            },
            "gpt-4-turbo": {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo", 
                "size": "1.76T",
                "type": "Large Language Model",
                "description": "Faster GPT-4 with longer context",
                "ram_required": 0,
                "cost_per_1k": 10.00
            },
            "gpt-4o": {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "size": "1.76T", 
                "type": "Multimodal Large Language Model",
                "description": "Latest GPT-4 optimized model",
                "ram_required": 0,
                "cost_per_1k": 5.00
            }
        }
        self.current_model = None
        self.setup_client()
    
    def setup_client(self):
        """Initialize Azure OpenAI client"""
        try:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_KEY"),
                api_version=os.getenv("AZURE_OPENAI_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            self.client = None
    
    def load_model(self, model_key: str) -> Dict[str, Any]:
        """'Load' a model (just set current model for API-based models)"""
        if not self.client:
            return {
                "success": False,
                "error": "Azure OpenAI client not configured. Check environment variables."
            }
        
        if model_key not in self.available_models:
            return {
                "success": False,
                "error": f"Model {model_key} not available"
            }
        
        self.current_model = model_key
        model_info = self.available_models[model_key]
        
        return {
            "success": True,
            "message": f"Selected {model_info['name']} - ready for API calls",
            "model_name": model_info['name'],
            "cost_info": f"${model_info['cost_per_1k']} per 1K tokens"
        }
    
    def generate_text(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text using Azure OpenAI API"""
        if not self.client or not self.current_model:
            return {
                "success": False,
                "error": "No model loaded or client not configured"
            }
        
        start_time = time.time()
        
        try:
            # Prepare messages for chat completion
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response
            generated_text = response.choices[0].message.content.strip()
            generation_time = time.time() - start_time
            
            # Calculate cost estimate
            model_info = self.available_models[self.current_model]
            total_tokens = response.usage.total_tokens if response.usage else 0
            estimated_cost = (total_tokens / 1000) * model_info['cost_per_1k']
            
            return {
                "success": True,
                "response": generated_text,
                "model_name": model_info['name'],
                "generation_time": round(generation_time, 2),
                "response_length": len(generated_text),
                "tokens_used": total_tokens,
                "estimated_cost": round(estimated_cost, 4),
                "system_info": {
                    "api_based": True,
                    "tokens": response.usage.dict() if response.usage else {}
                }
            }
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI API: {str(e)}")
            return {
                "success": False,
                "error": f"API call failed: {str(e)}",
                "model_name": self.available_models[self.current_model]['name'],
                "generation_time": time.time() - start_time
            }
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models"""
        return self.available_models
    
    def is_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured"""
        required_vars = ["AZURE_OPENAI_KEY", "AZURE_OPENAI_ENDPOINT"]
        return all(os.getenv(var) for var in required_vars) and self.client is not None

# Example usage and setup instructions
if __name__ == "__main__":
    print("🔧 Azure OpenAI Setup Instructions:")
    print("="*50)
    print()
    print("1. Set environment variables:")
    print("   export AZURE_OPENAI_KEY='your-api-key'")
    print("   export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
    print("   export AZURE_OPENAI_VERSION='2024-02-15-preview'")
    print()
    print("2. Create Azure OpenAI resource:")
    print("   - Go to Azure Portal")
    print("   - Create 'Azure OpenAI' resource")  
    print("   - Deploy GPT-3.5-turbo model")
    print("   - Copy endpoint and API key")
    print()
    print("3. Test connection:")
    
    manager = AzureOpenAIManager()
    if manager.is_configured():
        print("   ✅ Azure OpenAI configured correctly!")
        
        # Test model loading
        result = manager.load_model("gpt-35-turbo")
        print(f"   Load test: {result['message'] if result['success'] else result['error']}")
        
        if result['success']:
            # Test generation
            test_result = manager.generate_text("Write a brief test message.", max_tokens=20)
            if test_result['success']:
                print(f"   ✅ Generation test successful!")
                print(f"   Response: {test_result['response'][:50]}...")
                print(f"   Cost: ${test_result['estimated_cost']}")
            else:
                print(f"   ❌ Generation failed: {test_result['error']}")
    else:
        print("   ❌ Azure OpenAI not configured. Set environment variables.")
        print("   Missing variables:", [var for var in ["AZURE_OPENAI_KEY", "AZURE_OPENAI_ENDPOINT"] if not os.getenv(var)])