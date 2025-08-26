#!/usr/bin/env python3
"""
Deploy GPT-OSS-20B from Azure ML Model Catalog
Alternative to Azure OpenAI Service
"""

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint, 
    ManagedOnlineDeployment, 
    Model,
    Environment,
    CodeConfiguration
)
from azure.identity import DefaultAzureCredential
import time

def deploy_gpt_oss_20b():
    """Deploy GPT-OSS-20B as managed online endpoint"""
    
    # Initialize ML client
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id="<your-subscription-id>",  # Replace with your subscription
        resource_group_name="ocp10",
        workspace_name="ocp10"
    )
    
    print("🚀 Deploying GPT-OSS-20B from Azure ML Model Catalog")
    print("="*60)
    
    # Step 1: Create endpoint
    endpoint_name = "gpt-oss-20b-endpoint"
    
    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description="GPT-OSS-20B deployment for model testing",
        auth_mode="key"
    )
    
    print(f"📡 Creating endpoint: {endpoint_name}")
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    
    # Step 2: Get the model from catalog
    model = Model(
        name="gpt-oss-20b-cuda-gpu",
        version="1",
        type="mlflow_model"
    )
    
    # Step 3: Create deployment
    deployment = ManagedOnlineDeployment(
        name="gpt-oss-deployment",
        endpoint_name=endpoint_name,
        model=f"azureml://registries/azureml/models/gpt-oss-20b-cuda-gpu/versions/1",
        instance_type="Standard_NC6s_v3",  # Tesla V100 GPU
        instance_count=1,
        environment_variables={
            "AZUREML_MODEL_DIR": "/var/azureml-app/azureml-models/gpt-oss-20b-cuda-gpu/1"
        }
    )
    
    print(f"🔧 Creating deployment on Standard_NC6s_v3 (Tesla V100)")
    print(f"   This will cost approximately $3.00-4.00/hour when running")
    
    # Deploy (this takes 10-15 minutes)
    print("⏳ Deployment starting... (this takes 10-15 minutes)")
    ml_client.online_deployments.begin_create_or_update(deployment).result()
    
    # Set traffic to 100% for this deployment
    endpoint.traffic = {"gpt-oss-deployment": 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    
    print("✅ GPT-OSS-20B deployment complete!")
    
    # Get endpoint details
    endpoint = ml_client.online_endpoints.get(name=endpoint_name)
    
    print(f"📋 Endpoint Details:")
    print(f"   Name: {endpoint.name}")
    print(f"   Scoring URI: {endpoint.scoring_uri}")
    print(f"   Auth: Key-based")
    
    # Get the key
    keys = ml_client.online_endpoints.get_keys(name=endpoint_name)
    print(f"   Primary Key: {keys.primary_key}")
    
    return {
        "endpoint_name": endpoint_name,
        "scoring_uri": endpoint.scoring_uri,
        "auth_key": keys.primary_key
    }

def test_endpoint(scoring_uri, auth_key):
    """Test the deployed endpoint"""
    import requests
    import json
    
    print("\n🧪 Testing GPT-OSS-20B endpoint...")
    
    # Test payload
    test_data = {
        "input_data": {
            "input_string": [
                "Write a professional grant application response: How does your organization's mission align with educational technology funding?"
            ],
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_key}"
    }
    
    try:
        response = requests.post(scoring_uri, json=test_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test successful!")
            print(f"Response: {result}")
        else:
            print(f"❌ Test failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

def get_cost_estimate():
    """Show cost estimates"""
    print("\n💰 Cost Analysis for GPT-OSS-20B Deployment:")
    print("="*50)
    print("Instance: Standard_NC6s_v3 (Tesla V100)")
    print("Cost: ~$3.60/hour")
    print()
    print("Usage scenarios:")
    print("• Always on: $3.60 × 24 × 30 = $2,592/month")
    print("• 8 hours/day: $3.60 × 8 × 30 = $864/month") 
    print("• 2 hours/day: $3.60 × 2 × 30 = $216/month")
    print()
    print("Compare to Azure OpenAI GPT-3.5:")
    print("• 1000 requests/month: ~$500")
    print("• 10000 requests/month: ~$5000")
    print()
    print("💡 Recommendation: Use Azure ML endpoint for high-volume testing")
    print("   Use Azure OpenAI for production/low-volume usage")

if __name__ == "__main__":
    print("🔧 GPT-OSS-20B Deployment Script")
    print("="*40)
    print()
    print("This will deploy GPT-OSS-20B as an Azure ML managed endpoint.")
    print("Requirements:")
    print("• GPU instance (Standard_NC6s_v3 minimum)")
    print("• Cost: ~$3.60/hour when running")
    print()
    
    choice = input("Proceed with deployment? (y/n): ")
    
    if choice.lower() == 'y':
        # Show cost estimate first
        get_cost_estimate()
        
        confirm = input("\nProceed with deployment? (y/n): ")
        if confirm.lower() == 'y':
            try:
                # Deploy
                endpoint_info = deploy_gpt_oss_20b()
                
                # Test
                test_endpoint(endpoint_info['scoring_uri'], endpoint_info['auth_key'])
                
                print(f"\n🎉 Success! GPT-OSS-20B is now available at:")
                print(f"   {endpoint_info['scoring_uri']}")
                
            except Exception as e:
                print(f"❌ Deployment failed: {str(e)}")
        else:
            print("⏹️  Deployment cancelled")
    else:
        print("⏹️  Deployment cancelled")
        get_cost_estimate()