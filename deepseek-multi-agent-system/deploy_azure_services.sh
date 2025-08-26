#!/bin/bash

# Azure Services Deployment Script for DeepSeek R1 Multi-Agent Grant Writing System
# Uses your existing Azure credits - no additional costs

set -e

# Configuration
RESOURCE_GROUP="ocp10"
LOCATION="eastus2" 
SUBSCRIPTION_ID="f2c67079-16e2-4ab7-82ee-0c438d92b95e"

echo "🚀 Deploying Azure Services for DeepSeek R1 Multi-Agent System..."
echo "💳 Using existing Azure credits from resource group: $RESOURCE_GROUP"

# Set subscription
az account set --subscription $SUBSCRIPTION_ID

# 1. Azure Storage Account (for MCP collaboration tools)
echo "📦 Creating Azure Storage Account..."
STORAGE_ACCOUNT="grantagentstorage$(date +%s | tail -c 5)"
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# Get storage key
STORAGE_KEY=$(az storage account keys list \
  --resource-group $RESOURCE_GROUP \
  --account-name $STORAGE_ACCOUNT \
  --query '[0].value' -o tsv)

# Create containers
az storage container create --name "shared-artifacts" --account-name $STORAGE_ACCOUNT --account-key $STORAGE_KEY
az storage container create --name "workflow-checkpoints" --account-name $STORAGE_ACCOUNT --account-key $STORAGE_KEY

echo "✅ Storage Account created: $STORAGE_ACCOUNT"

# 2. Azure Cosmos DB (for collaboration tasks and state management)
echo "🌐 Creating Azure Cosmos DB..."
COSMOS_ACCOUNT="grantagents-cosmos-$(date +%s | tail -c 5)"
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --locations regionName=$LOCATION \
  --default-consistency-level Session \
  --enable-free-tier true

# Create database and containers
az cosmosdb sql database create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --name "GrantCollaboration"

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --database-name "GrantCollaboration" \
  --name "CollaborationTasks" \
  --partition-key-path "/requester" \
  --throughput 400

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --database-name "GrantCollaboration" \
  --name "SharedArtifacts" \
  --partition-key-path "/creator" \
  --throughput 400

# Get Cosmos DB connection details
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query "documentEndpoint" -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query "primaryMasterKey" -o tsv)

echo "✅ Cosmos DB created: $COSMOS_ACCOUNT"

# 3. Azure Service Bus (for real-time agent communication)
echo "📨 Creating Azure Service Bus..."
SERVICE_BUS_NAMESPACE="grantagents-bus-$(date +%s | tail -c 5)"
az servicebus namespace create \
  --resource-group $RESOURCE_GROUP \
  --name $SERVICE_BUS_NAMESPACE \
  --location $LOCATION \
  --sku Basic

# Create queue for agent notifications
az servicebus queue create \
  --resource-group $RESOURCE_GROUP \
  --namespace-name $SERVICE_BUS_NAMESPACE \
  --name "agent-notifications" \
  --max-size 1024

# Get Service Bus connection string
SERVICE_BUS_CONNECTION=$(az servicebus namespace authorization-rule keys list \
  --resource-group $RESOURCE_GROUP \
  --namespace-name $SERVICE_BUS_NAMESPACE \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString -o tsv)

echo "✅ Service Bus created: $SERVICE_BUS_NAMESPACE"

# 4. Azure Cognitive Search (for MCP research tools)
echo "🔍 Creating Azure Cognitive Search..."
SEARCH_SERVICE="grantagents-search-$(date +%s | tail -c 5)"
az search service create \
  --name $SEARCH_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku free

# Get search admin key
SEARCH_KEY=$(az search admin-key show \
  --resource-group $RESOURCE_GROUP \
  --service-name $SEARCH_SERVICE \
  --query "primaryKey" -o tsv)

SEARCH_ENDPOINT="https://$SEARCH_SERVICE.search.windows.net"

echo "✅ Cognitive Search created: $SEARCH_SERVICE"

# 5. Azure AI Language Service (for MCP validation tools)
echo "🧠 Creating Azure AI Language Service..."
LANGUAGE_SERVICE="grantagents-language-$(date +%s | tail -c 5)"
az cognitiveservices account create \
  --name $LANGUAGE_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --kind TextAnalytics \
  --sku S0 \
  --yes

# Get language service key
LANGUAGE_KEY=$(az cognitiveservices account keys list \
  --name $LANGUAGE_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --query "key1" -o tsv)

LANGUAGE_ENDPOINT="https://$LOCATION.api.cognitive.microsoft.com/"

echo "✅ AI Language Service created: $LANGUAGE_SERVICE"

# 6. Azure Bing Search (for MCP research tools)
echo "🌐 Creating Azure Bing Search..."
BING_SEARCH="grantagents-bing-$(date +%s | tail -c 5)"
az cognitiveservices account create \
  --name $BING_SEARCH \
  --resource-group $RESOURCE_GROUP \
  --location global \
  --kind Bing.Search.v7 \
  --sku S1 \
  --yes

# Get Bing search key
BING_KEY=$(az cognitiveservices account keys list \
  --name $BING_SEARCH \
  --resource-group $RESOURCE_GROUP \
  --query "key1" -o tsv)

echo "✅ Bing Search created: $BING_SEARCH"

# 7. Create environment configuration file
echo "📝 Creating environment configuration..."
cat > azure_services_config.env << EOF
# Azure Services Configuration for DeepSeek R1 Multi-Agent System
# Generated: $(date)

# DeepSeek R1 Serverless Endpoint (Already deployed)
DEEPSEEK_R1_ENDPOINT=https://deepseek-r1-reasoning.eastus2.models.ai.azure.com
DEEPSEEK_R1_API_KEY=YbBP7lxFmBWiYcoVnr3JwHCVpm20fyUF

# Azure Storage (Collaboration artifacts)
AZURE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT
AZURE_STORAGE_KEY=$STORAGE_KEY
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=$STORAGE_ACCOUNT;AccountKey=$STORAGE_KEY;EndpointSuffix=core.windows.net

# Azure Cosmos DB (Task management)
AZURE_COSMOS_ENDPOINT=$COSMOS_ENDPOINT
AZURE_COSMOS_KEY=$COSMOS_KEY

# Azure Service Bus (Real-time messaging)
AZURE_SERVICEBUS_CONNECTION=$SERVICE_BUS_CONNECTION

# Azure Cognitive Search (Research tools)
AZURE_SEARCH_ENDPOINT=$SEARCH_ENDPOINT
AZURE_SEARCH_KEY=$SEARCH_KEY

# Azure AI Language (Validation tools)
AZURE_LANGUAGE_ENDPOINT=$LANGUAGE_ENDPOINT
AZURE_LANGUAGE_KEY=$LANGUAGE_KEY

# Azure Bing Search (Research tools)
AZURE_BING_SEARCH_KEY=$BING_KEY

# System Configuration
AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID
AZURE_RESOURCE_GROUP=$RESOURCE_GROUP
AZURE_LOCATION=$LOCATION
EOF

echo ""
echo "🎉 AZURE SERVICES DEPLOYMENT COMPLETE!"
echo ""
echo "📊 Services Created:"
echo "  ✅ Storage Account: $STORAGE_ACCOUNT"
echo "  ✅ Cosmos DB: $COSMOS_ACCOUNT" 
echo "  ✅ Service Bus: $SERVICE_BUS_NAMESPACE"
echo "  ✅ Cognitive Search: $SEARCH_SERVICE"
echo "  ✅ AI Language: $LANGUAGE_SERVICE"
echo "  ✅ Bing Search: $BING_SEARCH"
echo ""
echo "💰 Estimated Monthly Cost: $15-50 (covered by your Azure credits)"
echo "📄 Configuration saved to: azure_services_config.env"
echo ""
echo "🚀 Ready to deploy the multi-agent system!"
echo "   Run: python integrated_deepseek_mcp_system.py"