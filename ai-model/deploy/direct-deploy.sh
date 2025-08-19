#!/bin/bash
# GrantSeeker AI - Direct Container Deployment Script
# Deploys container directly to Azure Container Instances without registry

set -e

# Configuration
RESOURCE_GROUP="ocp10"
CONTAINER_NAME="grantseeker-ai-api"
LOCATION="centralus"

echo "🚀 GrantSeeker AI - Direct Container Deployment"
echo "==============================================="

# Deploy directly from GitHub or local files
echo "🌐 Creating Azure Container Instance..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image python:3.10-slim \
    --os-type Linux \
    --ip-address public \
    --ports 8000 \
    --memory 8 \
    --cpu 2 \
    --environment-variables \
        FLASK_ENV=production \
        PYTHONUNBUFFERED=1 \
        HF_HOME=/app/cache \
    --restart-policy Always \
    --location $LOCATION \
    --command-line "bash -c '
        apt-get update && 
        apt-get install -y git curl && 
        pip install Flask==3.0.0 torch==2.4.0 transformers==4.44.0 accelerate==0.33.0 huggingface-hub==0.24.0 requests==2.31.0 &&
        mkdir -p /app/logs /app/cache &&
        cat > /app/flask_api.py << \"EOF\"
import logging, time, torch
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)
model, tokenizer = None, None

def load_model():
    global model, tokenizer
    try:
        logging.info(\"Loading Gemma 3 270M-IT...\")
        model_name = \"google/gemma-3-270m-it\"
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, cache_dir=\"/app/cache\")
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32, trust_remote_code=True, low_cpu_mem_usage=True, cache_dir=\"/app/cache\")
        logging.info(\"Model loaded successfully\")
    except Exception as e:
        logging.error(f\"Model loading failed: {e}\")

@app.route(\"/\", methods=[\"GET\"])
def root():
    return jsonify({\"service\": \"GrantSeeker AI - Gemma 3 270M-IT\", \"status\": \"healthy\" if model else \"loading\", \"endpoints\": {\"/health\": \"GET\", \"/generate\": \"POST\"}})

@app.route(\"/health\", methods=[\"GET\"])
def health():
    return jsonify({\"status\": \"healthy\", \"model\": \"gemma-3-270m-it\", \"model_loaded\": model is not None, \"timestamp\": time.time()})

@app.route(\"/generate\", methods=[\"POST\"])
def generate():
    if not model or not tokenizer:
        return jsonify({\"error\": \"Model not loaded\", \"success\": False}), 503
    try:
        data = request.json
        if not data or \"prompt\" not in data:
            return jsonify({\"error\": \"Missing prompt\", \"success\": False}), 400
        prompt = data[\"prompt\"]
        max_new_tokens = min(data.get(\"max_new_tokens\", 100), 300)
        temperature = max(0, min(data.get(\"temperature\", 0.7), 2))
        
        inputs = tokenizer(prompt, return_tensors=\"pt\")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=temperature, do_sample=temperature > 0, pad_token_id=tokenizer.eos_token_id)
        new_tokens = outputs[0][inputs[\"input_ids\"].shape[1]:]
        generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        return jsonify({\"generated_text\": generated_text, \"model\": \"gemma-3-270m-it\", \"success\": True})
    except Exception as e:
        return jsonify({\"error\": f\"Generation failed: {str(e)}\", \"success\": False}), 500

if __name__ == \"__main__\":
    logging.basicConfig(level=logging.INFO)
    load_model()
    app.run(host=\"0.0.0.0\", port=8000, debug=False)
EOF
        python /app/flask_api.py
    '"

echo "⏳ Container deployment initiated..."
echo "This may take 5-10 minutes for model download and initialization..."

# Wait for container to be created
sleep 30

# Get public IP
CONTAINER_IP=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query ipAddress.ip -o tsv)

echo ""
echo "🎉 GrantSeeker AI API Deployment Started!"
echo "========================================"
echo "Container Name: $CONTAINER_NAME"
echo "Public IP: $CONTAINER_IP"
echo "API Endpoints (will be available in 5-10 minutes):"
echo "  Health Check: http://$CONTAINER_IP:8000/health"
echo "  Generate API: http://$CONTAINER_IP:8000/generate"
echo "  Documentation: http://$CONTAINER_IP:8000/"
echo ""
echo "Monitor deployment logs:"
echo "az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --follow"
echo ""
echo "🔗 Once ready, update Azure Functions environment variable:"
echo "AZURE_ML_GEMMA_ENDPOINT=http://$CONTAINER_IP:8000/generate"