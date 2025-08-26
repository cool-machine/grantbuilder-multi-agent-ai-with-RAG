#!/usr/bin/env python3
"""
GPT-OSS-20B Flask API for Grant Writing AI
Containerized deployment for Azure Container Instances with GPU support
"""
import logging
import time
import os
import torch
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import psutil
import pynvml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/api.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Global variables for model and tokenizer
model = None
tokenizer = None
device = None

def get_gpu_info():
    """Get GPU information for monitoring"""
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        gpu_info = []
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            gpu_info.append({
                'id': i,
                'name': name,
                'total_memory_mb': memory_info.total // 1024 // 1024,
                'used_memory_mb': memory_info.used // 1024 // 1024,
                'free_memory_mb': memory_info.free // 1024 // 1024
            })
        
        return gpu_info
    except Exception as e:
        logging.warning(f"Could not get GPU info: {str(e)}")
        return []

def load_model():
    """Load GPT-OSS-20B model and tokenizer with optimization"""
    global model, tokenizer, device
    
    try:
        logging.info('🚀 Starting GPT-OSS-20B initialization...')
        start_time = time.time()
        
        model_name = "openai/gpt-oss-20b"
        
        # Determine device
        if torch.cuda.is_available():
            device = "cuda"
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            logging.info(f'🔥 CUDA available! Using GPU: {gpu_name} (Count: {gpu_count})')
        else:
            device = "cpu"
            logging.info('💻 CUDA not available, using CPU')
        
        # Load tokenizer
        tokenizer_start = time.time()
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir='/app/cache'
        )
        
        # Set pad token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        tokenizer_time = time.time() - tokenizer_start
        logging.info(f'✅ Tokenizer loaded in {tokenizer_time:.2f} seconds')
        
        # Configure quantization for memory efficiency
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        
        # Load model with optimizations
        model_start = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            cache_dir='/app/cache',
            quantization_config=quantization_config if device == "cuda" else None
        )
        
        if device == "cpu":
            model = model.to(device)
            
        model_time = time.time() - model_start
        logging.info(f'✅ Model loaded in {model_time:.2f} seconds')
        
        # Log GPU memory usage
        if device == "cuda":
            gpu_info = get_gpu_info()
            for gpu in gpu_info:
                logging.info(f"   GPU {gpu['id']} ({gpu['name']}): {gpu['used_memory_mb']}MB / {gpu['total_memory_mb']}MB used")
        
        # Test model functionality
        logging.info('🧪 Testing model functionality...')
        test_input = tokenizer('Hello, I am', return_tensors='pt').to(device if device != "auto" else "cuda")
        
        with torch.no_grad():
            test_output = model.generate(
                **test_input, 
                max_new_tokens=10, 
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        
        test_text = tokenizer.decode(test_output[0], skip_special_tokens=True)
        logging.info(f'✅ Model test successful: "Hello, I am" -> "{test_text}"')
        
        total_time = time.time() - start_time
        logging.info(f'🎉 GPT-OSS-20B initialization complete! Total time: {total_time:.2f} seconds')
        
    except Exception as e:
        logging.error(f'❌ Model loading failed: {str(e)}')
        raise

@app.route('/', methods=['GET'])
def root():
    """API documentation and status"""
    return jsonify({
        'service': 'GrantSeeker AI - GPT-OSS-20B API',
        'version': '2.0.0',
        'status': 'healthy' if model is not None else 'model_not_loaded',
        'model': 'openai/gpt-oss-20b',
        'parameters': '20 billion',
        'description': 'AI-powered grant writing assistance using OpenAI GPT-OSS-20B',
        'endpoints': {
            '/health': 'GET - Check API and model status',
            '/generate': 'POST - Generate grant writing text from prompt',
            '/gpu-info': 'GET - Get GPU status and memory usage'
        },
        'usage': {
            'endpoint': '/generate',
            'method': 'POST',
            'body': {
                'prompt': 'Your grant writing prompt here',
                'max_new_tokens': 200,
                'temperature': 0.7
            }
        },
        'architecture': {
            'frontend': 'React + TypeScript + Tailwind CSS',
            'backend': 'Azure Functions + Python',
            'ai_model': 'Containerized GPT-OSS-20B (20B parameters)',
            'deployment': 'Azure Container Instances with GPU'
        },
        'hardware': {
            'device': device,
            'cuda_available': torch.cuda.is_available(),
            'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint with system info"""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    health_data = {
        'status': 'healthy',
        'service': 'GrantSeeker AI Model API',
        'model': 'gpt-oss-20b',
        'model_loaded': model is not None,
        'container_id': os.environ.get('HOSTNAME', 'unknown'),
        'timestamp': time.time(),
        'system_info': {
            'device': device,
            'cuda_available': torch.cuda.is_available(),
            'cpu_usage_percent': cpu_usage,
            'memory_usage_percent': memory.percent,
            'available_memory_gb': memory.available / (1024**3)
        }
    }
    
    # Add GPU info if available
    if torch.cuda.is_available():
        health_data['gpu_info'] = get_gpu_info()
    
    return jsonify(health_data)

@app.route('/gpu-info', methods=['GET'])
def gpu_info():
    """Detailed GPU information endpoint"""
    if not torch.cuda.is_available():
        return jsonify({
            'cuda_available': False,
            'message': 'CUDA not available on this system'
        })
    
    return jsonify({
        'cuda_available': True,
        'gpu_count': torch.cuda.device_count(),
        'gpus': get_gpu_info()
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Generate grant writing text using GPT-OSS-20B"""
    global model, tokenizer, device
    
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
                    'max_new_tokens': 200,
                    'temperature': 0.7
                }
            }), 400
            
        prompt = data['prompt']
        max_new_tokens = min(data.get('max_new_tokens', 200), 1000)  # Cap at 1000 for resource protection
        temperature = max(0.0, min(data.get('temperature', 0.7), 2.0))  # Clamp between 0 and 2
        
        logging.info('📥 Processing grant writing request')
        logging.info(f'🔄 Generating response for prompt: "{prompt[:100]}..."')
        logging.info(f'Parameters: max_tokens={max_new_tokens}, temp={temperature}')
        
        # Generate response
        start_time = time.time()
        
        inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=2048)
        inputs = {k: v.to(device if device != "auto" else "cuda") for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True if temperature > 0 else False,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1,
                top_p=0.9,
                top_k=50
            )
        
        # Decode only the new tokens (exclude input prompt)
        new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        generation_time = time.time() - start_time
        logging.info(f'✅ Generation completed in {generation_time:.2f} seconds')
        logging.info(f'Response length: {len(generated_text)} characters')
        
        # Log GPU memory usage after generation
        if torch.cuda.is_available():
            gpu_info = get_gpu_info()
            for gpu in gpu_info:
                logging.info(f"   Post-generation GPU {gpu['id']}: {gpu['used_memory_mb']}MB used")
        
        return jsonify({
            'generated_text': generated_text,
            'model': 'gpt-oss-20b',
            'success': True,
            'generation_time': generation_time,
            'prompt_length': len(prompt),
            'response_length': len(generated_text),
            'parameters': {
                'max_new_tokens': max_new_tokens,
                'temperature': temperature,
                'device': device
            },
            'metadata': {
                'service': 'GrantSeeker AI',
                'container_deployment': True,
                'timestamp': time.time(),
                'model_parameters': '20B'
            }
        })
        
    except Exception as e:
        logging.error(f'❌ Generation error: {str(e)}')
        return jsonify({
            'error': f'Generation failed: {str(e)}',
            'success': False,
            'model': 'gpt-oss-20b'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/', '/health', '/generate', '/gpu-info'],
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
    
    logging.info('🚀 Starting GrantSeeker AI Model API with GPT-OSS-20B...')
    
    # Load model on startup
    load_model()
    
    # Production deployment with Waitress (if available) or Flask dev server
    try:
        from waitress import serve
        logging.info('🌐 Starting production server with Waitress...')
        serve(app, host='0.0.0.0', port=8000, threads=2)  # Reduced threads for GPU memory
    except ImportError:
        logging.info('🌐 Starting Flask development server...')
        app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)