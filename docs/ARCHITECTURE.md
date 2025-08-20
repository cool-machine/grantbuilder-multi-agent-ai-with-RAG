# 🏗️ GrantSeeker AI Platform - Architecture Documentation

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Patterns](#architecture-patterns)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Infrastructure](#infrastructure)
- [Security Architecture](#security-architecture)
- [Performance Architecture](#performance-architecture)
- [Scalability Considerations](#scalability-considerations)

## System Overview

The GrantSeeker AI Platform follows a **microservices architecture** with clear separation of concerns across three main layers:

1. **Frontend Layer**: React SPA hosted on GitHub Pages
2. **Backend Layer**: Serverless Azure Functions (Python)
3. **AI Layer**: Containerized Gemma 3 270M-IT model

```mermaid
graph TB
    subgraph "User Interface"
        U[👤 Users] --> F[🌐 Frontend SPA]
    end
    
    subgraph "Application Layer"
        F -->|HTTPS API| B[⚡ Backend Functions]
        B -->|HTTP| AI[🤖 AI Container]
    end
    
    subgraph "Infrastructure Layer"
        F -.-> GH[GitHub Pages]
        B -.-> AF[Azure Functions]
        AI -.-> ACI[Azure Container Instance]
    end
```

## Architecture Patterns

### 1. **Proxy Pattern**
- **GemmaProxy** acts as a gateway to the AI model
- Centralizes authentication, logging, and error handling
- Provides consistent API interface for all functions

### 2. **Function-as-a-Service (FaaS)**
- Each backend capability is a separate Azure Function
- Auto-scaling based on demand
- Pay-per-execution cost model

### 3. **Container-First AI**
- AI model runs in dedicated container
- Predictable performance and costs
- Full control over model deployment and updates

### 4. **Static Site Architecture**
- Frontend compiled to static assets
- CDN distribution via GitHub Pages
- Optimal performance and zero backend costs for UI

## Component Details

### Frontend Components

```mermaid
graph TD
    App[App.tsx] --> Router[React Router]
    Router --> Home[HomePage.tsx]
    Router --> Grants[GrantsPage.tsx]
    Router --> Analysis[GrantAnalysisPage.tsx]
    Router --> Fill[FillApplicationPage.tsx]
    
    Fill --> GFF[GrantFormFiller.tsx]
    Analysis --> GA[GrantAnalyzer.tsx]
    Home --> DP[DocumentProcessor.tsx]
    
    subgraph "Shared Components"
        Header[Header.tsx]
        Footer[Footer.tsx]
        ProtectedRoute[ProtectedRoute.tsx]
    end
    
    subgraph "Context Providers"
        GC[GrantContext.tsx]
        AC[AuthContext.tsx]
        LC[LanguageContext.tsx]
    end
```

### Backend Functions

```mermaid
graph LR
    subgraph "Azure Functions App: ocp10-grant-functions"
        GP[GemmaProxy/]
        FGF[FillGrantForm/]
        AG[AnalyzeGrant/]
        PD[ProcessDocument/]
        CS[CrawlerService/]
        GM[GetMatches/]
        TF[TokenizerFunction/]
    end
    
    GP --> |Proxies to| AI[AI Container]
    FGF --> |Uses| GP
    AG --> |Uses| GP
    PD --> |Uses| GP
```

#### Function Responsibilities

| Function | Purpose | Dependencies |
|----------|---------|--------------|
| **GemmaProxy** | AI model gateway and request routing | requests, logging |
| **FillGrantForm** | PDF form filling with AI assistance | PyPDF2, reportlab, GemmaProxy |
| **AnalyzeGrant** | Grant opportunity analysis | beautifulsoup4, GemmaProxy |
| **ProcessDocument** | Document parsing and extraction | PyPDF2, pandas |
| **CrawlerService** | Grant discovery web crawling | aiohttp, sqlalchemy |
| **GetMatches** | Grant matching algorithm | pandas, sqlalchemy |
| **TokenizerFunction** | Text tokenization services | transformers |

### AI Infrastructure

```mermaid
graph TB
    subgraph "Azure Container Instance"
        subgraph "Container: 13.89.105.77:8000"
            Flask[Flask API Server]
            Model[Gemma 3 270M-IT Model]
            Cache[Model Cache]
            Queue[Request Queue]
        end
    end
    
    Flask --> Model
    Flask --> Cache
    Flask --> Queue
    
    subgraph "Endpoints"
        Health[GET /health]
        Generate[POST /generate]
    end
    
    Flask --> Health
    Flask --> Generate
```

## Data Flow

### Grant Form Filling Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant FGF as FillGrantForm
    participant GP as GemmaProxy
    participant AI as AI Container
    
    U->>F: 1. Upload PDF file
    F->>F: 2. Convert to base64
    F->>FGF: 3. POST /api/fillgrantform
    
    Note over FGF: PDF Processing
    FGF->>FGF: 4. Decode PDF
    FGF->>FGF: 5. Extract text (PyPDF2)
    FGF->>FGF: 6. Match field patterns
    
    Note over FGF: AI Generation Loop
    loop For each field
        FGF->>GP: 7. Request field content
        GP->>AI: 8. POST /generate
        AI->>AI: 9. Model inference
        AI-->>GP: 10. Generated text
        GP-->>FGF: 11. Field response
    end
    
    Note over FGF: PDF Creation
    FGF->>FGF: 12. Create filled PDF (reportlab)
    FGF->>FGF: 13. Encode to base64
    FGF-->>F: 14. Return filled PDF
    F-->>U: 15. Download file
```

### Request/Response Patterns

#### API Request Format
```json
{
  "pdf_data": "base64_encoded_pdf_content",
  "ngo_profile": {
    "organization_name": "Community Health Alliance",
    "mission": "Providing healthcare access",
    "years_active": 5,
    "focus_areas": ["health", "community"],
    "annual_budget": 500000
  },
  "grant_context": {
    "funder_name": "Health Foundation",
    "focus_area": "community health",
    "max_amount": 50000
  }
}
```

#### AI Model Request Format
```json
{
  "prompt": "Generate grant application content...",
  "max_new_tokens": 100,
  "temperature": 0.5
}
```

## Infrastructure

### Hosting Architecture

```mermaid
graph TB
    subgraph "GitHub"
        Repo[Repository]
        Pages[GitHub Pages]
        Actions[GitHub Actions]
    end
    
    subgraph "Azure Cloud"
        RG[Resource Group: ocp10]
        FA[Functions App]
        SA[Storage Account]
        CI[Container Instance]
    end
    
    subgraph "External Services"
        CDN[GitHub Pages CDN]
        DNS[Custom Domain]
    end
    
    Repo --> Actions
    Actions --> Pages
    Pages --> CDN
    
    FA --> RG
    SA --> RG
    CI --> RG
```

### Resource Configuration

| Resource | Type | Configuration | Cost/Month |
|----------|------|---------------|------------|
| **Frontend** | GitHub Pages | Static hosting, CDN | Free |
| **Backend** | Azure Functions | Consumption plan, Python 3.9 | $0-10 |
| **AI Model** | Container Instance | 8GB RAM, 2 vCPUs | $30-50 |
| **Storage** | Azure Storage | Blob storage for logs | $1-5 |

## Security Architecture

### Network Security

```mermaid
graph LR
    Internet[🌐 Internet] -->|HTTPS| GH[GitHub Pages]
    Internet -->|HTTPS| AF[Azure Functions]
    AF -->|HTTP*| CI[Container Instance]
    
    subgraph "Security Layers"
        SSL[SSL/TLS Termination]
        CORS[CORS Policy]
        Input[Input Validation]
        RateLimit[Rate Limiting]
    end
    
    GH --> SSL
    AF --> SSL
    AF --> CORS
    AF --> Input
    CI --> RateLimit
    
    Note1[* HTTP within Azure network]
```

### Data Security

- **No Persistent Storage**: All processing is stateless
- **Memory-Only Processing**: PDFs processed in function memory
- **Auto-Cleanup**: Temporary data cleared after processing
- **Input Validation**: All inputs sanitized and validated

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant AF as Azure Functions
    participant AI as AI Container
    
    Note over U,AI: No authentication required (demo mode)
    U->>F: Access application
    F->>AF: Anonymous API calls
    AF->>AI: Internal HTTP calls
    AI-->>AF: Response
    AF-->>F: Response
    F-->>U: Display results
```

## Performance Architecture

### Caching Strategy

```mermaid
graph TB
    subgraph "Caching Layers"
        CDN[GitHub Pages CDN]
        Browser[Browser Cache]
        Function[Function Memory]
        Model[Model Cache]
    end
    
    subgraph "Cache Policies"
        Static[Static Assets: 1 year]
        API[API Responses: No cache]
        ModelCache[Model: Persistent in memory]
    end
    
    CDN --> Static
    Browser --> Static
    Function --> API
    Model --> ModelCache
```

### Performance Metrics

| Component | Metric | Target | Actual |
|-----------|--------|---------|---------|
| **Frontend Load** | Time to Interactive | < 3s | ~2s |
| **API Response** | 95th percentile | < 30s | ~10s |
| **AI Inference** | Generation time | < 10s | ~4-6s |
| **PDF Processing** | File processing | < 5s | ~2-3s |

### Optimization Techniques

1. **Frontend Optimizations**
   - Code splitting with React.lazy()
   - Image optimization and compression
   - Bundle size optimization with Vite

2. **Backend Optimizations**
   - Function memory tuning (512MB-1GB)
   - Connection pooling for HTTP requests
   - Efficient PDF processing algorithms

3. **AI Optimizations**
   - Model quantization for faster inference
   - Request batching where possible
   - Memory-efficient prompt construction

## Scalability Considerations

### Current Limitations

- **Single Container Instance**: 10-20 concurrent users
- **Memory Constraints**: 6GB RAM for AI model
- **Geographic Distribution**: Single Azure region

### Scaling Strategies

#### Horizontal Scaling
```mermaid
graph TB
    LB[Azure Load Balancer] --> C1[Container 1]
    LB --> C2[Container 2]
    LB --> C3[Container N]
    
    subgraph "Auto-scaling Rules"
        CPU[CPU > 70%]
        Memory[Memory > 80%]
        Requests[Requests > 50/min]
    end
    
    CPU --> LB
    Memory --> LB
    Requests --> LB
```

#### Vertical Scaling
- Increase container resources (up to 14GB RAM)
- Use larger VM sizes for Azure Functions
- Optimize model loading and caching

#### Geographic Distribution
- Deploy containers in multiple Azure regions
- Use Azure Front Door for global load balancing
- Implement region-specific routing

### Monitoring and Alerting

```mermaid
graph LR
    App[Application] --> Logs[Azure Monitor]
    App --> Metrics[Application Insights]
    App --> Health[Health Checks]
    
    Logs --> Alerts[Alert Rules]
    Metrics --> Alerts
    Health --> Alerts
    
    Alerts --> Email[Email Notifications]
    Alerts --> SMS[SMS Alerts]
    Alerts --> Webhook[Webhook Integration]
```

## Cost Architecture

### Current Cost Breakdown
- **Total Monthly Cost**: $31-65
- **Primary Cost Driver**: AI container hosting (~$30-50)
- **Variable Costs**: Azure Functions execution time
- **Fixed Costs**: Container instance base rate

### Cost Optimization Strategies
1. **Container Scheduling**: Stop/start based on usage patterns
2. **Function Optimization**: Reduce execution time and memory usage
3. **Regional Selection**: Choose cost-effective Azure regions
4. **Reserved Instances**: Use reserved pricing for predictable workloads

---

This architecture provides a solid foundation for the GrantSeeker AI Platform with clear separation of concerns, scalability options, and cost-effective resource utilization.