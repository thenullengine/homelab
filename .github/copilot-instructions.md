# Homelab AI Infrastructure - Copilot Instructions

## Architecture Overview

This is a containerized AI homelab setup combining **Open WebUI** (AI chat interface) with **SearXNG** (meta-search engine) to enable web search capabilities in AI conversations.

### Key Components
- **Open WebUI**: CUDA-enabled AI interface (port 3000) that connects to native Ollama
- **SearXNG**: Privacy-focused search aggregator (port 8888) serving as RAG web search backend
- **n8n**: Workflow automation platform (port 5678) for building integrations and automations
- **Shared Network**: `ai_network` enables service-to-service communication

## Essential Patterns

### Docker Compose Structure
Each service uses separate compose files in their own directories:
```
openwebui/docker-compose.yml    # AI interface with GPU support
searxng/docker-compose.yml      # Search engine with custom config
n8n/docker-compose.yml          # Workflow automation platform
```

### Volume Mounts & Configuration
- SearXNG uses **read-only config mount**: `./settings.yml:/etc/searxng/settings.yml:ro`
- Config/data directories are mounted but typically empty (runtime files)
- Open WebUI persists data in named volume: `open-webui_data`

### Environment Integration
- Open WebUI connects to **native Ollama** via `host.docker.internal:11434`
- SearXNG secret stored in `.env` file: `SEARXNG_SECRET=<value>`
- RAG web search configured with SearXNG endpoint: `http://searxng:8080/search?q=<query>`

## Development Workflows

### Starting Services
```powershell
# Start core services (order matters for dependencies)
cd searxng; docker-compose up -d
cd ../openwebui; docker-compose up -d 
cd ../n8n; docker-compose up -d

# Or start all services from root (if network exists)
# docker-compose -f searxng/docker-compose.yml -f openwebui/docker-compose.yml -f n8n/docker-compose.yml up -d
```

### Configuration Changes
- **SearXNG settings**: Edit `searxng/settings.yml`, restart container
- **Search engines**: Modify `engines:` section in settings.yml
- **Open WebUI environment**: Edit docker-compose.yml environment vars

### Network Architecture
- External network `ai_network` must exist before services start
- Services communicate via container names (searxng, open-webui)
- Host access patterns: `host.docker.internal` for native services

## Critical Conventions

### Security & Secrets
- `.env` file contains sensitive values (gitignored)
- SearXNG settings mounted read-only for safety
- No API keys exposed in compose files

### GPU Configuration
Open WebUI uses CUDA image with proper device reservation:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### Port Mapping Strategy
- Open WebUI: Host 3000 → Container 8080 (user access)
- SearXNG: Host 8888 → Container 8080 (testing/admin)
- n8n: Host 5678 → Container 5678 (workflow automation)
- Internal service communication uses container names, not ports

## Integration Points

### RAG Web Search Configuration
Open WebUI → SearXNG integration requires specific environment variables:
- `ENABLE_RAG_WEB_SEARCH=true`
- `RAG_WEB_SEARCH_ENGINE=searxng` 
- `SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>`

### SearXNG Engine Configuration
Key settings in `searxng/settings.yml`:
- Server bind: `127.0.0.1:8888` (internal)
- Search engines enabled/disabled via `disabled: true/false`
- Custom engine shortcuts and categories

## Common Operations

### Adding New Search Engines
Edit `searxng/settings.yml` engines section, restart SearXNG container.

### Scaling/Resource Changes
Modify `deploy.resources` in compose files, recreate containers.

### Debug Service Communication
Check container logs and network connectivity between services on `ai_network`.