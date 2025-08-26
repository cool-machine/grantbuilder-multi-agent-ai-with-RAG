#!/usr/bin/env python3
"""
Model Testing UI - Flask Backend
Runs on Azure ML Compute Instance
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

# Available models configuration - Optimized for 32GB RAM
AVAILABLE_MODELS = {
    "gpt2-small": {
        "id": "gpt2",
        "name": "GPT-2 Small (117M)",
        "size": "117M",
        "type": "General Purpose",
        "description": "Fast, lightweight model for quick testing",
        "ram_required": 2
    },
    "gpt2-medium": {
        "id": "gpt2-medium", 
        "name": "GPT-2 Medium (345M)",
        "size": "345M",
        "type": "General Purpose",
        "description": "Balanced performance and speed",
        "ram_required": 4
    },
    "gpt2-large": {
        "id": "gpt2-large",
        "name": "GPT-2 Large (774M)", 
        "size": "774M",
        "type": "General Purpose",
        "description": "Higher quality responses, slower",
        "ram_required": 6
    },
    "gpt2-xl": {
        "id": "gpt2-xl",
        "name": "GPT-2 XL (1.5B)",
        "size": "1.5B",
        "type": "General Purpose", 
        "description": "Largest GPT-2 model, high quality",
        "ram_required": 8
    },
    "distilgpt2": {
        "id": "distilgpt2",
        "name": "DistilGPT-2 (82M)",
        "size": "82M", 
        "type": "Distilled",
        "description": "Lightweight distilled version",
        "ram_required": 2
    },
    "microsoft-dialoGPT": {
        "id": "microsoft/DialoGPT-medium",
        "name": "DialoGPT Medium (345M)",
        "size": "345M",
        "type": "Conversational", 
        "description": "Optimized for dialogue",
        "ram_required": 4
    },
    "flan-t5-large": {
        "id": "google/flan-t5-large",
        "name": "FLAN-T5 Large (780M)",
        "size": "780M",
        "type": "Instruction Following",
        "description": "Google's instruction-tuned T5, great for tasks",
        "ram_required": 6
    },
    "flan-t5-xl": {
        "id": "google/flan-t5-xl", 
        "name": "FLAN-T5 XL (3B)",
        "size": "3B",
        "type": "Instruction Following",
        "description": "Larger FLAN-T5, excellent for structured tasks", 
        "ram_required": 12
    },
    "phi2": {
        "id": "microsoft/phi-2",
        "name": "Phi-2 (2.7B)", 
        "size": "2.7B",
        "type": "Code & Reasoning",
        "description": "Microsoft's compact but powerful model",
        "ram_required": 10
    },
    "code-llama-7b": {
        "id": "codellama/CodeLlama-7b-hf",
        "name": "Code Llama 7B",
        "size": "7B",
        "type": "Code Generation", 
        "description": "Meta's code-specialized Llama (requires 28GB+ RAM)",
        "ram_required": 28
    },
    "mistral-7b": {
        "id": "mistralai/Mistral-7B-v0.1",
        "name": "Mistral 7B", 
        "size": "7B",
        "type": "Large Language Model",
        "description": "Efficient 7B model (requires 28GB+ RAM)",
        "ram_required": 28
    }
}

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
            
        logger.info("Model cleaned up successfully")
        
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
def get_available_models():
    """Get list of available models"""
    return jsonify({
        "models": AVAILABLE_MODELS,
        "current_model": current_model_name,
        "system_info": get_system_info()
    })

@app.route('/api/prompts', methods=['GET']) 
def get_test_prompts():
    """Get predefined test prompts"""
    return jsonify({"prompts": TEST_PROMPTS})

@app.route('/api/load_model', methods=['POST'])
def load_model():
    """Load a specific model"""
    global current_model, current_tokenizer, current_model_name
    
    try:
        data = request.get_json()
        model_key = data.get('model_key')
        
        if model_key not in AVAILABLE_MODELS:
            return jsonify({"error": "Invalid model key"}), 400
        
        model_info = AVAILABLE_MODELS[model_key]
        model_id = model_info['id']
        
        # Check if same model is already loaded
        if current_model_name == model_key:
            return jsonify({
                "message": f"Model {model_info['name']} is already loaded",
                "model_name": model_info['name'],
                "system_info": get_system_info()
            })
        
        # Clean up previous model
        cleanup_model()
        
        # Check available memory
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        
        # Get required memory from model config
        required_memory = model_info.get('ram_required', 1)
        
        if available_gb < required_memory:
            return jsonify({
                "error": f"Insufficient memory. Required: {required_memory}GB, Available: {available_gb:.1f}GB"
            }), 400
        
        logger.info(f"Loading model: {model_info['name']} ({model_id})")
        
        # Load tokenizer
        current_tokenizer = AutoTokenizer.from_pretrained(model_id)
        if current_tokenizer.pad_token is None:
            current_tokenizer.pad_token = current_tokenizer.eos_token
        
        # Load model with appropriate settings
        load_kwargs = {
            "torch_dtype": torch.float16,
            "device_map": "auto", 
            "low_cpu_mem_usage": True
        }
        
        # For large models, use additional memory optimizations
        if model_info['size'] in ['7B', '20B']:
            load_kwargs["load_in_8bit"] = True
        
        current_model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)
        current_model_name = model_key
        
        logger.info(f"Model {model_info['name']} loaded successfully")
        
        return jsonify({
            "message": f"Model {model_info['name']} loaded successfully",
            "model_name": model_info['name'],
            "system_info": get_system_info()
        })
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        cleanup_model()
        return jsonify({"error": f"Failed to load model: {str(e)}"}), 500

@app.route('/api/generate', methods=['POST'])
def generate_text():
    """Generate text using the currently loaded model"""
    global current_model, current_tokenizer, current_model_name
    
    try:
        if current_model is None or current_tokenizer is None:
            return jsonify({"error": "No model loaded. Please load a model first."}), 400
        
        data = request.get_json()
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        logger.info(f"Generating text with {current_model_name}")
        
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
            "model_name": AVAILABLE_MODELS[current_model_name]['name'],
            "generation_time": round(generation_time, 2),
            "response_length": len(response),
            "prompt_length": len(prompt),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system_info": {
                "initial": initial_memory,
                "final": final_memory
            }
        }
        
        logger.info(f"Text generated successfully in {generation_time:.2f}s")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        return jsonify({"error": f"Failed to generate text: {str(e)}"}), 500

@app.route('/api/test_models', methods=['POST'])
def test_multiple_models():
    """Test multiple models with the same prompt"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model_keys = data.get('models', [])
        max_tokens = data.get('max_tokens', 100)
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        if not model_keys:
            return jsonify({"error": "At least one model must be selected"}), 400
        
        # Start testing in background
        def run_tests():
            global testing_status
            testing_status = {"is_running": True, "results": [], "progress": 0}
            
            for i, model_key in enumerate(model_keys):
                testing_status["current_test"] = AVAILABLE_MODELS[model_key]['name']
                testing_status["progress"] = int((i / len(model_keys)) * 100)
                
                try:
                    # Load model
                    load_response = load_model_internal(model_key)
                    if not load_response["success"]:
                        testing_status["results"].append({
                            "model": AVAILABLE_MODELS[model_key]['name'],
                            "success": False,
                            "error": load_response["error"]
                        })
                        continue
                    
                    # Generate text
                    gen_response = generate_text_internal(prompt, max_tokens)
                    testing_status["results"].append(gen_response)
                    
                except Exception as e:
                    testing_status["results"].append({
                        "model": AVAILABLE_MODELS[model_key]['name'],
                        "success": False,
                        "error": str(e)
                    })
            
            testing_status["is_running"] = False
            testing_status["progress"] = 100
            cleanup_model()
        
        # Start testing thread
        thread = threading.Thread(target=run_tests)
        thread.daemon = True
        thread.start()
        
        return jsonify({"message": "Testing started", "status": "running"})
        
    except Exception as e:
        logger.error(f"Error starting model tests: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test_status', methods=['GET'])
def get_test_status():
    """Get current testing status"""
    return jsonify(testing_status)

def load_model_internal(model_key):
    """Internal function to load model"""
    # Implementation similar to load_model but returns dict instead of response
    pass

def generate_text_internal(prompt, max_tokens):
    """Internal function to generate text"""
    # Implementation similar to generate_text but returns dict instead of response
    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)