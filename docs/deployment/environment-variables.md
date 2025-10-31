# Environment Variables Reference

Complete reference for all environment variables used in Open Notebook.

## 📋 Quick Reference

| Category | Variable | Required | Default | Description |
|----------|----------|----------|---------|-------------|
| **API** | `API_URL` | No | Auto-detect | External API URL for browser |
| **API** | `INTERNAL_API_URL` | No | `http://localhost:5055` | Internal API URL for Next.js |
| **API** | `API_CLIENT_TIMEOUT` | No | `300` | API request timeout (seconds) |
| **API** | `ESPERANTO_LLM_TIMEOUT` | No | `60` | LLM inference timeout (seconds) |
| **Database** | `SURREAL_URL` | Yes | - | SurrealDB WebSocket URL |
| **Database** | `SURREAL_USER` | Yes | - | SurrealDB username |
| **Database** | `SURREAL_PASSWORD` | Yes | - | SurrealDB password |
| **Database** | `SURREAL_NAMESPACE` | Yes | - | SurrealDB namespace |
| **Database** | `SURREAL_DATABASE` | Yes | - | SurrealDB database name |
| **AI** | `OPENAI_API_KEY` | Recommended | - | OpenAI API key |
| **AI** | `ANTHROPIC_API_KEY` | No | - | Anthropic API key |
| **AI** | `GOOGLE_API_KEY` | No | - | Google Gemini API key |
| **AI** | `GROQ_API_KEY` | No | - | Groq API key |
| **AI** | `OLLAMA_API_BASE` | No | - | Ollama server URL |

---

## 🌐 API Configuration

### API_URL

**Purpose**: External API URL that browsers use to connect to the backend

**Required**: No (auto-detects from request)

**Default**: Auto-detected based on incoming request

**When to set**:
- Behind reverse proxy with custom domain
- Remote server access
- When auto-detection doesn't work

**Examples**:
```env
# Local development (usually not needed)
API_URL=http://localhost:5055

# Remote server
API_URL=http://192.168.1.100:5055

# Custom domain
API_URL=https://notebook.example.com

# Subdomain
API_URL=https://api.example.com
```

**Important**:
- ❌ Don't include `/api` at the end
- ✅ Use the URL that browsers can access
- ✅ Match the protocol (http/https)

---

### INTERNAL_API_URL

**Purpose**: Internal API URL for Next.js server-side API proxying

**Required**: No

**Default**: `http://localhost:5055`

**When to set**:
- Multi-container Docker Compose deployments
- Kubernetes with service networking
- Advanced container networking

**Examples**:
```env
# Single container (default, don't set)
# INTERNAL_API_URL=http://localhost:5055

# Multi-container Docker Compose
INTERNAL_API_URL=http://api:5055

# Kubernetes
INTERNAL_API_URL=http://api-service.namespace.svc.cluster.local:5055
```

**Why two URLs?**
- `API_URL`: External/public URL browsers use (can be `https://your-domain.com`)
- `INTERNAL_API_URL`: Internal container networking (usually `http://localhost:5055` or service name)

---

### API_CLIENT_TIMEOUT

**Purpose**: Maximum time to wait for API responses

**Required**: No

**Default**: `300` (5 minutes)

**When to increase**:
- Using slow AI providers
- Local Ollama on CPU
- Processing very large documents
- Remote LM Studio over slow network

**Examples**:
```env
# Fast cloud APIs (default)
API_CLIENT_TIMEOUT=300

# Local Ollama on CPU
API_CLIENT_TIMEOUT=600

# Very large documents
API_CLIENT_TIMEOUT=900
```

**Recommendations**:
- OpenAI, Anthropic, Groq: 300 seconds
- Ollama on GPU: 300 seconds
- Ollama on CPU: 600+ seconds
- Remote LM Studio: 900+ seconds

---

### ESPERANTO_LLM_TIMEOUT

**Purpose**: Timeout for AI model inference at the library level

**Required**: No

**Default**: `60` (1 minute)

**When to increase**:
- Local models timing out during inference
- Large models on CPU
- Remote self-hosted LLMs

**Examples**:
```env
# Fast cloud APIs (default)
ESPERANTO_LLM_TIMEOUT=60

# Local Ollama with small models
ESPERANTO_LLM_TIMEOUT=120

# Large models on CPU
ESPERANTO_LLM_TIMEOUT=300
```

**Important**:
- Should be LOWER than `API_CLIENT_TIMEOUT`
- Only increase if models timeout during inference
- If transformations complete but timeout, increase `API_CLIENT_TIMEOUT` first

---

## 🗄️ Database Configuration

### SURREAL_URL

**Purpose**: WebSocket URL for SurrealDB connection

**Required**: Yes

**Format**: `ws://host:port/rpc` or `wss://host:port/rpc`

**Examples**:
```env
# Single container (default)
SURREAL_URL=ws://localhost:8000/rpc

# Multi-container Docker Compose
SURREAL_URL=ws://surrealdb:8000/rpc

# Remote SurrealDB with SSL
SURREAL_URL=wss://db.example.com:8000/rpc
```

---

### SURREAL_USER

**Purpose**: SurrealDB authentication username

**Required**: Yes

**Default**: `root` (for development)

**Production**: Change to a secure username

**Example**:
```env
# Development
SURREAL_USER=root

# Production
SURREAL_USER=open_notebook_admin
```

---

### SURREAL_PASSWORD

**Purpose**: SurrealDB authentication password

**Required**: Yes

**Default**: `root` (for development)

**Production**: Change to a strong password

**Example**:
```env
# Development
SURREAL_PASSWORD=root

# Production
SURREAL_PASSWORD=your_secure_password_here
```

---

### SURREAL_NAMESPACE

**Purpose**: SurrealDB namespace for data isolation

**Required**: Yes

**Default**: `open_notebook`

**Example**:
```env
SURREAL_NAMESPACE=open_notebook
```

---

### SURREAL_DATABASE

**Purpose**: SurrealDB database name

**Required**: Yes

**Common values**: `production`, `staging`, `development`

**Example**:
```env
# Production
SURREAL_DATABASE=production

# Staging
SURREAL_DATABASE=staging
```

---

## 🤖 AI Provider Configuration

### OpenAI

```env
# Required for OpenAI models
OPENAI_API_KEY=sk-...

# Optional: Custom endpoint
OPENAI_API_BASE=https://api.openai.com/v1
```

**Get your key**: [platform.openai.com](https://platform.openai.com)

**Provides**:
- Language models (GPT-4, GPT-3.5)
- Embeddings (text-embedding-3)
- Text-to-speech
- Speech-to-text

---

### Anthropic

```env
ANTHROPIC_API_KEY=sk-ant-...
```

**Get your key**: [console.anthropic.com](https://console.anthropic.com)

**Provides**:
- Claude models (Claude 3.5 Sonnet, Opus, Haiku)

---

### Google Gemini

```env
# Google AI Studio
GOOGLE_API_KEY=AIzaSy...

# Optional: Custom endpoint (for Vertex AI, proxies)
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com
```

**Get your key**: [makersuite.google.com](https://makersuite.google.com)

**Provides**:
- Gemini models (best for long context)
- Embeddings
- Text-to-speech

---

### Google Vertex AI

```env
VERTEX_PROJECT=my-google-cloud-project
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
VERTEX_LOCATION=us-east5
```

**Setup**: Requires Google Cloud project and service account

---

### Groq

```env
GROQ_API_KEY=gsk_...
```

**Get your key**: [console.groq.com](https://console.groq.com)

**Provides**:
- Fast inference for Llama, Mixtral models
- Speech-to-text

---

### Ollama

```env
# Local Ollama
OLLAMA_API_BASE=http://localhost:11434

# Remote Ollama
OLLAMA_API_BASE=http://192.168.1.100:11434
```

**Setup**: Install Ollama from [ollama.ai](https://ollama.ai)

**Provides**:
- Local language models
- Local embeddings
- No API key required

---

### Mistral

```env
MISTRAL_API_KEY=...
```

**Get your key**: [console.mistral.ai](https://console.mistral.ai)

---

### DeepSeek

```env
DEEPSEEK_API_KEY=...
```

**Get your key**: [platform.deepseek.com](https://platform.deepseek.com)

**Provides**:
- DeepSeek models including reasoning models (R1)

---

### xAI

```env
XAI_API_KEY=...
```

**Get your key**: [x.ai](https://x.ai)

**Provides**:
- Grok models

---

### OpenRouter

```env
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=...
```

**Get your key**: [openrouter.ai](https://openrouter.ai)

**Provides**:
- Access to multiple models through one API

---

### OpenAI Compatible Endpoints

For LM Studio, vLLM, or other OpenAI-compatible servers:

```env
# Generic configuration (all modalities)
OPENAI_COMPATIBLE_BASE_URL=http://localhost:1234/v1
OPENAI_COMPATIBLE_API_KEY=optional-key

# Mode-specific (overrides generic)
OPENAI_COMPATIBLE_BASE_URL_LLM=http://localhost:1234/v1
OPENAI_COMPATIBLE_API_KEY_LLM=...

OPENAI_COMPATIBLE_BASE_URL_EMBEDDING=http://localhost:8080/v1
OPENAI_COMPATIBLE_API_KEY_EMBEDDING=...

OPENAI_COMPATIBLE_BASE_URL_STT=http://localhost:9000/v1
OPENAI_COMPATIBLE_API_KEY_STT=...

OPENAI_COMPATIBLE_BASE_URL_TTS=http://localhost:9000/v1
OPENAI_COMPATIBLE_API_KEY_TTS=...
```

---

### Azure OpenAI

```env
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
```

---

### ElevenLabs

```env
ELEVENLABS_API_KEY=...

# Optional: Control concurrent TTS requests
TTS_BATCH_SIZE=2
```

**Get your key**: [elevenlabs.io](https://elevenlabs.io)

**Provides**:
- High-quality text-to-speech for podcasts

**Recommendations**:
- OpenAI: `TTS_BATCH_SIZE=5`
- ElevenLabs: `TTS_BATCH_SIZE=2`
- Google: `TTS_BATCH_SIZE=4`

---

### Voyage AI

```env
VOYAGE_API_KEY=...
```

**Get your key**: [voyageai.com](https://voyageai.com)

**Provides**:
- High-quality embeddings

---

## 🔧 Additional Services

### Firecrawl

```env
FIRECRAWL_API_KEY=...
```

**Get your key**: [firecrawl.dev](https://firecrawl.dev)

**Provides**:
- Enhanced web scraping
- Better content extraction

---

### Jina AI

```env
JINA_API_KEY=...
```

**Get your key**: [jina.ai](https://jina.ai)

**Provides**:
- Web content extraction
- Document processing

---

## 🐛 Debugging

### LangSmith Tracing

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=Open Notebook
```

**Get your key**: [smith.langchain.com](https://smith.langchain.com)

**Provides**:
- Detailed LLM call tracing
- Performance monitoring
- Debugging assistance

---

## 📝 Example Configurations

### Minimal Setup (OpenAI Only)

```env
# Database
SURREAL_URL=ws://localhost:8000/rpc
SURREAL_USER=root
SURREAL_PASSWORD=root
SURREAL_NAMESPACE=open_notebook
SURREAL_DATABASE=production

# AI Provider
OPENAI_API_KEY=sk-...
```

---

### Multi-Provider Setup

```env
# Database
SURREAL_URL=ws://localhost:8000/rpc
SURREAL_USER=root
SURREAL_PASSWORD=root
SURREAL_NAMESPACE=open_notebook
SURREAL_DATABASE=production

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
OLLAMA_API_BASE=http://localhost:11434
```

---

### Production Setup with Custom Domain

```env
# API Configuration
API_URL=https://notebook.example.com

# Database (secure credentials)
SURREAL_URL=ws://localhost:8000/rpc
SURREAL_USER=open_notebook_admin
SURREAL_PASSWORD=your_secure_password_here
SURREAL_NAMESPACE=open_notebook
SURREAL_DATABASE=production

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Timeouts (increased for reliability)
API_CLIENT_TIMEOUT=600
ESPERANTO_LLM_TIMEOUT=120
```

---

### Local Development with Ollama

```env
# Database
SURREAL_URL=ws://localhost:8000/rpc
SURREAL_USER=root
SURREAL_PASSWORD=root
SURREAL_NAMESPACE=open_notebook
SURREAL_DATABASE=development

# Local AI
OLLAMA_API_BASE=http://localhost:11434

# Optional: Cloud AI for embeddings
OPENAI_API_KEY=sk-...

# Increased timeouts for local models
API_CLIENT_TIMEOUT=900
ESPERANTO_LLM_TIMEOUT=300
```

---

## 🔒 Security Best Practices

### Never Commit Secrets

```bash
# ❌ DON'T commit .env files
git add .env

# ✅ DO use .env.example as template
git add .env.example
```

### Use Platform Secret Management

- **Railway**: Environment variables in dashboard
- **Render**: Environment variables in service settings
- **AWS**: AWS Secrets Manager
- **Kubernetes**: Kubernetes Secrets

### Rotate Keys Regularly

- API keys: Every 90 days
- Database passwords: Every 180 days
- Document rotation procedures

### Use Strong Passwords

```bash
# Generate secure password
openssl rand -base64 32
```

---

## 🆘 Troubleshooting

### "Unable to connect to server"

Check `API_URL` configuration:
```env
# ❌ Wrong
API_URL=http://localhost:5055  # Won't work from other devices

# ✅ Correct
API_URL=http://192.168.1.100:5055  # Use actual IP
```

### "Database connection failed"

Check `SURREAL_URL` format:
```env
# ❌ Wrong
SURREAL_URL=http://localhost:8000

# ✅ Correct
SURREAL_URL=ws://localhost:8000/rpc
```

### "Timeout errors"

Increase timeouts:
```env
API_CLIENT_TIMEOUT=600
ESPERANTO_LLM_TIMEOUT=120
```

### "Invalid API key"

Verify key format:
- OpenAI: Starts with `sk-`
- Anthropic: Starts with `sk-ant-`
- Google: Starts with `AIzaSy`
- Groq: Starts with `gsk_`

---

## 📚 Additional Resources

- [Docker Deployment Guide](docker.md)
- [Cloud Platform Deployment](cloud-platforms.md)
- [Production Checklist](production-checklist.md)
- [Troubleshooting Guide](../troubleshooting/index.md)

---

**Need help?** Join our [Discord community](https://discord.gg/37XJPXfz2w) for support!
