#!/bin/bash

# Deploy GPT-OSS-20B to Azure Container Instances
# Requires GPU-enabled container instances

set -e

echo "🚀 Deploying GPT-OSS-20B to Azure Container Instances"
echo "=============================================="

# Configuration
RESOURCE_GROUP="ocp10"
CONTAINER_NAME="grantseeker-gpt-oss-20b"
REGISTRY_NAME="grantseekerregistry"
IMAGE_NAME="grantseeker-gpt-oss-20b:latest"
LOCATION="eastus"

# GPU Configuration
GPU_TYPE="K80"  # Options: K80, P100, V100
GPU_COUNT=1
CPU_CORES=4
MEMORY_GB=28

echo "📋 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Container Name: $CONTAINER_NAME"
echo "   GPU Type: $GPU_TYPE"
echo "   GPU Count: $GPU_COUNT"
echo "   Memory: ${MEMORY_GB}GB"
echo "   Location: $LOCATION"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

echo "🏗️  Building and pushing Docker image..."

# Build the Docker image
docker build -f Dockerfile.gpt-oss -t $IMAGE_NAME .

# Create ACR if it doesn't exist
if ! az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "🏗️  Creating Azure Container Registry..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $REGISTRY_NAME \
        --sku Basic \
        --location $LOCATION
fi

# Login to ACR
az acr login --name $REGISTRY_NAME

# Tag and push image
FULL_IMAGE_NAME="${REGISTRY_NAME}.azurecr.io/$IMAGE_NAME"
docker tag $IMAGE_NAME $FULL_IMAGE_NAME
docker push $FULL_IMAGE_NAME

echo "✅ Image pushed to: $FULL_IMAGE_NAME"

echo "🚀 Deploying container instance..."

# Delete existing container if it exists
if az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME &> /dev/null; then
    echo "🗑️  Deleting existing container instance..."
    az container delete \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_NAME \
        --yes
    
    echo "⏳ Waiting for deletion to complete..."
    sleep 30
fi

# Create new container instance with GPU
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $FULL_IMAGE_NAME \
    --cpu $CPU_CORES \
    --memory $MEMORY_GB \
    --gpu-type $GPU_TYPE \
    --gpu-count $GPU_COUNT \
    --dns-name-label $CONTAINER_NAME \
    --ports 8000 \
    --environment-variables \
        FLASK_ENV=production \
        HF_HOME=/app/cache \
        TRANSFORMERS_CACHE=/app/cache \
        PYTORCH_TRANSFORMERS_CACHE=/app/cache \
        CUDA_VISIBLE_DEVICES=0 \
    --registry-login-server "${REGISTRY_NAME}.azurecr.io" \
    --registry-username $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
    --registry-password $(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv) \
    --location $LOCATION

echo "⏳ Waiting for container to start..."
sleep 60

# Get container details
CONTAINER_IP=$(az container show \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --query ipAddress.ip \
    --output tsv)

CONTAINER_FQDN=$(az container show \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --query ipAddress.fqdn \
    --output tsv)

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "Container Name: $CONTAINER_NAME"
echo "Public IP: $CONTAINER_IP"
echo "FQDN: $CONTAINER_FQDN"
echo "API URL: http://$CONTAINER_FQDN:8000"
echo "Health Check: http://$CONTAINER_FQDN:8000/health"
echo ""
echo "💰 Estimated Cost:"
echo "   GPU ($GPU_TYPE): ~$0.90/hour"
echo "   CPU + Memory: ~$0.10/hour"
echo "   Total: ~$1.00/hour (~$24/day if running continuously)"
echo ""

# Test the endpoint
echo "🧪 Testing endpoint..."
sleep 30  # Give more time for model loading

if curl -f "http://$CONTAINER_FQDN:8000/health" &> /dev/null; then
    echo "✅ Health check passed!"
    
    # Test generation
    echo "🧪 Testing text generation..."
    curl -X POST "http://$CONTAINER_FQDN:8000/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "prompt": "Write a brief grant application response:",
            "max_new_tokens": 50,
            "temperature": 0.7
        }' | jq '.'
else
    echo "❌ Health check failed. Check container logs:"
    echo "   az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
fi

echo ""
echo "📋 Useful Commands:"
echo "   View logs: az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo "   Restart: az container restart --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo "   Delete: az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes"
echo ""
echo "🔧 Update backend environment variable:"
echo "   AZURE_ML_GPT_OSS_ENDPOINT=http://$CONTAINER_FQDN:8000/generate"