#!/usr/bin/env python3
"""
Hybrid Model Testing UI - Flask Backend
Supports both local models AND Azure OpenAI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import psutil
import json
import threading
from datetime import datetime
from typing import Dict, List, Any
import gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
import os

# Import Azure OpenAI manager
from azure_openai_models import AzureOpenAIManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables for model management
current_model = None
current_tokenizer = None
current_model_name = None
model_cache = {}
testing_status = {"is_running": False, "current_test": None, "progress": 0}

# Initialize Azure OpenAI manager
azure_openai = AzureOpenAIManager()

# Combined models: Local + Azure OpenAI
def get_all_available_models():
    """Combine local and Azure OpenAI models"""
    local_models = {
        "gpt2-small": {
            "id": "gpt2",
            "name": "GPT-2 Small (117M)",
            "size": "117M",
            "type": "Local - General Purpose",
            "description": "Fast, lightweight model for quick testing",
            "ram_required": 2,
            "source": "local"
        },
        "gpt2-medium": {
            "id": "gpt2-medium", 
            "name": "GPT-2 Medium (345M)",
            "size": "345M",
            "type": "Local - General Purpose",
            "description": "Balanced performance and speed",
            "ram_required": 4,
            "source": "local"
        },
        "gpt2-large": {
            "id": "gpt2-large",
            "name": "GPT-2 Large (774M)", 
            "size": "774M",
            "type": "Local - General Purpose",
            "description": "Higher quality responses, slower",
            "ram_required": 6,
            "source": "local"
        },
        "gpt2-xl": {
            "id": "gpt2-xl",
            "name": "GPT-2 XL (1.5B)",
            "size": "1.5B",
            "type": "Local - General Purpose", 
            "description": "Largest GPT-2 model, high quality",
            "ram_required": 8,
            "source": "local"
        },
        "flan-t5-xl": {
            "id": "google/flan-t5-xl", 
            "name": "FLAN-T5 XL (3B)",
            "size": "3B",
            "type": "Local - Instruction Following",
            "description": "Larger FLAN-T5, excellent for structured tasks", 
            "ram_required": 12,
            "source": "local"
        },
        "phi2": {
            "id": "microsoft/phi-2",
            "name": "Phi-2 (2.7B)", 
            "size": "2.7B",
            "type": "Local - Code & Reasoning",
            "description": "Microsoft's compact but powerful model",
            "ram_required": 10,
            "source": "local"
        }
    }
    
    # Add Azure OpenAI models if configured
    azure_models = {}
    if azure_openai.is_configured():
        for key, model in azure_openai.get_models().items():
            azure_models[f"azure_{key}"] = {
                **model,
                "type": f"Azure OpenAI - {model['type']}",
                "source": "azure",
                "cost_per_1k": model.get('cost_per_1k', 0)
            }
    
    return {**local_models, **azure_models}

# Predefined test prompts
TEST_PROMPTS = {
    "grant_writing": {
        "name": "Grant Application Response",
        "prompt": """Write a professional grant application response for the following:

Organization: Tech for Education Initiative
Project: AI-powered learning platform for underserved communities  
Funding Request: $150,000
Question: Describe how your organization's mission aligns with this funding opportunity.

Response:"""
    },
    "creative_writing": {
        "name": "Creative Story",
        "prompt": "Write a short story about an AI that discovers it can dream. Begin with: 'The first time I dreamed, I thought I was malfunctioning.'"
    },
    "code_generation": {
        "name": "Code Generation", 
        "prompt": "Write a Python function that takes a list of numbers and returns the second largest number. Include error handling and comments."
    },
    "business_plan": {
        "name": "Business Plan Section",
        "prompt": "Write a market analysis section for a startup that provides AI-powered tutoring services for students. Focus on market size and competition."
    },
    "technical_explanation": {
        "name": "Technical Explanation",
        "prompt": "Explain how neural networks learn, using simple language that a high school student could understand. Include an analogy."
    }
}

def get_system_info():
    """Get current system resource usage"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "ram_total_gb": round(memory.total / (1024**3), 2),
        "ram_available_gb": round(memory.available / (1024**3), 2), 
        "ram_used_percent": round(memory.percent, 1),
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "azure_openai_configured": azure_openai.is_configured(),
        "timestamp": datetime.now().isoformat()
    }

def cleanup_model():
    """Clean up current model to free memory"""
    global current_model, current_tokenizer, current_model_name
    
    try:
        if current_model is not None:
            del current_model
        if current_tokenizer is not None:
            del current_tokenizer
        
        current_model = None
        current_tokenizer = None
        current_model_name = None
        
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info("Local model cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning up model: {str(e)}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info()
    })

@app.route('/api/models', methods=['GET'])
def get_available_models_endpoint():
    """Get list of all available models (local + Azure)"""
    return jsonify({
        "models": get_all_available_models(),
        "current_model": current_model_name,
        "azure_configured": azure_openai.is_configured(),
        "system_info": get_system_info()
    })

@app.route('/api/prompts', methods=['GET']) 
def get_test_prompts():
    """Get predefined test prompts"""
    return jsonify({"prompts": TEST_PROMPTS})

@app.route('/api/load_model', methods=['POST'])
def load_model():
    """Load a specific model (local or Azure)"""
    global current_model, current_tokenizer, current_model_name
    
    try:
        data = request.get_json()
        model_key = data.get('model_key')
        
        all_models = get_all_available_models()
        if model_key not in all_models:
            return jsonify({"error": "Invalid model key"}), 400
        
        model_info = all_models[model_key]
        
        # Check if same model is already loaded
        if current_model_name == model_key:
            return jsonify({
                "message": f"Model {model_info['name']} is already loaded",
                "model_name": model_info['name'],
                "system_info": get_system_info()
            })
        
        # Handle Azure OpenAI models
        if model_info.get('source') == 'azure':
            cleanup_model()  # Clean up any local model
            
            # "Load" Azure model (just set it as current)
            azure_key = model_key.replace('azure_', '')
            result = azure_openai.load_model(azure_key)
            
            if result['success']:
                current_model_name = model_key
                return jsonify({
                    "message": result['message'],
                    "model_name": model_info['name'],
                    "cost_info": f"${model_info.get('cost_per_1k', 0)} per 1K tokens",
                    "source": "azure",
                    "system_info": get_system_info()
                })
            else:
                return jsonify({"error": result['error']}), 500
        
        # Handle local models
        else:
            # Clean up previous model
            cleanup_model()
            
            # Check available memory for local models
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            required_memory = model_info.get('ram_required', 1)
            
            if available_gb < required_memory:
                return jsonify({
                    "error": f"Insufficient memory. Required: {required_memory}GB, Available: {available_gb:.1f}GB"
                }), 400
            
            logger.info(f"Loading local model: {model_info['name']} ({model_info['id']})")
            
            # Load tokenizer
            current_tokenizer = AutoTokenizer.from_pretrained(model_info['id'])
            if current_tokenizer.pad_token is None:
                current_tokenizer.pad_token = current_tokenizer.eos_token
            
            # Load model with appropriate settings
            load_kwargs = {
                "torch_dtype": torch.float16,
                "device_map": "auto", 
                "low_cpu_mem_usage": True
            }
            
            current_model = AutoModelForCausalLM.from_pretrained(model_info['id'], **load_kwargs)
            current_model_name = model_key
            
            logger.info(f"Local model {model_info['name']} loaded successfully")
            
            return jsonify({
                "message": f"Local model {model_info['name']} loaded successfully",
                "model_name": model_info['name'],
                "source": "local",
                "system_info": get_system_info()
            })
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        cleanup_model()
        return jsonify({"error": f"Failed to load model: {str(e)}"}), 500

@app.route('/api/generate', methods=['POST'])
def generate_text():
    """Generate text using the currently loaded model (local or Azure)"""
    global current_model, current_tokenizer, current_model_name
    
    try:
        if not current_model_name:
            return jsonify({"error": "No model loaded. Please load a model first."}), 400
        
        data = request.get_json()
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        all_models = get_all_available_models()
        model_info = all_models[current_model_name]
        
        # Handle Azure OpenAI generation
        if model_info.get('source') == 'azure':
            result = azure_openai.generate_text(prompt, max_tokens, temperature)
            return jsonify(result)
        
        # Handle local model generation
        else:
            if current_model is None or current_tokenizer is None:
                return jsonify({"error": "Local model not properly loaded"}), 400
            
            logger.info(f"Generating text with local model: {current_model_name}")
            
            # Record start time and system state
            start_time = time.time()
            initial_memory = get_system_info()
            
            # Tokenize input
            inputs = current_tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512
            )
            
            # Generate response
            with torch.no_grad():
                outputs = current_model.generate(
                    inputs.input_ids,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=current_tokenizer.eos_token_id,
                    eos_token_id=current_tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = current_tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = generated_text[len(prompt):].strip()
            
            # Calculate metrics
            generation_time = time.time() - start_time
            final_memory = get_system_info()
            
            result = {
                "success": True,
                "response": response,
                "model_name": model_info['name'],
                "generation_time": round(generation_time, 2),
                "response_length": len(response),
                "prompt_length": len(prompt),
                "max_tokens": max_tokens,
                "temperature": temperature,
                "source": "local",
                "system_info": {
                    "initial": initial_memory,
                    "final": final_memory
                }
            }
            
            logger.info(f"Local text generated successfully in {generation_time:.2f}s")
            
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        return jsonify({"error": f"Failed to generate text: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting Hybrid Model Testing UI")
    print("="*50)
    print(f"Azure OpenAI configured: {azure_openai.is_configured()}")
    print(f"Local models available: {len([m for m in get_all_available_models().values() if m.get('source') == 'local'])}")
    print(f"Azure models available: {len([m for m in get_all_available_models().values() if m.get('source') == 'azure'])}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)