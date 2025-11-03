# n8n Workflow Automation

n8n is a fair-code workflow automation platform that helps you automate repetitive tasks, sync data between different services, and build powerful integrations.

## Quick Start

```powershell
# Navigate to n8n directory
cd n8n

# Start n8n service
docker-compose up -d

# Check service status
docker-compose logs -f n8n
```

## Access

- **Web Interface**: http://localhost:5678
- **Container**: `n8n`
- **Network**: `ai_network`

## Configuration

### Environment Variables

Key environment variables in `docker-compose.yml`:

- `GENERIC_TIMEZONE` / `TZ`: Set your timezone (configured for Europe/London)
- `N8N_RUNNERS_ENABLED`: Enables task runners for better performance
- `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS`: Security enforcement

### Database

By default, n8n uses SQLite stored in the persistent volume. For production setups, PostgreSQL is recommended:

1. Uncomment PostgreSQL environment variables in `docker-compose.yml`
2. Set up a PostgreSQL container or external instance
3. Update the connection details

### Security

For production environments, enable basic authentication:

1. Uncomment the basic auth environment variables
2. Set secure credentials in the main `.env` file
3. Consider using HTTPS with a reverse proxy

## Integration with Other Services

### SearXNG Integration

n8n is configured to use SearXNG for web search tools:

```yaml
- 'SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>'
```

Use the **SearXNG Tool** in AI Agent workflows for web research automation.

### Native Ollama Integration

n8n can connect to your native Ollama installation:

```yaml
- 'OLLAMA_BASE_URL=http://host.docker.internal:11434'
```

Use **Ollama Chat Model** nodes in LangChain workflows with your local AI models.

### Network Architecture

- Connected to the shared `ai_network`
- Can communicate with other services (searxng, open-webui)
- Access via container name: `n8n`

## Data Persistence

- **Volume**: `n8n_data` mounted to `/home/node/.n8n`
- **Contains**: Workflows, credentials, execution data, encryption keys
- **Backup**: Regular backup of this volume is recommended

## Common Operations

### View Logs
```powershell
docker-compose logs -f n8n
```

### Restart Service
```powershell
docker-compose restart n8n
```

### Update n8n
```powershell
docker-compose pull
docker-compose down
docker-compose up -d
```

### CLI Access
```powershell
docker-compose exec n8n /bin/sh
```

## Troubleshooting

### First Setup
1. Navigate to http://localhost:5678
2. Set up your first admin account
3. Start building workflows

### Common Issues
- **Port conflicts**: Ensure port 5678 is not used by other services
- **Permission issues**: Check file permissions on the mounted volume
- **Network issues**: Verify `ai_network` exists and is accessible

### Health Check
The container includes a health check that verifies n8n is responding on port 5678.

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Community Templates](https://n8n.io/workflows)
- [Node Reference](https://docs.n8n.io/integrations/)
- [Docker Configuration](https://docs.n8n.io/hosting/installation/docker/)