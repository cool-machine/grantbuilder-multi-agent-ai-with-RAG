# AI Model Testing UI

A web interface for testing and comparing different language models on Azure ML compute instances.

## 🚀 Features

- **Model Selection**: Choose from various pre-configured models (GPT-2, Llama, Mistral, etc.)
- **Real-time Testing**: Test prompts with instant feedback and metrics
- **System Monitoring**: Live system resource monitoring (RAM, CPU, disk)
- **Performance Comparison**: Visual dashboards comparing model performance
- **Predefined Prompts**: Quick test scenarios for different use cases

## 🏗️ Architecture

```
Frontend (React/Vite) → Flask API → Azure ML Models
```

## 🔧 Setup Instructions

### Backend (Run on Azure ML Compute Instance)

1. **SSH into your Azure ML compute instance**:
   ```bash
   az ml compute connect --name "multi-model-test" --resource-group ocp10 --workspace-name ocp10
   ```

2. **Clone and setup backend**:
   ```bash
   git clone <your-repo>
   cd model-testing-ui/backend
   pip install -r requirements.txt
   python app.py
   ```

3. **Backend will be available at**: `http://<compute-instance-ip>:5000`

### Frontend (Local Development)

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Set environment variables**:
   ```bash
   # Create .env file
   echo "VITE_API_BASE_URL=http://<your-compute-instance-ip>:5000/api" > .env
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Access UI at**: `http://localhost:3000`

## 🎯 Usage Guide

### 1. Model Selection
- Browse available models in the left panel
- See model specifications (size, type, description)  
- Click to load a model (loads in Azure ML compute)
- Monitor system resources during loading

### 2. Testing
- Choose from predefined prompts or write custom ones
- Adjust generation parameters (max tokens, temperature)
- Click "Generate Response" to test the loaded model
- View results with performance metrics

### 3. Comparison Dashboard
- Switch to "Comparison Dashboard" tab
- View performance charts comparing all tested models
- Analyze metrics: generation time, response length, success rates
- Export comparison data

## 📊 Available Models

| Model | Size | Type | Description |
|-------|------|------|-------------|
| GPT-2 Small | 117M | General Purpose | Fast, lightweight |
| GPT-2 Medium | 345M | General Purpose | Balanced performance |
| GPT-2 Large | 774M | General Purpose | Higher quality |
| DistilGPT-2 | 82M | Distilled | Ultra-lightweight |
| DialoGPT | 345M | Conversational | Dialogue optimized |
| **GPT-NeoX-20B** | 20B | Large LM | High-quality (requires 40GB+ RAM) |
| **Llama 2 7B** | 7B | Large LM | Meta's model (requires auth) |
| **Mistral 7B** | 7B | Large LM | Efficient 7B model |

## 🔍 API Endpoints

### Backend API (Flask)
- `GET /api/health` - System status
- `GET /api/models` - Available models
- `GET /api/prompts` - Predefined test prompts
- `POST /api/load_model` - Load specific model
- `POST /api/generate` - Generate text with loaded model
- `POST /api/test_models` - Batch test multiple models

## 💾 System Requirements

### Minimum (Small Models)
- **RAM**: 8GB
- **Storage**: 50GB
- **CPU**: 4+ cores

### Recommended (7B Models) 
- **RAM**: 32GB
- **Storage**: 100GB
- **CPU**: 16+ cores

### Required (20B Models)
- **RAM**: 64GB+  
- **Storage**: 200GB
- **CPU**: 32+ cores
- **Optional**: GPU (for faster inference)

## 🚨 Memory Management

The system includes smart memory management:
- **Auto cleanup**: Models are unloaded after each test
- **Memory checks**: Prevents loading if insufficient RAM
- **Resource monitoring**: Real-time system status
- **Graceful degradation**: Skips large models if needed

## 🔐 Security Notes

- Backend should only be accessible from your network
- No authentication currently implemented (Azure ML provides network isolation)
- Model weights cached locally on compute instance

## 📈 Performance Tips

1. **Start with small models** (GPT-2) to test setup
2. **Monitor memory** before loading large models
3. **Use appropriate instance size** for your target models
4. **Close other applications** when testing large models

## 🛠️ Troubleshooting

### Common Issues

**Backend not responding**:
- Check if Flask app is running: `ps aux | grep python`
- Verify firewall rules on compute instance
- Check backend logs for errors

**Model loading fails**:
- Insufficient memory (check system info panel)
- Network issues downloading model weights
- Missing dependencies (run `pip install -r requirements.txt`)

**Frontend connection issues**:
- Verify VITE_API_BASE_URL in .env file
- Check compute instance IP address
- Ensure ports 5000 and 3000 are accessible

## 📝 Development

### Adding New Models
1. Edit `AVAILABLE_MODELS` dict in `backend/app.py`
2. Add model configuration with HuggingFace model ID
3. Update memory requirements if needed

### Customizing UI
- Components in `frontend/src/components/`
- Styling with TailwindCSS
- Charts using Recharts library

## 🎉 Success Criteria

✅ **Working Setup**:
- Backend Flask API responding
- Frontend displaying model list
- Successfully loading and testing small models
- System monitoring showing real-time stats

✅ **Full Functionality**:
- Testing multiple models without memory issues
- Comparison dashboard showing performance metrics
- Stable operation over extended testing periods

---

**Status**: Ready for deployment and testing! 🚀