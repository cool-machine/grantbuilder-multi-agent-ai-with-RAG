#!/usr/bin/env python3
"""
Simple Test Model Flask API - Fast validation version
Uses a tiny model for quick container testing
"""
import logging
import time
import os
from flask import Flask, request, jsonify

# Configure logging - use stdout for container deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Simple mock model for testing
class SimpleTestModel:
    def __init__(self):
        self.name = "SimpleTestModel"
        self.loaded = True
        
    def generate(self, prompt, max_new_tokens=50, temperature=0.7):
        """Generate simple test response"""
        responses = [
            f"This is a test response for: {prompt}",
            f"Grant writing assistance for: {prompt}",
            f"AI-generated content based on: {prompt}",
            f"Professional response regarding: {prompt}"
        ]
        import random
        return random.choice(responses)

# Global model instance
model = None

def load_model():
    """Load simple test model (instant)"""
    global model
    
    try:
        logging.info('🚀 Starting Simple Test Model initialization...')
        start_time = time.time()
        
        # Instant "loading"
        model = SimpleTestModel()
        
        load_time = time.time() - start_time
        logging.info(f'✅ Simple Test Model loaded in {load_time:.2f} seconds')
        logging.info(f'🎯 Model ready for testing: {model.name}')
        
        return True
        
    except Exception as e:
        logging.error(f'❌ Failed to load Simple Test Model: {str(e)}')
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global model
    
    if model is None:
        return jsonify({
            'status': 'loading',
            'message': 'Model is still loading...',
            'model': 'SimpleTestModel'
        }), 503
    
    return jsonify({
        'status': 'healthy',
        'message': 'Simple Test Model API is ready',
        'model': model.name,
        'loaded': model.loaded,
        'endpoints': ['/health', '/generate'],
        'version': '1.0.0-test'
    }), 200

@app.route('/generate', methods=['POST'])
def generate_text():
    """Generate text using simple test model"""
    global model
    
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded yet',
            'message': 'Please wait for model initialization'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: prompt'
            }), 400
        
        prompt = data['prompt']
        max_new_tokens = data.get('max_new_tokens', 50)
        temperature = data.get('temperature', 0.7)
        
        logging.info(f'🎯 Generating response for prompt: {prompt[:100]}...')
        start_time = time.time()
        
        # Generate response
        generated_text = model.generate(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature
        )
        
        generation_time = time.time() - start_time
        
        response = {
            'success': True,
            'generated_text': generated_text,
            'prompt': prompt,
            'model': model.name,
            'generation_time': round(generation_time, 3),
            'parameters': {
                'max_new_tokens': max_new_tokens,
                'temperature': temperature
            }
        }
        
        logging.info(f'✅ Generated response in {generation_time:.3f} seconds')
        return jsonify(response), 200
        
    except Exception as e:
        logging.error(f'❌ Generation error: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Text generation failed'
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        'service': 'GrantSeeker AI - Simple Test API',
        'version': '1.0.0-test',
        'status': 'running',
        'model': 'SimpleTestModel',
        'description': 'Fast testing version for container validation',
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
                    'max_new_tokens': 'Number of tokens (optional, default: 50)',
                    'temperature': 'Creativity level (optional, default: 0.7)'
                }
            }
        }
    }), 200

if __name__ == '__main__':
    logging.info('🚀 Starting GrantSeeker AI Simple Test API...')
    
    # Load model
    if load_model():
        logging.info('✅ Simple Test Model loaded successfully')
    else:
        logging.error('❌ Failed to load Simple Test Model')
        exit(1)
    
    # Start Flask server
    logging.info('🌐 Starting Flask server on port 8000...')
    app.run(host='0.0.0.0', port=8000, debug=False)