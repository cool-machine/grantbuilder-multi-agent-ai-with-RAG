# 🔐 GitHub Secrets Configuration

This document outlines all the required GitHub repository secrets for automated deployment.

## Required Secrets

### 1. Azure Authentication

#### `AZURE_CREDENTIALS`
Azure service principal credentials for resource access.

**Format**: JSON
```json
{
  "clientId": "your-service-principal-client-id",
  "clientSecret": "your-service-principal-secret",
  "subscriptionId": "f2c67079-16e2-4ab7-82ee-0c438d92b95e",
  "tenantId": "87725b4f-d4d4-4c30-88b0-91027518be30"
}
```

**How to get**:
```bash
# Create service principal with contributor access
az ad sp create-for-rbac \
  --name "grantseeker-github-actions" \
  --role contributor \
  --scopes /subscriptions/f2c67079-16e2-4ab7-82ee-0c438d92b95e/resourceGroups/ocp10 \
  --sdk-auth
```

#### `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
Azure Functions publish profile for deployment.

**How to get**:
```bash
# Download publish profile
az functionapp deployment list-publishing-profiles \
  --name ocp10-grant-functions \
  --resource-group ocp10 \
  --xml
```

**Alternative**: Download from Azure Portal:
1. Go to Azure Functions → ocp10-grant-functions
2. Click "Get publish profile"
3. Copy entire XML content

### 2. Container Registry Access

GitHub Actions automatically uses Azure credentials for ACR access via `az acr login`.

### 3. API Configuration

#### `GEMMA_API_ENDPOINT` (Optional)
Default AI model endpoint URL. Auto-updated by container deployment.

**Format**: `http://CONTAINER_IP:8000/generate`

#### `GEMMA_API_KEY` (Optional)
API key for AI model access (if authentication is added).

## Setup Instructions

### 1. Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name and value

### 2. Required Repository Secrets

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `AZURE_CREDENTIALS` | Service principal JSON | ✅ Yes |
| `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` | Functions publish profile | ✅ Yes |
| `GEMMA_API_ENDPOINT` | AI model endpoint URL | ⚠️ Optional |
| `GEMMA_API_KEY` | AI model API key | ⚠️ Optional |

### 3. Verify Service Principal Permissions

```bash
# Test service principal access
az login --service-principal \
  --username "your-client-id" \
  --password "your-client-secret" \
  --tenant "87725b4f-d4d4-4c30-88b0-91027518be30"

# Test resource group access
az group show --name ocp10

# Test function app access
az functionapp show --name ocp10-grant-functions --resource-group ocp10

# Test container registry access
az acr show --name def8f76bf0ee4d4e8cc860df6deb046c --resource-group ocp10
```

## Environment-Specific Configuration

### Production Environment
- All secrets required
- Automatic deployment on `main` branch push
- Full health checks and monitoring

### Staging Environment (Optional)
Create environment-specific secrets:
- `AZURE_CREDENTIALS_STAGING`
- `AZURE_FUNCTIONAPP_PUBLISH_PROFILE_STAGING`

## Security Best Practices

### 1. Least Privilege Access
Service principal has minimal required permissions:
- **Scope**: Limited to `ocp10` resource group
- **Role**: Contributor (can manage resources, not permissions)
- **Duration**: No expiration (can be rotated)

### 2. Secret Rotation
Rotate secrets regularly:
```bash
# Generate new service principal secret
az ad sp credential reset --name "grantseeker-github-actions"

# Update GitHub repository secret
```

### 3. Monitoring
Monitor deployment activities:
- Azure Activity Log for resource changes
- GitHub Actions logs for deployment status
- Function App logs for runtime issues

## Troubleshooting

### Common Issues

#### 1. Authentication Failed
```
Error: Failed to authenticate with Azure
```

**Solution**:
1. Verify `AZURE_CREDENTIALS` JSON format
2. Check service principal hasn't expired
3. Ensure correct subscription ID and tenant ID

#### 2. Insufficient Permissions
```
Error: The client does not have authorization to perform action
```

**Solution**:
1. Verify service principal has Contributor role
2. Check scope includes the resource group
3. Ensure subscription is active

#### 3. Publish Profile Invalid
```
Error: Failed to deploy to Azure Functions
```

**Solution**:
1. Download fresh publish profile from Azure Portal
2. Verify function app name matches workflow
3. Check resource group and subscription

### Debug Commands

```bash
# Test Azure CLI login with service principal
az login --service-principal --username $CLIENT_ID --password $CLIENT_SECRET --tenant $TENANT_ID

# List available function apps
az functionapp list --resource-group ocp10 --query "[].{Name:name, State:state}" --output table

# Check container registry access
az acr repository list --name def8f76bf0ee4d4e8cc860df6deb046c
```

## Automatic Updates

The deployment workflows automatically:
1. **Update API endpoints** when container IP changes
2. **Configure app settings** with new environment variables
3. **Test connectivity** between components
4. **Verify health** of all services

This ensures the platform maintains integration without manual intervention.