# LiteLLM Cisco Proxy - Production Setup

## Overview

This is a production-ready setup for LiteLLM proxy with:
- **PostgreSQL database** for key management and spend tracking
- **Automated team key creation** on startup
- **Cisco LLM integration** with OAuth2 token management
- **OpenTelemetry observability** for monitoring
- **Streaming support** for time-to-first-token measurements

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   PostgreSQL    │◄────►│  LiteLLM Proxy   │◄────►│   Cisco LLM     │
│   (Database)    │      │  (Authentication)│      │   (via OAuth2)  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   OpenTelemetry  │
                         │   (Observability)│
                         └──────────────────┘
```

## Features

### Automated Key Management
- **Master Key**: Used for admin operations
- **Team A Key**: Automatically created with $100 budget
- **Team B Key**: Automatically created with $50 budget
- Keys are created automatically on first startup
- Idempotent: Safe to restart without duplicating keys

### Database-Backed Authentication
- All keys stored in PostgreSQL
- Spend tracking per team
- Budget enforcement
- Usage analytics

### Streaming Support
- Real-time token streaming
- Time-to-first-token (TTFT) measurement
- Full streaming response support

## Quick Start

### 1. Set Environment Variables

Copy the environment template:
```bash
cp env.template.example .env
```

Edit `.env` with your credentials:
```bash
# Required
CISCO_CLIENT_ID=your-client-id
CISCO_CLIENT_SECRET=your-client-secret

# Optional (defaults provided)
POSTGRES_PASSWORD=litellm_password_change_in_prod
LITELLM_MASTER_KEY=sk-master-key-change-in-prod
TEAM_A_KEY=sk-team-a-key-12345
TEAM_B_KEY=sk-team-b-key-67890
```

### 2. Start Services

```bash
docker-compose -f docker-compose.cisco.yml up -d
```

This will:
1. Start PostgreSQL database
2. Wait for database to be healthy
3. Start LiteLLM proxy
4. Automatically create team keys

### 3. Verify Setup

Check logs:
```bash
docker-compose -f docker-compose.cisco.yml logs litellm-cisco | grep "Key Initialization"
```

Expected output:
```
✓ Key created successfully: Team A API Key
✓ Key created successfully: Team B API Key
```

### 4. Test with Streaming

```bash
# Activate virtual environment
source ../.venv/bin/activate

# Run test with Team A key
TEAM_A_KEY="sk-team-a-key-12345" python cisco_test.py
```

Expected output:
```
=== OpenTelemetry Poetry Generator (via LiteLLM Proxy) ===
Using Team A key (sk-team-a-key-12345...)

[Time to First Token: 2.077s]
<streaming poem output>
[Total time: 3.712s]
```

## Configuration Files

### docker-compose.cisco.yml
- Defines PostgreSQL and LiteLLM services
- Sets up health checks and dependencies
- Configures environment variables

### cisco-llm.yml
- Model configuration (Cisco LLM, GPT-4.1)
- Callback configuration (OpenTelemetry, Cisco token handler)
- Database connection settings

### init-keys.sh
- Automated key creation script
- Runs in background on startup
- Idempotent (safe to run multiple times)

### cisco_test.py
- Test script with streaming support
- Uses Team A key by default
- Measures TTFT and total response time

## Team Keys

| Team | Key | Budget | Models |
|------|-----|--------|--------|
| Team A | sk-team-a-key-12345 | $100 | cisco-llm, gpt-4.1 |
| Team B | sk-team-b-key-67890 | $50 | cisco-llm, gpt-4.1 |

**Note**: Change these keys in production!

## API Endpoints

- **Base URL**: http://localhost:4000
- **Health**: http://localhost:4000/health/readiness
- **Completions**: http://localhost:4000/v1/chat/completions
- **Admin UI**: http://localhost:4000/ui (requires master key)

## Using Team Keys

### Python Example
```python
import openai

client = openai.OpenAI(
    api_key="sk-team-a-key-12345",  # Team A key
    base_url="http://localhost:4000/v1"
)

response = client.chat.completions.create(
    model="cisco-llm",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True  # Enable streaming
)

for chunk in response:
    print(chunk.choices[0].delta.content, end='')
```

### cURL Example
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-team-a-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cisco-llm",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

## Cluster Deployment

This setup is designed for automated deployment to Kubernetes or similar:

1. **No Manual Intervention**: Keys created automatically on startup
2. **StatefulSets**: PostgreSQL data persisted across restarts
3. **Health Checks**: Built-in readiness probes
4. **Secrets Management**: Use Kubernetes secrets for sensitive values
5. **Horizontal Scaling**: LiteLLM proxy can scale horizontally

### Kubernetes Example

```yaml
# Convert to Kubernetes manifests using kompose
kompose convert -f docker-compose.cisco.yml
```

Or use Helm chart:
```bash
helm install litellm-cisco ./charts/litellm-cisco \
  --set cisco.clientId=$CISCO_CLIENT_ID \
  --set cisco.clientSecret=$CISCO_CLIENT_SECRET \
  --set postgresql.password=$POSTGRES_PASSWORD
```

## Monitoring

### OpenTelemetry
- Traces exported to http://host.docker.internal:4317
- Metrics tracking for all requests
- Custom attributes for Cisco integration

### Database Metrics
- Spend per team tracked in real-time
- Budget limits enforced
- Usage analytics available

### Logs
```bash
# View all logs
docker-compose -f docker-compose.cisco.yml logs -f

# View key initialization
docker-compose -f docker-compose.cisco.yml exec litellm-cisco cat /var/log/init-keys.log

# View database logs
docker-compose -f docker-compose.cisco.yml logs postgres
```

## Troubleshooting

### Keys Not Created
```bash
# Check initialization log
docker-compose -f docker-compose.cisco.yml exec litellm-cisco cat /var/log/init-keys.log

# Manually run initialization
docker-compose -f docker-compose.cisco.yml exec litellm-cisco /app/init-keys.sh
```

### Database Connection Issues
```bash
# Check database health
docker-compose -f docker-compose.cisco.yml exec postgres pg_isready -U litellm_user -d litellm

# Check connection from proxy
docker-compose -f docker-compose.cisco.yml exec litellm-cisco \
  python3 -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### Authentication Errors
```bash
# Verify key exists in database
docker-compose -f docker-compose.cisco.yml exec postgres \
  psql -U litellm_user -d litellm -c "SELECT token, team_id FROM \"LiteLLM_VerificationToken\" LIMIT 5;"
```

## Security Considerations

### Production Changes Required

1. **Change all default keys**:
   - LITELLM_MASTER_KEY
   - TEAM_A_KEY
   - TEAM_B_KEY
   - POSTGRES_PASSWORD

2. **Use secrets management**:
   - Kubernetes Secrets
   - AWS Secrets Manager
   - HashiCorp Vault

3. **Network security**:
   - Use TLS/SSL for database connections
   - Deploy behind API gateway with rate limiting
   - Use private networks for service communication

4. **Remove localhost binding**:
   - Change `127.0.0.1:4000:4000` to `4000:4000` for cluster access
   - Or use ingress controller for external access

## Maintenance

### Backup Database
```bash
docker-compose -f docker-compose.cisco.yml exec postgres \
  pg_dump -U litellm_user litellm > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
cat backup_20260212.sql | docker-compose -f docker-compose.cisco.yml exec -T postgres \
  psql -U litellm_user litellm
```

### Update LiteLLM Version
1. Update `Dockerfile.cisco` base image
2. Rebuild: `docker-compose -f docker-compose.cisco.yml build`
3. Restart: `docker-compose -f docker-compose.cisco.yml up -d`

## License

See main repository LICENSE file.
