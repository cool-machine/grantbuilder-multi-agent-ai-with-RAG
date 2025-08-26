#!/usr/bin/env python3
"""
Hugging Face Inference Endpoints Integration
Much cheaper alternative to Azure ML endpoints
"""

import os
import time
import requests
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class HuggingFaceEndpointManager:
    """Manage Hugging Face Inference Endpoints"""
    
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.available_models = {
            "gpt-neox-20b": {
                "id": "EleutherAI/gpt-neox-20b",
                "name": "GPT-NeoX-20B",
                "size": "20B",
                "type": "Large Language Model",
                "description": "Open-source 20B model, excellent quality",
                "cost_per_hour": 1.20,
                "endpoint_url": None  # Will be set when deployed
            },
            "llama2-7b-chat": {
                "id": "meta-llama/Llama-2-7b-chat-hf", 
                "name": "Llama 2 7B Chat",
                "size": "7B",
                "type": "Large Language Model",
                "description": "Meta's chat-optimized Llama 2",
                "cost_per_hour": 0.60,
                "endpoint_url": None
            },
            "mistral-7b-instruct": {
                "id": "mistralai/Mistral-7B-Instruct-v0.1",
                "name": "Mistral 7B Instruct", 
                "size": "7B",
                "type": "Large Language Model",
                "description": "Mistral's instruction-tuned model",
                "cost_per_hour": 0.60,
                "endpoint_url": None
            },
            "code-llama-13b": {
                "id": "codellama/CodeLlama-13b-Instruct-hf",
                "name": "Code Llama 13B",
                "size": "13B", 
                "type": "Code Generation",
                "description": "Meta's code-specialized model",
                "cost_per_hour": 0.90,
                "endpoint_url": None
            },
            "flan-t5-xxl": {
                "id": "google/flan-t5-xxl",
                "name": "FLAN-T5 XXL (11B)",
                "size": "11B",
                "type": "Instruction Following", 
                "description": "Google's largest FLAN-T5, great for structured tasks",
                "cost_per_hour": 0.80,
                "endpoint_url": None
            }
        }
        self.current_model = None
    
    def is_configured(self) -> bool:
        """Check if HuggingFace token is configured"""
        return bool(self.hf_token)
    
    def create_endpoint(self, model_key: str) -> Dict[str, Any]:
        """Create a Hugging Face Inference Endpoint"""
        if not self.is_configured():
            return {"success": False, "error": "HUGGINGFACE_TOKEN not configured"}
        
        if model_key not in self.available_models:
            return {"success": False, "error": f"Model {model_key} not available"}
        
        model_info = self.available_models[model_key]
        endpoint_name = f"grantseeker-{model_key}"
        
        # Hugging Face Inference Endpoints API
        url = "https://api.endpoints.huggingface.co/v2/endpoint"
        
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        # Endpoint configuration
        payload = {
            "accountId": None,  # Uses your default account
            "compute": {
                "accelerator": "gpu",
                "instanceSize": "medium",  # medium = 1 GPU, large = 2 GPU
                "instanceType": "nvidia-t4",
                "scaling": {
                    "maxReplica": 1,
                    "minReplica": 0  # Auto-scale to 0 when not used
                }
            },
            "model": {
                "framework": "pytorch",
                "image": {
                    "huggingface": {}
                },
                "repository": model_info["id"],
                "revision": "main",
                "task": "text-generation"
            },
            "name": endpoint_name,
            "provider": {
                "region": "us-east-1", 
                "vendor": "aws"
            },
            "type": "protected"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 202:  # Accepted
                endpoint_data = response.json()
                model_info["endpoint_url"] = endpoint_data["url"]
                
                return {
                    "success": True,
                    "message": f"Endpoint creation started for {model_info['name']}",
                    "endpoint_url": endpoint_data["url"],
                    "status": "creating",
                    "estimated_time": "5-10 minutes",
                    "cost_per_hour": model_info["cost_per_hour"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create endpoint: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
    
    def check_endpoint_status(self, model_key: str) -> Dict[str, Any]:
        """Check if endpoint is ready"""
        if model_key not in self.available_models:
            return {"success": False, "error": "Model not found"}
        
        model_info = self.available_models[model_key] 
        if not model_info.get("endpoint_url"):
            return {"success": False, "error": "Endpoint not created"}
        
        # Check endpoint status
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        try:
            response = requests.get(
                f"https://api.endpoints.huggingface.co/v2/endpoint/{model_key}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "status": data.get("status", "unknown"),
                    "ready": data.get("status") == "running"
                }
            else:
                return {"success": False, "error": f"Status check failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_text(self, model_key: str, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text using Hugging Face endpoint"""
        if model_key not in self.available_models:
            return {"success": False, "error": "Model not found"}
        
        model_info = self.available_models[model_key]
        endpoint_url = model_info.get("endpoint_url")
        
        if not endpoint_url:
            return {"success": False, "error": "Endpoint not deployed"}
        
        start_time = time.time()
        
        # Payload for text generation
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(endpoint_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result[0]["generated_text"] if result else ""
                
                generation_time = time.time() - start_time
                
                return {
                    "success": True,
                    "response": generated_text,
                    "model_name": model_info["name"], 
                    "generation_time": round(generation_time, 2),
                    "response_length": len(generated_text),
                    "cost_per_hour": model_info["cost_per_hour"],
                    "endpoint_info": {
                        "provider": "Hugging Face",
                        "model_size": model_info["size"],
                        "endpoint_url": endpoint_url
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Generation failed: {response.status_code} - {response.text}",
                    "generation_time": time.time() - start_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "generation_time": time.time() - start_time
            }
    
    def delete_endpoint(self, model_key: str) -> Dict[str, Any]:
        """Delete endpoint to stop costs"""
        if model_key not in self.available_models:
            return {"success": False, "error": "Model not found"}
        
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        try:
            response = requests.delete(
                f"https://api.endpoints.huggingface.co/v2/endpoint/{model_key}",
                headers=headers
            )
            
            if response.status_code == 202:
                return {
                    "success": True,
                    "message": f"Endpoint deletion started for {model_key}"
                }
            else:
                return {"success": False, "error": f"Deletion failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models"""
        return self.available_models
    
    def estimate_cost(self, model_key: str, hours_per_day: float = 2) -> Dict[str, Any]:
        """Estimate monthly costs"""
        if model_key not in self.available_models:
            return {"error": "Model not found"}
        
        model_info = self.available_models[model_key]
        hourly_cost = model_info["cost_per_hour"]
        
        return {
            "hourly": hourly_cost,
            "daily": hourly_cost * hours_per_day,
            "monthly": hourly_cost * hours_per_day * 30,
            "model": model_info["name"]
        }

# Example usage and setup
if __name__ == "__main__":
    print("🤗 Hugging Face Inference Endpoints Setup")
    print("="*50)
    print()
    print("1. Get HuggingFace token:")
    print("   - Go to: https://huggingface.co/settings/tokens")
    print("   - Create token with 'Inference Endpoints' permission") 
    print("   - Set: export HUGGINGFACE_TOKEN='your-token'")
    print()
    print("2. Available models and costs:")
    
    manager = HuggingFaceEndpointManager()
    for key, model in manager.get_models().items():
        cost = manager.estimate_cost(key, 2)  # 2 hours/day
        print(f"   {model['name']}: ${cost['monthly']:.0f}/month (2h/day)")
    
    print()
    if manager.is_configured():
        print("✅ HuggingFace token configured!")
        print("Ready to deploy endpoints.")
    else:
        print("❌ HUGGINGFACE_TOKEN not set")
        print("Set token to proceed with deployment.")