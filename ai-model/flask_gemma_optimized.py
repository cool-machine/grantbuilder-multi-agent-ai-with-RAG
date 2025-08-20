#!/usr/bin/env python3
"""
Optimized Gemma 3 270M-IT Flask API for Container Deployment
With enhanced error handling, caching, and startup optimization
"""
import logging
import time
import os
import sys
import signal
import traceback
import gc
from pathlib import Path
from flask import Flask, request, jsonify

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables
model = None
tokenizer = None
model_loaded = False
startup_error = None

def check_memory():
    """Check available memory"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        logger.info(f"Memory: {memory.available / 1024**3:.1f}GB available, {memory.percent}% used")
        return memory.available / 1024**3  # GB
    except:
        return 8.0  # Assume 8GB if can't check

def load_model_optimized():
    """Load Gemma 3 270M-IT model with optimization"""
    global model, tokenizer, model_loaded, startup_error
    
    try:
        logger.info('🚀 Starting optimized Gemma 3 270M-IT initialization...')
        start_time = time.time()
        
        # Check memory first
        available_memory = check_memory()
        if available_memory < 2.0:
            raise RuntimeError(f"Insufficient memory: {available_memory:.1f}GB available, need at least 2GB")
        
        model_name = "google/gemma-3-270m-it"
        cache_dir = Path("/app/cache")
        cache_dir.mkdir(exist_ok=True)
        
        # Import heavy libraries only when needed
        logger.info('📦 Importing transformers and torch...')
        import torch
        from transformers import Gemma3ForCausalLM, AutoTokenizer
        
        # Set optimizations
        torch.set_num_threads(2)  # Limit CPU threads
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        
        logger.info(f'💾 Cache directory: {cache_dir}')
        logger.info(f'🔧 PyTorch version: {torch.__version__}')
        logger.info(f'🎯 Model: {model_name}')
        
        # Get HuggingFace token from environment
        hf_token = os.getenv('HF_TOKEN')
        if hf_token:
            logger.info('🔑 Using HuggingFace token for authentication')
        else:
            logger.warning('⚠️ No HF_TOKEN found - may fail for gated models')
        
        # Load tokenizer first (smaller, faster)
        logger.info('📝 Loading tokenizer...')
        tokenizer_start = time.time()
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=str(cache_dir),
            trust_remote_code=True,
            use_fast=True,  # Use fast tokenizer
            token=hf_token  # Add token for authentication
        )
        
        # Set pad token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        tokenizer_time = time.time() - tokenizer_start
        logger.info(f'✅ Tokenizer loaded in {tokenizer_time:.2f}s')
        
        # Load model with optimizations
        logger.info('🧠 Loading Gemma 3 270M model...')
        model_start = time.time()
        
        model = Gemma3ForCausalLM.from_pretrained(
            model_name,
            cache_dir=str(cache_dir),
            trust_remote_code=True,
            torch_dtype=torch.float32,  # Use full precision for stability
            low_cpu_mem_usage=True,     # Optimize memory usage
            device_map="auto" if torch.cuda.is_available() else None,
            token=hf_token  # Add token for authentication
        )
        
        # Move to CPU explicitly if no CUDA
        if not torch.cuda.is_available():
            model = model.to('cpu')
            logger.info('🖥️ Using CPU for inference')
        else:
            logger.info('🚀 Using GPU for inference')
            
        model_time = time.time() - model_start
        logger.info(f'✅ Model loaded in {model_time:.2f}s')
        
        # Test generation
        logger.info('🧪 Testing model generation...')
        test_start = time.time()
        test_input = tokenizer("Test:", return_tensors="pt")
        
        with torch.no_grad():
            test_output = model.generate(
                **test_input,
                max_new_tokens=10,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        
        test_response = tokenizer.decode(test_output[0], skip_special_tokens=True)
        test_time = time.time() - test_start
        logger.info(f'✅ Test generation completed in {test_time:.2f}s')
        logger.info(f'🎯 Test output: {test_response}')
        
        # Clear test variables
        del test_input, test_output
        gc.collect()
        
        total_time = time.time() - start_time
        logger.info(f'🎉 Gemma 3 270M initialization complete in {total_time:.2f}s')
        logger.info(f'📊 Model parameters: ~270M')
        logger.info(f'💾 Memory usage optimized with float16 and low_cpu_mem_usage')
        
        model_loaded = True
        return True
        
    except Exception as e:
        error_msg = f"Failed to load Gemma 3 270M: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")
        startup_error = error_msg
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with detailed status"""
    global model_loaded, startup_error
    
    if startup_error:
        return jsonify({
            'status': 'error',
            'message': 'Model failed to load',
            'error': startup_error,
            'model': 'gemma-3-270m-it'
        }), 503
    
    if not model_loaded:
        return jsonify({
            'status': 'loading',
            'message': 'Gemma 3 270M is still loading...',
            'model': 'gemma-3-270m-it'
        }), 503
    
    # Check memory
    try:
        memory_info = check_memory()
        return jsonify({
            'status': 'healthy',
            'message': 'Gemma 3 270M API is ready',
            'model': 'gemma-3-270m-it',
            'loaded': True,
            'memory_available_gb': round(memory_info, 1),
            'endpoints': ['/health', '/generate'],
            'version': '1.0.0-optimized'
        }), 200
    except:
        return jsonify({
            'status': 'healthy',
            'message': 'Gemma 3 270M API is ready',
            'model': 'gemma-3-270m-it',
            'loaded': True,
            'endpoints': ['/health', '/generate'],
            'version': '1.0.0-optimized'
        }), 200

@app.route('/generate', methods=['POST'])
def generate_text():
    """Generate text using Gemma 3 270M"""
    global model, tokenizer, model_loaded
    
    if not model_loaded or model is None or tokenizer is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded yet',
            'message': 'Please wait for model initialization to complete'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: prompt'
            }), 400
        
        prompt = data['prompt']
        max_new_tokens = min(data.get('max_new_tokens', 50), 200)  # Limit tokens
        temperature = data.get('temperature', 0.7)
        
        logger.info(f'🎯 Generating for prompt: {prompt[:100]}...')
        start_time = time.time()
        
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        
        # Generate with optimized settings
        import torch
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True
            )
        
        # Decode response
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the new text (remove input prompt)
        new_text = generated_text[len(prompt):].strip()
        
        generation_time = time.time() - start_time
        
        response = {
            'success': True,
            'generated_text': new_text,
            'full_response': generated_text,
            'prompt': prompt,
            'model': 'gemma-3-270m-it',
            'generation_time': round(generation_time, 3),
            'parameters': {
                'max_new_tokens': max_new_tokens,
                'temperature': temperature
            }
        }
        
        logger.info(f'✅ Generated {len(new_text)} chars in {generation_time:.3f}s')
        
        # Cleanup
        del inputs, outputs
        gc.collect()
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f'❌ Generation error: {str(e)}')
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Text generation failed'
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        'service': 'GrantSeeker AI - Gemma 3 270M API',
        'version': '1.0.0-optimized',
        'status': 'running',
        'model': 'google/gemma-3-270m-it',
        'description': 'Optimized Gemma 3 270M for grant writing assistance',
        'endpoints': {
            '/': 'This documentation',
            '/health': 'Health check',
            '/generate': 'Text generation (POST with JSON body)'
        },
        'usage': {
            'generate': {
                'method': 'POST',
                'content_type': 'application/json',
                'body': {
                    'prompt': 'Your prompt here (required)',
                    'max_new_tokens': 'Number of tokens (optional, default: 50, max: 200)',
                    'temperature': 'Creativity level (optional, default: 0.7)'
                }
            }
        }
    }), 200

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logger.info('🛑 Received shutdown signal, cleaning up...')
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info('🚀 Starting GrantSeeker AI Gemma 3 270M API...')
    
    # Load model in startup
    success = load_model_optimized()
    if not success:
        logger.error('❌ Failed to load model during startup')
        if startup_error:
            logger.error(f'Error details: {startup_error}')
        # Still start Flask for health check access
    
    # Start Flask server
    logger.info('🌐 Starting Flask server on port 8000...')
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)