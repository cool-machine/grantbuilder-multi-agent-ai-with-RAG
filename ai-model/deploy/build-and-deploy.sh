#!/bin/bash
# GrantSeeker AI - Container Build and Deployment Script
# Builds and deploys Gemma 3 270M-IT API to Azure Container Instances

set -e

# Configuration
RESOURCE_GROUP="ocp10"
CONTAINER_NAME="grantseeker-ai-api"
IMAGE_NAME="grantseeker-ai"
REGISTRY_NAME="def8f76bf0ee4d4e8cc860df6deb046c"  # Existing ACR from resource list
LOCATION="centralus"

echo "🚀 GrantSeeker AI - Container Deployment"
echo "========================================"

# Step 1: Build container image
echo "📦 Building container image..."
docker build -t $IMAGE_NAME:latest ../

# Step 2: Tag for Azure Container Registry
echo "🏷️  Tagging image for ACR..."
ACR_LOGIN_SERVER="${REGISTRY_NAME}.azurecr.io"
docker tag $IMAGE_NAME:latest $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

# Step 3: Push to Azure Container Registry
echo "⬆️  Pushing image to ACR..."
az acr login --name $REGISTRY_NAME
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

# Step 4: Deploy to Azure Container Instances
echo "🌐 Deploying to Azure Container Instances..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $REGISTRY_NAME \
    --registry-password $(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv) \
    --ip-address public \
    --ports 8000 \
    --memory 8 \
    --cpu 2 \
    --environment-variables \
        FLASK_ENV=production \
        PYTHONUNBUFFERED=1 \
    --restart-policy Always \
    --location $LOCATION

# Step 5: Get public IP and test
echo "✅ Deployment complete! Getting container info..."
CONTAINER_IP=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query ipAddress.ip -o tsv)

echo ""
echo "🎉 GrantSeeker AI API Deployed Successfully!"
echo "=========================================="
echo "Container Name: $CONTAINER_NAME"
echo "Public IP: $CONTAINER_IP"
echo "API Endpoints:"
echo "  Health Check: http://$CONTAINER_IP:8000/health"
echo "  Generate API: http://$CONTAINER_IP:8000/generate"
echo "  Documentation: http://$CONTAINER_IP:8000/"
echo ""
echo "Testing API availability..."
sleep 30  # Wait for container to start

if curl -s "http://$CONTAINER_IP:8000/health" > /dev/null; then
    echo "✅ API is responding!"
else
    echo "⚠️  API not yet available - container may still be starting"
    echo "Check logs with: az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
fi

echo ""
echo "🔗 Update Azure Functions environment variable:"
echo "AZURE_ML_GEMMA_ENDPOINT=http://$CONTAINER_IP:8000/generate"