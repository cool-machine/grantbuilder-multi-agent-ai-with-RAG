# Mistral 7B Integration Guide

## 🎯 Overview
This guide helps you integrate Mistral 7B into your GrantSeeker Azure Functions backend for advanced grant analysis.

## 📋 Prerequisites

### Hardware Requirements
- **RAM**: 16GB+ (for local testing)
- **GPU**: Optional but recommended (RTX 4090, V100, etc.)
- **Azure**: Standard_NC6s_v3 or larger for production

### Software Requirements
- Python 3.9+
- CUDA (if using GPU)
- Azure Functions Core Tools

## 🚀 Deployment Options

### Option 1: Local Testing First (Recommended)

1. **Install Dependencies**:
```bash
cd /Users/gg1900/coding/grantseeker-back
source venv/bin/activate
pip install torch transformers accelerate sentencepiece
```

2. **Test Locally**:
```bash
# Backup current function
cp TokenizerFunction/__init__.py TokenizerFunction/__init___backup.py

# Use Mistral version
cp TokenizerFunction/__init___mistral.py TokenizerFunction/__init__.py

# Start local function
func start --port 7071
```

3. **Test API**:
```bash
curl -X POST http://localhost:7071/api/tokenizerfunction \
  -H "Content-Type: application/json" \
  -d '{
    "text": "NSF research grant for AI applications in healthcare",
    "model": "mistral-7b-instruct",
    "analysis_type": "grant_analysis"
  }'
```

### Option 2: Direct Azure Deployment

1. **Update Requirements**:
```bash
# Replace requirements.txt with Mistral version
cp requirements.txt.mistral requirements.txt
```

2. **Deploy to Azure**:
```bash
# Deploy with increased timeout for model loading
func azure functionapp publish ocp10-grant-functions --python --build remote
```

## 🧪 Testing Grant Analysis

### Test Cases

1. **Grant Analysis**:
```json
{
  "text": "The National Science Foundation seeks proposals for innovative AI research in healthcare applications. Maximum award: $500,000 over 3 years.",
  "model": "mistral-7b-instruct", 
  "analysis_type": "grant_analysis"
}
```

2. **Document Analysis**:
```json
{
  "text": "Annual Report - Teach for America has successfully placed 3,500 teachers in rural communities...",
  "model": "mistral-7b-instruct",
  "analysis_type": "document_analysis"
}
```

## ⚡ Performance Optimization

### For Production Use:

1. **Model Caching**:
   - Models load once and stay in memory
   - First request may be slow (30-60 seconds)
   - Subsequent requests are fast (<5 seconds)

2. **Memory Management**:
   - Use `torch.float16` for GPU inference
   - Consider 4-bit quantization with `bitsandbytes`
   - Monitor Azure Function memory usage

3. **Azure Function Settings**:
   - Increase timeout to 300 seconds
   - Use Premium plan for better performance
   - Consider dedicated App Service plan for heavy usage

## 🔧 Configuration Options

### Environment Variables (Optional):
```bash
# In Azure Function App Configuration
DEFAULT_MODEL=mistral-7b-instruct
TORCH_DEVICE=cuda  # or cpu
MODEL_CACHE_DIR=/tmp/models
```

### Model Variants:
- `mistralai/Mistral-7B-Instruct-v0.1` - Original instruction-tuned
- `mistralai/Mistral-7B-Instruct-v0.2` - Improved version
- `mistralai/Mistral-7B-v0.1` - Base model (requires custom prompting)

## 🚨 Troubleshooting

### Common Issues:

1. **Out of Memory**:
   - Use CPU inference: `device="cpu"`
   - Reduce batch size or model precision
   - Consider model quantization

2. **Slow Loading**:
   - Models download ~13GB on first run
   - Use Azure Function warm-up triggers
   - Consider pre-loading in Docker container

3. **Import Errors**:
   - Ensure all dependencies in requirements.txt
   - Check Python version compatibility
   - Verify CUDA installation if using GPU

### Fallback Strategy:
The function automatically falls back to simple tokenization if Mistral fails to load, ensuring your GrantSeeker platform stays operational.

## 📊 Expected Performance

### Local Testing (16GB RAM):
- **Model Loading**: 30-60 seconds (first time)
- **Grant Analysis**: 2-10 seconds per request
- **Memory Usage**: 8-12GB

### Azure Functions Premium:
- **Cold Start**: 60-120 seconds (rare)
- **Warm Requests**: 3-15 seconds
- **Memory Usage**: Monitor with Application Insights

## 🎯 Integration with GrantSeeker Frontend

Once deployed, your existing frontend components will automatically benefit:
- **GrantAnalyzer**: Enhanced with Mistral 7B insights
- **DocumentProcessor**: Better document understanding
- **GrantFormFiller**: Smarter form field completion

## 🔄 Rollback Plan

If issues occur:
```bash
# Restore original function
cp TokenizerFunction/__init___backup.py TokenizerFunction/__init__.py

# Deploy simple version
func azure functionapp publish ocp10-grant-functions --python
```

## 🚀 Next Steps

1. **Start with local testing**
2. **Test with real grant examples**
3. **Deploy to Azure when satisfied**
4. **Monitor performance and costs**
5. **Consider fine-tuning on NIH/NIAID data**

Your GrantSeeker platform will be significantly enhanced with Mistral 7B's grant analysis capabilities!