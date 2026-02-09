# Running LiteLLM with Cisco Integration in Docker

This guide explains how the Cisco integration modules are loaded into the LiteLLM Docker container.

## Architecture: How Modules Get Loaded

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Container                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Base Image: ghcr.io/berriai/litellm:main-v1.81.0    │ │
│  │  - Python 3.11                                         │ │
│  │  - LiteLLM installed                                   │ │
│  │  - All dependencies                                    │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  COPY cisco_provider.py → /app/                       │ │
│  │  COPY cisco_callback.py → /app/                       │ │
│  │  COPY docker-entrypoint.sh → /app/                    │ │
│  │  COPY proxy_config_docker.yaml → /app/config.yaml    │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Environment Variables:                                │ │
│  │  - PYTHONPATH=/app                                     │ │
│  │  - CISCO_CLIENT_ID=xxx                                │ │
│  │  - CISCO_CLIENT_SECRET=yyy                            │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Entrypoint: /app/docker-entrypoint.sh                │ │
│  │  1. Check environment variables                        │ │
│  │  2. (Optional) Pre-import cisco_callback.py           │ │
│  │     → Validates module loads correctly                 │ │
│  │  3. Start: litellm --config /app/config.yaml          │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  LiteLLM Proxy Running                                 │ │
│  │  - Loads config.yaml                                   │ │
│  │  - Imports cisco_callback.cisco_handler via config    │ │
│  │  - Registers callback for cisco-llm requests          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Three Loading Mechanisms

### 1. **PYTHONPATH** (Primary Method)
```dockerfile
WORKDIR /app
ENV PYTHONPATH=/app
COPY cisco_provider.py /app/
COPY cisco_callback.py /app/
```

**How it works:**
- `/app` is in Python's module search path
- `cisco_callback.py` can be imported with `import cisco_callback`
- `cisco_provider.py` can be imported with `import cisco_provider`

**Verification:**
```bash
docker exec -it litellm-cisco python3 -c "import sys; print(sys.path)"
# Output should include '/app'
```

### 2. **Config-Based Registration** (Recommended)
```yaml
# In proxy_config_docker.yaml
litellm_settings:
  callbacks: ["cisco_callback.cisco_handler"]
```

**How it works:**
- LiteLLM imports `cisco_callback` module
- Accesses the `cisco_handler` instance (module-level singleton)
- Registers it as a CustomLogger callback
- Callback hooks fire on every request

**Required at module level:**
```python
# At bottom of cisco_callback.py
cisco_handler = CiscoTokenCallback()
```

This ensures the callback instance is available for import and registration.

### 3. **Entrypoint Pre-loading** (Optional)
```bash
#!/bin/bash
# docker-entrypoint.sh
python3 -c "
import sys
sys.path.insert(0, '/app')
import cisco_callback  # Validates import works
"
exec litellm "$@"
```

**How it works:**
- Before starting LiteLLM, validates the module can be imported
- Useful for catching import errors early during container startup
- Not required since config-based registration handles the import

## Setup Instructions

### Option A: Build Custom Image (Recommended)

**1. Create your environment file:**
```bash
cd litellm-custom
cp env.template .env
# Edit .env with your actual credentials
```

**2. Build the image:**
```bash
docker build -f Dockerfile.cisco -t litellm-cisco:latest .
```

**3. Run with docker-compose:**
```bash
docker-compose -f docker-compose.cisco.yml up -d
```

**4. Verify it's working:**
```bash
# Check logs
docker logs litellm-cisco

# Should see:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:4000

# Test the endpoint
curl http://localhost:4000/v1/models
```

### Option B: Volume Mount (Development)

If you want to edit files without rebuilding:

```yaml
services:
  litellm-cisco:
    image: ghcr.io/berriai/litellm:main-v1.81.0
    volumes:
      # Mount Python modules
      - ./cisco_provider.py:/app/cisco_provider.py:ro
      - ./cisco_callback.py:/app/cisco_callback.py:ro
      - ./proxy_config_docker.yaml:/app/config.yaml:ro
      
      # Mount entrypoint
      - ./docker-entrypoint.sh:/app/docker-entrypoint.sh:ro
    
    environment:
      PYTHONPATH: /app
      CISCO_CLIENT_ID: ${CISCO_CLIENT_ID}
      CISCO_CLIENT_SECRET: ${CISCO_CLIENT_SECRET}
    
    entrypoint: ["/app/docker-entrypoint.sh"]
    command: ["--config", "/app/config.yaml", "--port", "4000"]
```

**Pros:**
- No rebuild needed for code changes
- Great for development

**Cons:**
- Need to restart container to pick up changes
- Slightly slower startup (no caching)

### Option C: Base Image + Startup Script

Use the official LiteLLM image and inject modules at runtime:

```dockerfile
FROM ghcr.io/berriai/litellm:main-v1.81.0
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh
ENTRYPOINT ["/startup.sh"]
```

```bash
#!/bin/bash
# startup.sh - downloads modules from S3/GitHub/etc
curl -o /app/cisco_provider.py https://your-repo/cisco_provider.py
curl -o /app/cisco_callback.py https://your-repo/cisco_callback.py
python3 -c "import cisco_callback"
exec litellm "$@"
```

## Verification Steps

### 1. Check if modules are accessible
```bash
docker exec litellm-cisco python3 -c "
import sys
sys.path.insert(0, '/app')
import cisco_provider
import cisco_callback
print('✓ Modules loaded successfully')
"
```

### 2. Verify callback registration
```bash
docker exec litellm-cisco python3 -c "
import sys
sys.path.insert(0, '/app')
import cisco_callback
print('✓ cisco_handler instance exists:', hasattr(cisco_callback, 'cisco_handler'))
print('Handler type:', type(cisco_callback.cisco_handler).__name__)
"
```

Expected output:
```
✓ cisco_handler instance exists: True
Handler type: CiscoTokenCallback
```

### 3. Test token fetching
```bash
docker exec -e CISCO_CLIENT_ID=xxx -e CISCO_CLIENT_SECRET=yyy \
  litellm-cisco python3 -c "
import sys
sys.path.insert(0, '/app')
from cisco_provider import get_cisco_token
token = get_cisco_token()
print('✓ Token fetched:', token[:20] + '...')
"
```

### 4. Test via API
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cisco-llm",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Debugging

### Module not found errors
```bash
# Check if files exist in container
docker exec litellm-cisco ls -la /app/

# Check Python path
docker exec litellm-cisco python3 -c "import sys; print(sys.path)"

# Try importing manually
docker exec litellm-cisco python3 -c "
import sys
sys.path.insert(0, '/app')
import cisco_provider
print('Success!')
"
```

### Callback not firing
```bash
# Check if callback is registered
docker exec litellm-cisco python3 -c "
import litellm
print('Callbacks:', litellm.callbacks)
"

# Check logs for registration message
docker logs litellm-cisco | grep "CiscoTokenCallback"
```

### Token fetching fails
```bash
# Test token manager directly
docker exec litellm-cisco python3 -c "
import sys
sys.path.insert(0, '/app')
from cisco_provider import get_cisco_token
try:
    token = get_cisco_token()
    print('Token:', token[:30])
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
"
```

## File Structure in Container

```
/app/
├── cisco_provider.py          # Token manager
├── cisco_callback.py          # LiteLLM callback
├── config.yaml                # LiteLLM configuration
├── docker-entrypoint.sh       # Startup script
└── /tmp/
    └── .cisco_token.json      # Token cache (created at runtime)
```

## Environment Variables Hierarchy

**Required Variables:**
- `CISCO_CLIENT_ID` - OAuth2 client ID for Cisco API
- `CISCO_CLIENT_SECRET` - OAuth2 client secret for Cisco API
- `CISCO_APP_KEY` - Application key for user field injection (required by Cisco API)

**Loading Order:**
1. **Docker Compose .env file** → Read by docker-compose
2. **Environment section in docker-compose.yml** → Set in container
3. **ENV in Dockerfile** → Baked into image (defaults)
4. **Runtime -e flags** → Override at container start

Example:
```bash
# .env file
CISCO_CLIENT_ID=from_env_file
CISCO_CLIENT_SECRET=your_secret
CISCO_APP_KEY=your_app_key

# docker-compose.yml
environment:
  CISCO_CLIENT_ID: ${CISCO_CLIENT_ID}  # Uses value from .env
  CISCO_CLIENT_SECRET: ${CISCO_CLIENT_SECRET}
  CISCO_APP_KEY: ${CISCO_APP_KEY}

# Runtime override
docker run -e CISCO_CLIENT_ID=override_value \
  -e CISCO_CLIENT_SECRET=override_secret \
  -e CISCO_APP_KEY=override_app_key ...
```

## Security Best Practices

### 1. Never commit credentials
```bash
# .gitignore
.env
*.env
!env.template
```

### 2. Use Docker secrets (production)
```yaml
services:
  litellm-cisco:
    secrets:
      - cisco_client_id
      - cisco_client_secret
    environment:
      CISCO_CLIENT_ID_FILE: /run/secrets/cisco_client_id
      CISCO_CLIENT_SECRET_FILE: /run/secrets/cisco_client_secret

secrets:
  cisco_client_id:
    external: true
  cisco_client_secret:
    external: true
```

### 3. Persist token cache securely
```yaml
volumes:
  cisco-token-cache:
    driver: local
    driver_opts:
      type: tmpfs  # In-memory, cleared on restart
      device: tmpfs
```

## Production Deployment

### Multi-stage build
```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM ghcr.io/berriai/litellm:main-v1.81.0
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy Cisco modules
COPY cisco_provider.py cisco_callback.py /app/
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["--config", "/app/config.yaml"]
```

### Health checks
```yaml
healthcheck:
  test: |
    curl -f http://localhost:4000/health && \
    python3 -c "import sys; sys.path.insert(0, '/app'); import cisco_callback" || exit 1
  interval: 30s
  timeout: 10s
  retries: 3
```

## Summary

The key insight is that **LiteLLM doesn't need special configuration to load custom modules** - it's just Python! 

The integration works because:
1. ✅ Files are copied into `/app/` (in `PYTHONPATH`)
2. ✅ Config references `cisco_callback.cisco_handler` for registration
3. ✅ LiteLLM imports the module and accesses the handler instance
4. ✅ Callback hooks fire automatically on matching requests

**No special LiteLLM features needed** - it's standard Python module loading + config-based callback registration!
