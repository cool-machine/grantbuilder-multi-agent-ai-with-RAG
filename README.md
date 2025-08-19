# 🚀 GrantSeeker AI Platform

**Complete AI-powered grant discovery, analysis, and application system using Google Gemma 3 270M-IT**

[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)](docs/architecture.md)
[![AI Model](https://img.shields.io/badge/AI-Gemma%203%20270M--IT-green)](https://huggingface.co/google/gemma-3-270m-it)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-blue)](frontend/)
[![Backend](https://img.shields.io/badge/Backend-Azure%20Functions-orange)](backend/)
[![Container](https://img.shields.io/badge/Container-Azure%20ACI-purple)](ai-model/)

## 🎯 Overview

GrantSeeker AI Platform is a comprehensive solution for nonprofits and researchers to discover, analyze, and apply for grants using advanced AI assistance. The platform combines modern web technologies with containerized AI models to provide professional-grade grant writing support.

### ✨ Key Features

- **🔍 Grant Discovery**: Intelligent search and filtering of funding opportunities
- **📊 AI-Powered Analysis**: Automated grant requirement analysis using Gemma 3 270M-IT
- **📝 Smart Form Filling**: AI-assisted grant application completion
- **💰 Cost-Effective**: Production-ready deployment for ~$30-50/month
- **🌐 Production Ready**: Auto-scaling, monitoring, and error handling

## 🏗️ Architecture

```mermaid
graph TB
    A[User Browser] -->|HTTPS| B[React Frontend]
    B -->|API Calls| C[Azure Functions Backend]
    C -->|HTTP| D[Containerized AI API]
    D -->|Inference| E[Gemma 3 270M-IT Model]
    
    subgraph "Frontend Layer"
        B --> B1[Grant Discovery]
        B --> B2[Document Analysis]
        B --> B3[Form Filling]
    end
    
    subgraph "Backend Layer"
        C --> C1[TokenizerFunction]
        C --> C2[AnalyzeGrant]
        C --> C3[FillGrantForm]
        C --> C4[ProcessDocument]
    end
    
    subgraph "AI Layer"
        D --> D1[Flask API Server]
        D --> D2[Model Caching]
        E --> E1[Text Generation]
        E --> E2[Context Understanding]
    end
    
    subgraph "Infrastructure"
        F[GitHub Pages] --> B
        G[Azure Functions] --> C
        H[Azure Container Instances] --> D
    end
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Docker
- Azure CLI
- Azure subscription

### 1. Clone Repository

```bash
git clone https://github.com/your-username/grantseeker-ai-platform.git
cd grantseeker-ai-platform
```

### 2. Deploy AI Model Container

```bash
cd ai-model
./deploy/build-and-deploy.sh
```

### 3. Deploy Backend Functions

```bash
cd backend
func azure functionapp publish ocp10-grant-functions --python
```

### 4. Deploy Frontend

```bash
cd frontend
npm install
npm run build
# Deploy to GitHub Pages or Azure Static Web Apps
```

## 📁 Repository Structure

```
grantseeker-ai-platform/
├── 📁 frontend/                 # React + TypeScript frontend
│   ├── src/components/         # UI components
│   ├── src/pages/             # Page components
│   ├── src/services/          # API services
│   └── package.json           # Dependencies
├── 📁 backend/                 # Azure Functions backend
│   ├── FillGrantForm/         # PDF form filling function
│   ├── TokenizerFunction/     # Text tokenization
│   ├── AnalyzeGrant/          # Grant analysis
│   ├── ProcessDocument/       # Document processing
│   └── requirements.txt       # Python dependencies
├── 📁 ai-model/               # Containerized AI model
│   ├── flask_gemma_api.py     # Flask API server
│   ├── Dockerfile             # Container configuration
│   ├── requirements.txt       # Model dependencies
│   └── deploy/                # Deployment scripts
├── 📁 docs/                   # Documentation
├── 📁 .github/workflows/      # CI/CD pipelines
└── README.md                  # This file
```

## 🤖 AI Model Details

### Google Gemma 3 270M-IT

- **Parameters**: 270 million (optimized for efficiency)
- **Type**: Instruction-tuned language model
- **Deployment**: Containerized on Azure Container Instances
- **Performance**: ~4-6 second generation time
- **Memory**: ~2-3 GB RAM requirement
- **Cost**: Predictable infrastructure pricing

### API Endpoints

```bash
# Health check
GET http://your-container-ip:8000/health

# Text generation
POST http://your-container-ip:8000/generate
{
  "prompt": "Write a grant project description for marine conservation:",
  "max_new_tokens": 100,
  "temperature": 0.7
}
```

## 💰 Cost Analysis

### Monthly Cost Breakdown

| Component | Service | Cost Range |
|-----------|---------|------------|
| **Frontend** | GitHub Pages | Free |
| **Backend** | Azure Functions (Consumption) | $0-10 |
| **AI Model** | Container Instances (8GB) | $30-50 |
| **Storage** | Azure Storage | $1-5 |
| **Total** | **Complete Platform** | **$31-65/month** |

### Cost Comparison

| Solution | Monthly Cost | Limitations |
|----------|--------------|-------------|
| **GrantSeeker AI** | $31-65 | None - full control |
| OpenAI GPT-3.5 API | $100-500+ | Token limits, rate limits |
| Azure OpenAI | $80-300+ | Quota requirements |
| Functions Premium | $73+ | Fixed cost, overprovisioned |

## 📊 Performance Metrics

### Response Times
- **Model Loading**: ~6 seconds (cached)
- **Text Generation**: ~4-6 seconds
- **API Response**: <10 seconds end-to-end
- **Frontend Load**: ~2 seconds

### Quality Metrics
- **Professional Grant Writing**: ✅ High quality output
- **Context Understanding**: ✅ Follows prompts accurately
- **Consistency**: ✅ Reproducible results
- **Language Support**: ✅ English + basic multilingual

## 🛠️ Development

### Local Development Setup

```bash
# Frontend development
cd frontend
npm install
npm run dev  # http://localhost:5173

# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
func start  # http://localhost:7071

# AI Model development
cd ai-model
pip install -r requirements.txt
python flask_gemma_api.py  # http://localhost:8000
```

### Docker Development

```bash
# Build and run AI model container locally
cd ai-model
docker build -t grantseeker-ai .
docker run -p 8000:8000 grantseeker-ai
```

## 🔒 Security

- **Container Security**: Non-root user, minimal base image
- **API Security**: Input validation, rate limiting
- **Network Security**: HTTPS enforced, private container networking
- **Data Privacy**: No persistent storage of user data
- **Model Security**: Local deployment, no external AI API dependencies

## 📈 Scalability

### Current Capacity
- **Concurrent Users**: ~10-20 (single container)
- **Requests/Hour**: ~100-500
- **Model Throughput**: ~10-15 requests/minute

### Scaling Options
- **Horizontal**: Multiple container instances
- **Vertical**: Larger container sizes (up to 14GB)
- **Load Balancing**: Azure Load Balancer + multiple containers
- **Auto-scaling**: Container Groups with scaling rules

## 🧪 Testing

```bash
# Run frontend tests
cd frontend
npm test

# Run backend tests
cd backend
python -m pytest

# Test AI model API
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test prompt", "max_new_tokens": 50}'
```

## 📚 Documentation

- [**Architecture Guide**](docs/architecture.md) - System design and components
- [**Deployment Guide**](docs/deployment.md) - Step-by-step setup
- [**API Reference**](docs/api.md) - Complete API documentation
- [**Cost Optimization**](docs/cost-optimization.md) - Reducing operational costs
- [**Troubleshooting**](docs/troubleshooting.md) - Common issues and solutions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License**.

### 🎓 Academic & Learning Use
- ✅ **Free to use** for learning, research, and educational purposes
- ✅ **Share and adapt** the code with proper attribution
- ✅ **Study the architecture** for academic research

### 🚫 Commercial Restrictions
- ❌ **No commercial use** without explicit permission
- ❌ **No selling** or monetizing the platform directly
- ❌ **No commercial deployment** without licensing agreement

### 💼 Commercial Licensing
For commercial use, enterprise licensing, or business deployment:
- **Contact**: [Add your contact information]
- **Custom licensing** available for businesses
- **Enterprise support** and customization options

See the [LICENSE](LICENSE) file for complete terms.

## 🙏 Acknowledgments

- **Google Gemma Team** - For the excellent 270M-IT model
- **Hugging Face** - For model hosting and transformers library
- **Microsoft Azure** - For cost-effective cloud infrastructure
- **Open Source Community** - For the amazing tools and libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/grantseeker-ai-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/grantseeker-ai-platform/discussions)
- **Documentation**: [Wiki](https://github.com/your-username/grantseeker-ai-platform/wiki)

---

**Built with ❤️ for the nonprofit and research community**

*Empowering organizations to secure funding through AI-assisted grant writing*