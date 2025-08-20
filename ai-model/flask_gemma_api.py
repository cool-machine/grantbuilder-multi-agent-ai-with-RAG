#!/usr/bin/env python3
"""
Gemma 3 270M-IT Flask API for Grant Writing AI
Containerized deployment for Azure Container Instances
"""
import logging
import time
import os
import torch
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configure logging - use stdout for container deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Global variables for model and tokenizer
model = None
tokenizer = None

def load_model():
    """Load Gemma 3 270M-IT model and tokenizer"""
    global model, tokenizer
    
    try:
        logging.info('🚀 Starting Gemma 3 270M-IT initialization...')
        start_time = time.time()
        
        model_name = "google/gemma-3-270m-it"
        
        # Load tokenizer
        tokenizer_start = time.time()
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir='/app/cache'
        )
        tokenizer_time = time.time() - tokenizer_start
        logging.info(f'✅ Tokenizer loaded in {tokenizer_time:.2f} seconds')
        
        # Load model optimized for containers
        model_start = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,  # CPU optimized
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            cache_dir='/app/cache'
        )
        model_time = time.time() - model_start
        logging.info(f'✅ Model loaded in {model_time:.2f} seconds')
        
        # Test model functionality
        test_input = tokenizer('Hello', return_tensors='pt')
        with torch.no_grad():
            test_output = model.generate(**test_input, max_new_tokens=5, do_sample=False)
        test_text = tokenizer.decode(test_output[0], skip_special_tokens=True)
        logging.info(f'✅ Model test successful: "Hello" -> "{test_text}"')
        
        total_time = time.time() - start_time
        logging.info(f'🎉 Gemma 3 270M-IT initialization complete! Total time: {total_time:.2f} seconds')
        
    except Exception as e:
        logging.error(f'❌ Model loading failed: {str(e)}')
        raise

@app.route('/', methods=['GET'])
def root():
    """API documentation and status"""
    return jsonify({
        'service': 'GrantSeeker AI - Gemma 3 270M-IT API',
        'version': '1.0.0',
        'status': 'healthy' if model is not None else 'model_not_loaded',
        'model': 'google/gemma-3-270m-it',
        'description': 'AI-powered grant writing assistance using Google Gemma 3 270M-IT',
        'endpoints': {
            '/health': 'GET - Check API and model status',
            '/generate': 'POST - Generate grant writing text from prompt'
        },
        'usage': {
            'endpoint': '/generate',
            'method': 'POST',
            'body': {
                'prompt': 'Your grant writing prompt here',
                'max_new_tokens': 100,
                'temperature': 0.7
            }
        },
        'architecture': {
            'frontend': 'React + TypeScript + Tailwind CSS',
            'backend': 'Azure Functions + Python',
            'ai_model': 'Containerized Gemma 3 270M-IT',
            'deployment': 'Azure Container Instances'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'GrantSeeker AI Model API',
        'model': 'gemma-3-270m-it',
        'model_loaded': model is not None,
        'container_id': os.environ.get('HOSTNAME', 'unknown'),
        'timestamp': time.time(),
        'memory_info': {
            'available': 'Container optimized',
            'torch_cuda_available': torch.cuda.is_available()
        }
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Generate grant writing text using Gemma 3 270M-IT"""
    global model, tokenizer
    
    if model is None or tokenizer is None:
        return jsonify({
            'error': 'Model not loaded - container may be starting up',
            'success': False,
            'suggestion': 'Wait a few seconds and try again'
        }), 503
    
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({
                'error': 'Missing prompt in request body',
                'success': False,
                'expected_format': {
                    'prompt': 'Your grant writing prompt',
                    'max_new_tokens': 100,
                    'temperature': 0.7
                }
            }), 400
            
        prompt = data['prompt']
        max_new_tokens = data.get('max_new_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        # Validate parameters
        if max_new_tokens > 500:
            max_new_tokens = 500  # Container resource protection
        if temperature < 0 or temperature > 2:
            temperature = 0.7
        
        logging.info('📥 Processing grant writing request')
        logging.info(f'🔄 Generating response for prompt: "{prompt[:50]}..."')
        logging.info(f'Parameters: max_tokens={max_new_tokens}, temp={temperature}')
        
        # Generate response
        start_time = time.time()
        
        inputs = tokenizer(prompt, return_tensors='pt')
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True if temperature > 0 else False,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1  # Improve text quality
            )
        
        # Decode only the new tokens (exclude input prompt)
        new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        generation_time = time.time() - start_time
        logging.info(f'✅ Generation completed in {generation_time:.2f} seconds')
        logging.info(f'Response length: {len(generated_text)} characters')
        
        return jsonify({
            'generated_text': generated_text,
            'model': 'gemma-3-270m-it',
            'success': True,
            'generation_time': generation_time,
            'prompt_length': len(prompt),
            'response_length': len(generated_text),
            'parameters': {
                'max_new_tokens': max_new_tokens,
                'temperature': temperature
            },
            'metadata': {
                'service': 'GrantSeeker AI',
                'container_deployment': True,
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        logging.error(f'❌ Generation error: {str(e)}')
        return jsonify({
            'error': f'Generation failed: {str(e)}',
            'success': False,
            'model': 'gemma-3-270m-it'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/', '/health', '/generate'],
        'service': 'GrantSeeker AI Model API'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'service': 'GrantSeeker AI Model API',
        'suggestion': 'Check container logs for details'
    }), 500

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('/app/logs', exist_ok=True)
    
    logging.info('🚀 Starting GrantSeeker AI Model API...')
    
    # Load model on startup
    load_model()
    
    # Production deployment with Waitress (if available) or Flask dev server
    try:
        from waitress import serve
        logging.info('🌐 Starting production server with Waitress...')
        serve(app, host='0.0.0.0', port=8000, threads=4)
    except ImportError:
        logging.info('🌐 Starting Flask development server...')
        app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)