# GrantSeeker Backend - AI-Powered Grant Analysis System

> Backend Azure Functions API for AI-powered grant analysis, document processing, and intelligent grant matching using OpenAI GPT models

## 🎯 Overview

This project provides an intelligent grant analysis system that helps NGOs and researchers discover, analyze, and apply for relevant funding opportunities. Built with Azure Functions v4, Python, and Azure OpenAI GPT-3.5-Turbo.

## ✨ Features

### 🔤 Document Processing
- **Multi-format support**: PDF, DOCX, TXT document upload
- **AI-powered analysis**: Extract key information using GPT-3.5-Turbo
- **Grant classification**: Automatic identification of grant-related content
- **Metadata extraction**: Organizations, amounts, deadlines, requirements

### 📊 Grant Analysis
- **Opportunity evaluation**: Deep analysis of grant requirements and criteria
- **Eligibility assessment**: Automated eligibility requirement extraction
- **Competition analysis**: Assessment of competitiveness levels
- **Strategic recommendations**: Tailored advice for strong applications

### 🎯 Intelligent Matching
- **AI-powered matching**: Smart grant-to-applicant compatibility scoring
- **Detailed reasoning**: Explanations for match scores and recommendations
- **Gap analysis**: Identification of potential weaknesses in applications
- **Priority ranking**: High/medium/low priority recommendations

### 🔧 Text Tokenization
- **Legacy support**: Original simple tokenization for backward compatibility
- **Multiple formats**: Support for various text processing needs

### 📝 PDF Form Filling
- **Automated form filling**: AI-powered completion of grant application forms
- **Professional PDF generation**: Clean, structured grant applications
- **Multi-format support**: Handles both fillable and non-fillable PDF forms

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Azure Functions │    │  Azure Services │
│   (React App)   │───▶│     Backend      │───▶│                 │
│                 │    │                  │    │ • OpenAI GPT-3.5│
└─────────────────┘    │ • TokenizerFunc  │    │ • Cosmos DB     │
                       │ • ProcessDoc     │    │ • Blob Storage  │
                       │ • AnalyzeGrant   │    │                 │
                       │ • GetMatches     │    │                 │
                       │ • FillGrantForm  │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Azure subscription with function app quota
- Azure OpenAI service access (GPT-3.5-Turbo)
- Python 3.9+ for local development
- Azure CLI installed and authenticated

### 1. Clone Repository
```bash
git clone https://github.com/cool-machine/grantseeker-back.git
cd grantseeker-back
```

### 2. Set Up Local Development
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Start local development server
func start
```

### 3. Deploy to Azure
```bash
# Option 1: Manual deployment
./deploy_enhanced.sh

# Option 2: GitHub Actions (recommended)
# 1. Add AZURE_CREDENTIALS secret to GitHub repository
# 2. Push to main branch - auto-deploys via GitHub Actions
```

## 📡 API Endpoints

### Base URL
```
https://ocp10-grant-functions.azurewebsites.net/api/
```

### 1. Tokenizer Function
```http
POST /tokenizerfunction
Content-Type: application/json

{
  "text": "Text to tokenize",
  "model_name": "gpt2",
  "return_tokens": true,
  "return_token_ids": true
}
```

### 2. Process Document
```http
POST /processdocument
Content-Type: application/json

{
  "documentContent": "Grant application text...",
  "fileName": "application.pdf",
  "fileType": "pdf"
}
```

**Response:**
```json
{
  "success": true,
  "documentId": "20250814_123456_application.pdf",
  "analysis": {
    "summary": "Brief document summary",
    "documentType": "grant application",
    "isGrantRelated": true,
    "confidence": 0.95,
    "keyEntities": ["NSF", "$500,000", "2025-03-15"],
    "grantRequirements": ["PhD required", "University affiliation"]
  },
  "blobUrl": "https://...",
  "wordCount": 1247
}
```

### 3. Analyze Grant Opportunity
```http
POST /analyzegrant
Content-Type: application/json

{
  "grantDescription": "NSF research grant for AI development...",
  "organizationType": "university",
  "fundingAmount": "$500,000",
  "deadline": "2025-03-15"
}
```

**Response:**
```json
{
  "success": true,
  "grantId": "grant_20250814_123456_abc12345",
  "analysis": {
    "eligibilityRequirements": ["PhD in relevant field", "US institution"],
    "fundingDetails": {
      "amount": "$500,000",
      "duration": "3 years",
      "matchingRequired": false
    },
    "competitiveness": "high",
    "recommendedApplicantProfile": "Established AI researcher...",
    "successFactors": ["Novel approach", "Strong preliminary data"]
  }
}
```

### 4. Get Grant Matches
```http
GET /getmatches?documentId=doc123&organizationType=university&researchArea=AI
```

**Response:**
```json
{
  "success": true,
  "matches": [
    {
      "grantId": "grant_20250814_123456_abc12345",
      "matchScore": 85,
      "reasoning": "Strong alignment with AI research focus...",
      "strengths": ["Research area match", "Institution type"],
      "gaps": ["Limited commercial experience"],
      "recommendations": ["Emphasize academic partnerships"],
      "priority": "high",
      "grantDetails": {
        "description": "NSF AI research funding...",
        "fundingAmount": "$500,000",
        "deadline": "2025-03-15"
      }
    }
  ],
  "totalGrants": 15,
  "userDocument": {
    "id": "doc123",
    "fileName": "research_proposal.pdf",
    "analysis": {...}
  }
}
```

### 5. Fill Grant Form
```http
POST /fillgrantform
Content-Type: application/json

{
  "pdfContent": "base64_encoded_pdf_content",
  "fileName": "grant_form.pdf",
  "ngoProfile": {
    "organizationName": "Community Development Alliance",
    "missionStatement": "Empowering underserved communities...",
    "yearsActive": 8,
    "focusAreas": ["education", "technology", "community development"]
  },
  "grantContext": {
    "funderName": "Education Innovation Foundation",
    "focusArea": "digital literacy",
    "maxAmount": "$50,000",
    "deadline": "2025-03-15"
  }
}
```

**Response:**
```json
{
  "success": true,
  "filled_responses": {
    "organization_name": "Community Development Alliance",
    "project_title": "Digital Literacy Empowerment Initiative",
    "project_description": "Comprehensive digital literacy program...",
    "requested_amount": "$45,000"
  },
  "filled_pdf": {
    "data": "base64_encoded_filled_pdf",
    "filename": "filled_grant_application.pdf",
    "content_type": "application/pdf"
  },
  "processing_summary": {
    "total_fields": 8,
    "filled_fields": 8,
    "fill_rate": 100,
    "pdf_generation": {
      "success": true,
      "method": "generated"
    }
  }
}
```

## 🛠️ Technology Stack

### Backend
- **Azure Functions v4** - Serverless compute platform
- **Python 3.9** - Runtime environment
- **OpenAI Python SDK** - GPT-3.5-Turbo integration
- **Azure SDK v2** - Latest Azure service integrations

### Azure Services
- **Azure OpenAI** - GPT-3.5-Turbo for natural language processing
- **Azure Cosmos DB** - Document and grant opportunity storage
- **Azure Blob Storage** - File storage for uploaded documents
- **Azure Functions** - Serverless API endpoints

### DevOps
- **GitHub Actions** - Automated CI/CD pipeline
- **Azure CLI** - Infrastructure deployment
- **Service Principal** - Secure authentication

## ⚙️ Configuration

### Environment Variables
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo

# Cosmos DB Configuration
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
COSMOS_DATABASE_NAME=GrantAnalysis

# Storage Configuration
AzureWebJobsStorage=DefaultEndpointsProtocol=https;AccountName=...
```

### GitHub Secrets (for Actions)
```json
AZURE_CREDENTIALS={
  "clientId": "service-principal-id",
  "clientSecret": "service-principal-secret",
  "subscriptionId": "azure-subscription-id",
  "tenantId": "azure-tenant-id"
}
```

## 📊 Cost Estimation

### Development Environment
| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| Azure Functions | Consumption Plan | Free (1M requests) |
| Azure OpenAI | GPT-3.5-Turbo | ~$10-20 |
| Cosmos DB | 400 RU/s | ~$25 |
| Blob Storage | 10GB LRS | ~$2 |
| **Total** | | **~$37-47/month** |

### Production Scaling
- **High volume**: Scale Cosmos DB RU/s based on throughput needs
- **Global distribution**: Add Cosmos DB regions for multi-region deployment
- **Premium Functions**: Upgrade to Premium plan for guaranteed performance

## 🚀 Deployment

### GitHub Actions (Recommended)
1. **Fork/clone** this repository
2. **Add secrets** to GitHub repository settings:
   - `AZURE_CREDENTIALS` (JSON format)
3. **Push to main** branch - automatically deploys

### Manual Deployment
```bash
# 1. Login to Azure
az login

# 2. Deploy infrastructure and functions
./deploy_enhanced.sh

# 3. Deploy GPT-3.5-Turbo model
az cognitiveservices account deployment create \
  --name ocp10-grant-openai \
  --resource-group ocp10 \
  --deployment-name gpt-35-turbo \
  --model-name gpt-35-turbo \
  --model-version 0125 \
  --model-format OpenAI \
  --scale-type Standard
```

## 🧪 Testing

### Local Testing
```bash
# Start local development server
func start --port 7071

# Test endpoints
curl "http://localhost:7071/api/tokenizerfunction?text=hello"
```

### Production Testing
```bash
# Test deployed functions
curl "https://ocp10-grant-functions.azurewebsites.net/api/tokenizerfunction?text=hello"
```

## 📁 Project Structure

```
grantseeker-back/
├── TokenizerFunction/          # Original tokenization endpoint
│   ├── __init__.py
│   └── function.json
├── ProcessDocument/            # Document analysis with AI
│   ├── __init__.py
│   └── function.json
├── AnalyzeGrant/              # Grant opportunity analysis
│   ├── __init__.py
│   └── function.json
├── GetMatches/                # Intelligent grant matching
│   ├── __init__.py
│   └── function.json
├── FillGrantForm/             # AI-powered PDF form filling
│   ├── __init__.py
│   ├── function.json
│   └── pdf_utils.py
├── .github/workflows/         # GitHub Actions CI/CD
│   └── deploy-functions.yml
├── tests/                     # Unit and integration tests
├── venv/                      # Python virtual environment
├── requirements.txt           # Python dependencies
├── host.json                  # Azure Functions configuration
├── deploy_enhanced.sh         # Infrastructure deployment script
├── CLAUDE.md                  # Project memory and documentation
└── README.md                  # This file
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- **Project Memory**: See [CLAUDE.md](CLAUDE.md) for complete development history
- **Azure Functions**: [Official Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- **Azure OpenAI**: [Service Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)

### Issues & Questions
- **Bug Reports**: Open an issue on GitHub
- **Feature Requests**: Open an issue with the `enhancement` label
- **Questions**: Use GitHub Discussions

## 🏆 Acknowledgments

- **Azure OpenAI Service** for providing GPT-3.5-Turbo capabilities
- **Microsoft Azure** for the serverless computing platform
- **OpenAI** for the underlying language models
- **Grant writing community** for inspiration and requirements

---

<div align="center">

**Built with ❤️ for the grant writing community**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)

</div>