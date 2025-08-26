# Model Testing Integration with GrantSeeker Platform

## 🎯 **What's Built**

I've integrated **AI Model Testing** directly into your existing GrantSeeker platform:

### **✅ Frontend Integration:**
- ✅ **New page**: `/model-testing` in your GrantSeeker app
- ✅ **Navigation**: Added to "AI Tools" dropdown menu
- ✅ **Grant-specific prompts**: Mission alignment, project impact, budget justification
- ✅ **Same design language**: Matches your existing GrantSeeker UI

### **✅ Backend Options:**
- ✅ **Local models**: Run on your Azure ML compute instance
- ✅ **Hugging Face**: Affordable cloud hosting ($0.60-1.20/hour)
- ✅ **Azure OpenAI**: GPT-3.5 Turbo integration (when approved)

---

## 🚀 **How to Use It**

### **Option 1: Test Locally (Recommended Start)**

1. **Start your Azure ML compute instance**:
   ```bash
   ./cost_control.sh start
   ```

2. **SSH into your compute instance**:
   ```bash
   az ml compute connect --name "multi-model-test" --resource-group ocp10 --workspace-name ocp10
   ```

3. **Run the model testing backend**:
   ```bash
   cd model-testing-ui/backend
   pip install -r requirements.txt
   python app_hybrid.py
   ```

4. **Update your GrantSeeker frontend**:
   ```bash
   # In your frontend directory
   echo "VITE_MODEL_TESTING_API_URL=http://YOUR_COMPUTE_IP:5000/api" >> .env
   npm run dev
   ```

5. **Access the testing page**:
   - Go to: `http://localhost:3000/model-testing`
   - Or click "AI Tools" → "Model Testing Lab" in your GrantSeeker nav

### **Option 2: Deploy on Hugging Face (Production)**

1. **Get HuggingFace token**:
   ```bash
   # Get token from: https://huggingface.co/settings/tokens
   export HUGGINGFACE_TOKEN="your-token-here"
   ```

2. **Deploy models you want to test**:
   ```bash
   python huggingface_endpoint.py
   ```

3. **Update backend to use HF endpoints**:
   ```bash
   python app_hybrid.py  # Will auto-detect HF token
   ```

---

## 🎯 **Perfect for Your Grant Writing Use Case**

### **Built-in Grant Scenarios:**
1. **Mission Alignment** - "How does your organization's mission align with this funding opportunity?"
2. **Project Impact** - "Describe the expected outcomes and how you will measure success"
3. **Budget Justification** - "Justify why this budget allocation will effectively achieve goals"
4. **Sustainability Plan** - "How will you ensure the program continues after the grant period?"

### **Model Comparison:**
- **Test the same prompt** across multiple models
- **Compare quality** vs **cost** vs **speed**
- **Find the sweet spot** for your grant writing needs

---

## 💰 **Cost-Effective Testing Strategy**

### **Phase 1: Free Baseline (Your 32GB instance)**
1. **FLAN-T5 XL (3B)** - Excellent for structured tasks like grants
2. **Microsoft Phi-2 (2.7B)** - Great reasoning capabilities
3. **GPT-2 XL (1.5B)** - Reliable baseline

**Cost**: Just compute time (~$2.40/hour, stop when done)

### **Phase 2: Quality Comparison**
4. **GPT-3.5 Turbo** (Azure OpenAI) - $0.50 per 1K tokens
5. **Llama 2 7B** (Hugging Face) - $0.60/hour
6. **Mistral 7B** (Hugging Face) - $0.60/hour

**Result**: Find which model gives you the best **quality/cost ratio**

---

## 🔧 **Integration Benefits**

### **Same UI, Better Testing:**
- **Familiar interface** - Uses your GrantSeeker design
- **Grant-specific prompts** - Not generic AI testing
- **Contextual results** - Compare models for your exact use case
- **Cost tracking** - See price per generation

### **Production Integration:**
Once you find the best model, you can:
- **Replace Gemma** in your main GrantSeeker backend
- **Use the same API endpoints** in your existing grant form filler
- **Get better quality** grant responses

---

## 📊 **Expected Results**

### **For Grant Writing, You'll Likely Find:**
1. **FLAN-T5 XL** - Best free option for structured responses
2. **GPT-3.5 Turbo** - Highest quality, reasonable cost
3. **Phi-2** - Surprising quality for size, great backup

### **Cost Comparison** (1000 grant responses/month):
- **FLAN-T5 XL**: ~$50 in compute costs
- **GPT-3.5 Turbo**: ~$500 in API costs
- **Hybrid approach**: Use FLAN-T5 for drafts, GPT-3.5 for final

---

## 🎉 **Ready to Test!**

### **Quick Start:**
1. **Start your compute instance**
2. **Run the backend** (`python app_hybrid.py`)
3. **Open GrantSeeker** at `/model-testing`
4. **Test grant writing prompts** with different models
5. **Find your optimal model** for production use

### **The Result:**
You'll have data-driven insights into which AI model gives you the **best grant writing quality** for your **budget and requirements**.

**This integration turns your GrantSeeker platform into a comprehensive AI model evaluation lab specifically designed for grant writing! 🚀**

---

## 🆘 **Quick Troubleshooting**

### **Backend won't start:**
```bash
# Check if port 5000 is free
lsof -i :5000
# Kill if needed, then restart
```

### **Frontend can't connect:**
```bash
# Check your compute instance IP
az ml compute show --name "multi-model-test" --resource-group ocp10 --workspace-name ocp10 --query "properties.connectivityEndpoints"

# Update .env file with correct IP
```

### **Models won't load:**
```bash
# Check available memory
free -h
# If low, restart instance or try smaller models
```

**You now have a complete model testing lab integrated into your GrantSeeker platform! 🎯**