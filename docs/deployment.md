# 🚀 GrantSeeker AI Platform - Deployment Guide

Complete deployment guide for the GrantSeeker AI Platform with automated CI/CD using GitHub Actions.

## 📋 Deployment Overview

The platform uses a **multi-tier deployment strategy**:

```
GitHub Repository → GitHub Actions → Multi-Target Deployment
├── 🌐 Frontend → GitHub Pages (Static hosting)
├── ⚡ Backend → Azure Functions (Serverless API)  
└── 🤖 AI Model → Azure Container Instances (Containerized AI)
```

## 🎯 Quick Deployment

### Prerequisites
- ✅ Azure subscription with active credits
- ✅ GitHub repository with Actions enabled
- ✅ Azure CLI installed locally (for initial setup)

### One-Time Setup

1. **Fork/Clone Repository**
   ```bash
   git clone https://github.com/your-username/grantseeker-ai-platform.git
   cd grantseeker-ai-platform
   ```

2. **Configure GitHub Secrets**
   - Follow [GitHub Secrets Setup Guide](github-secrets-setup.md)
   - Add required Azure credentials and publish profiles

3. **Enable GitHub Pages**
   - Go to Repository Settings → Pages
   - Source: GitHub Actions
   - The workflow will handle the rest

### Automatic Deployment

Once configured, the platform deploys automatically:

- **Frontend**: On changes to `frontend/` directory
- **Backend**: On changes to `backend/` directory  
- **AI Model**: On changes to `ai-model/` directory

## 🔄 Deployment Workflows

### 1. Frontend Deployment (`deploy-frontend.yml`)

**Trigger**: Changes to `frontend/**` or manual dispatch

**Process**:
```
1. 📦 Install Node.js dependencies
2. 🔍 Run linting and tests
3. 🏗️ Build React application
4. 🌐 Deploy to GitHub Pages
5. ✅ Health check deployed site
```

**Output**: Live website at `https://your-username.github.io/grantseeker-ai-platform/`

### 2. Backend Deployment (`deploy-backend.yml`)

**Trigger**: Changes to `backend/**` or manual dispatch

**Process**:
```
1. 🐍 Setup Python environment
2. 📦 Install Azure Functions dependencies
3. 🧪 Run tests and linting
4. ⚡ Deploy to Azure Functions
5. 🔧 Configure app settings
6. ✅ Verify function endpoints
```

**Output**: Live API at `https://ocp10-grant-functions.azurewebsites.net/api/`

### 3. AI Model Deployment (`deploy-container.yml`)

**Trigger**: Changes to `ai-model/**` or manual dispatch

**Process**:
```
1. 🐳 Build container image with ACR
2. 🔒 Security scan (optional)
3. 🚀 Deploy to Azure Container Instances
4. 🧪 Health check and AI functionality test
5. 🔗 Update backend with new endpoint
6. ✅ End-to-end integration test
```

**Output**: Live AI API at `http://CONTAINER_IP:8000/`

## 📊 Deployment Status

### Success Indicators
- ✅ **All workflows complete** without errors
- ✅ **Green checkmarks** on all deployment jobs
- ✅ **Health checks pass** for all components
- ✅ **Integration tests successful**

### Monitoring Deployments

```bash
# View Azure Functions logs
az functionapp logs tail --name ocp10-grant-functions --resource-group ocp10

# View Container logs  
az container logs --resource-group ocp10 --name grantseeker-ai-api --follow

# Test endpoints
curl https://ocp10-grant-functions.azurewebsites.net/api/TokenizerFunction?text=hello
curl http://CONTAINER_IP:8000/health
```

## 🛠️ Manual Deployment

If GitHub Actions aren't available, deploy manually:

### Frontend (Manual)
```bash
cd frontend
npm install
npm run build
# Deploy dist/ folder to any static hosting
```

### Backend (Manual)
```bash
cd backend
func azure functionapp publish ocp10-grant-functions --python
```

### AI Model (Manual)
```bash
cd ai-model
./deploy/build-and-deploy.sh
# Or use direct-deploy.sh for simpler setup
```

## 🔧 Configuration

### Environment Variables

#### Frontend (.env)
```bash
VITE_AZURE_FUNCTIONS_URL=https://ocp10-grant-functions.azurewebsites.net/api
VITE_API_BASE_URL=https://ocp10-grant-functions.azurewebsites.net/api
```

#### Backend (App Settings)
```bash
AZURE_ML_GEMMA_ENDPOINT=http://CONTAINER_IP:8000/generate
AZURE_ML_GEMMA_KEY=optional-api-key
PYTHONPATH=/home/site/wwwroot
FUNCTIONS_WORKER_RUNTIME=python
```

#### AI Model (Container Environment)
```bash
FLASK_ENV=production
PYTHONUNBUFFERED=1
HF_HOME=/app/cache
TRANSFORMERS_CACHE=/app/cache
```

## 📈 Scaling and Optimization

### Development → Production

#### Development
- **Frontend**: Local dev server (`npm run dev`)
- **Backend**: Local Functions runtime (`func start`)
- **AI Model**: Local Docker container
- **Cost**: $0 (local development)

#### Production  
- **Frontend**: GitHub Pages (CDN distributed)
- **Backend**: Azure Functions Consumption Plan
- **AI Model**: Azure Container Instances (8GB RAM)
- **Cost**: ~$30-50/month

### Performance Optimization

#### Frontend
- ✅ **Build optimization** with Vite
- ✅ **Code splitting** for lazy loading
- ✅ **CDN distribution** via GitHub Pages
- ✅ **Caching strategies** for API calls

#### Backend
- ✅ **Cold start optimization** with proper dependencies
- ✅ **Connection pooling** for external services
- ✅ **Error handling** and retry logic
- ✅ **Request/response caching**

#### AI Model
- ✅ **Model caching** in container storage
- ✅ **CPU optimization** with PyTorch CPU builds
- ✅ **Memory optimization** with low_cpu_mem_usage
- ✅ **Request batching** for efficiency

### Scaling Options

#### Horizontal Scaling
- **Frontend**: Automatic via GitHub Pages CDN
- **Backend**: Automatic with Azure Functions  
- **AI Model**: Multiple container instances + load balancer

#### Vertical Scaling
- **Backend**: Upgrade to Premium Functions plan
- **AI Model**: Increase container CPU/memory (up to 14GB)

## 🧪 Testing Deployments

### Automated Tests
Each deployment includes:
- ✅ **Unit tests** for components
- ✅ **Integration tests** between services
- ✅ **Health checks** for all endpoints
- ✅ **End-to-end tests** for complete workflows

### Manual Testing Checklist
```bash
# 1. Frontend accessibility
curl https://your-username.github.io/grantseeker-ai-platform/

# 2. Backend API endpoints
curl https://ocp10-grant-functions.azurewebsites.net/api/TokenizerFunction?text=test

# 3. AI model functionality
curl -X POST http://CONTAINER_IP:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test AI generation", "max_new_tokens": 20}'

# 4. Complete integration
# Test full grant form filling workflow through UI
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Frontend Build Fails
```
Error: Module not found
```
**Solution**: Check `package.json` dependencies and Node.js version

#### 2. Backend Deployment Fails  
```
Error: Failed to authenticate with Azure
```
**Solution**: Verify `AZURE_CREDENTIALS` secret format and permissions

#### 3. Container Deployment Timeout
```
Error: Container failed to start
```
**Solution**: Check container logs, may need more time for model download

#### 4. Integration Failure
```
Error: Cannot connect to AI model
```
**Solution**: Verify container IP updated in backend app settings

### Debug Commands

```bash
# Check GitHub Actions logs
# Go to repository → Actions tab → Select workflow run

# Check Azure resources status
az resource list --resource-group ocp10 --query "[].{Name:name, Type:type, State:state}" --output table

# Test component connectivity
curl -f https://ocp10-grant-functions.azurewebsites.net/api/GemmaProxy || echo "Backend connectivity issue"
```

## 📊 Cost Monitoring

### Monthly Cost Breakdown
| Component | Service | Estimated Cost |
|-----------|---------|----------------|
| Frontend | GitHub Pages | Free |
| Backend | Azure Functions | $0-10 |
| AI Model | Container Instances (8GB) | $30-50 |
| Storage | Azure Storage | $1-5 |
| **Total** | **Complete Platform** | **$31-65/month** |

### Cost Optimization Tips
- ✅ **Auto-shutdown**: Container stops when idle
- ✅ **Consumption pricing**: Pay only for function executions
- ✅ **Efficient caching**: Reduce redundant API calls
- ✅ **Resource monitoring**: Track usage patterns

## 🔄 Updates and Maintenance

### Automatic Updates
- **Dependencies**: Dependabot PRs for security updates
- **Container images**: Weekly automated rebuilds
- **Function runtime**: Automatic Azure platform updates

### Manual Updates
- **AI model**: Update `ai-model/` code and push
- **API endpoints**: Modify `backend/` functions and push  
- **UI changes**: Update `frontend/` components and push

### Backup and Recovery
- **Code**: Git repository (distributed backup)
- **Configuration**: Documented in deployment files
- **Data**: No persistent data stored (stateless architecture)

---

## 🎉 Deployment Complete!

Once all workflows succeed, you'll have:
- ✅ **Live website** with professional UI
- ✅ **Scalable API** with Azure Functions
- ✅ **AI-powered backend** with containerized model
- ✅ **Automated deployments** for future updates
- ✅ **Cost-effective solution** at ~$30-50/month

**Access your deployed platform**:
- 🌐 **Frontend**: https://your-username.github.io/grantseeker-ai-platform/
- ⚡ **Backend**: https://ocp10-grant-functions.azurewebsites.net/api/
- 🤖 **AI Model**: http://CONTAINER_IP:8000/

Happy grant writing! 🚀