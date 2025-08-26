#!/bin/bash

# Deploy GPT-OSS-20B to Azure Container Instances using CPU (for initial testing)
# This version uses CPU with aggressive quantization

set -e

echo "🚀 Deploying GPT-OSS-20B to Azure Container Instances (CPU Version)"
echo "================================================================="

# Configuration
RESOURCE_GROUP="ocp10"
CONTAINER_NAME="grantseeker-gpt-oss-20b-cpu"
REGISTRY_NAME="def8f76bf0ee4d4e8cc860df6deb046c"
IMAGE_NAME="grantseeker-gpt-oss-20b-cpu"
LOCATION="eastus"

# CPU Configuration (Large CPU instance)
CPU_CORES=8
MEMORY_GB=32

echo "📋 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Container Name: $CONTAINER_NAME"
echo "   Registry: $REGISTRY_NAME"
echo "   CPU Cores: $CPU_CORES"
echo "   Memory: ${MEMORY_GB}GB"
echo "   Mode: CPU with quantization"
echo ""

# Check Azure CLI login
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

echo "🏗️  Building CPU-optimized image in Azure Container Registry..."

# Build and push using ACR Tasks (cloud build)
az acr build \
    --registry $REGISTRY_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $IMAGE_NAME:latest \
    --file Dockerfile.gpt-oss-cpu \
    .

echo "✅ Image built and pushed to ACR"

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

echo "🚀 Creating CPU-optimized container instance..."

# Get registry credentials
REGISTRY_LOGIN_SERVER="${REGISTRY_NAME}.azurecr.io"
REGISTRY_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
REGISTRY_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Create container instance with large CPU allocation
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image "${REGISTRY_LOGIN_SERVER}/${IMAGE_NAME}:latest" \
    --cpu $CPU_CORES \
    --memory $MEMORY_GB \
    --os-type Linux \
    --dns-name-label $CONTAINER_NAME \
    --ports 8000 \
    --environment-variables \
        FLASK_ENV=production \
        HF_HOME=/app/cache \
        TRANSFORMERS_CACHE=/app/cache \
        PYTORCH_TRANSFORMERS_CACHE=/app/cache \
        CUDA_VISIBLE_DEVICES=-1 \
        OMP_NUM_THREADS=8 \
    --registry-login-server $REGISTRY_LOGIN_SERVER \
    --registry-username $REGISTRY_USERNAME \
    --registry-password $REGISTRY_PASSWORD \
    --location $LOCATION

echo "⏳ Waiting for container to start..."
sleep 120

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

# Test the endpoint
echo "🧪 Testing endpoint (model loading may take 5-10 minutes)..."
sleep 60

echo "Testing health endpoint..."
for i in {1..5}; do
    if curl -f -m 30 "http://$CONTAINER_FQDN:8000/health" &> /dev/null; then
        echo "✅ Health check passed!"
        break
    else
        echo "⏳ Attempt $i/5: Model still loading... (waiting 60s)"
        sleep 60
    fi
done

echo ""
echo "📋 Next Steps:"
echo "1. Update Azure Functions environment variable:"
echo "   AZURE_ML_GPT_OSS_ENDPOINT=http://$CONTAINER_FQDN:8000/generate"
echo ""
echo "2. Test text generation:"
echo '   curl -X POST "http://'$CONTAINER_FQDN':8000/generate" \'
echo '     -H "Content-Type: application/json" \'
echo '     -d "{\"prompt\": \"Write a grant application:\", \"max_new_tokens\": 100}"'
echo ""
echo "💡 Note: This is the CPU version for testing. GPU version available later."
echo ""
echo "📋 Management Commands:"
echo "   View logs: az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo "   Restart: az container restart --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo "   Delete: az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes"