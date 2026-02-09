# Cisco LLM Integration with LiteLLM

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR APPLICATION                             │
│                      (proxy_test.py, etc.)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP Request
                             │ POST /v1/chat/completions
                             │ model: "cisco-llm"
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       LITELLM PROXY                                  │
│                    (localhost:4000)                                  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  1. Request Handler                                         │   │
│  │     - Validates master_key                                  │   │
│  │     - Parses model name: "cisco-llm"                       │   │
│  └────────────────────┬───────────────────────────────────────┘   │
│                       │                                             │
│                       ▼                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  2. get_llm_provider()                                      │   │
│  │     model: "cisco-llm" → config lookup                     │   │
│  │     Returns:                                                │   │
│  │       - model: "openai/gpt-4.1"                         │   │
│  │       - provider: "openai"                                  │   │
│  │       - api_base: "https://chat-ai.cisco.com/..."         │   │
│  │       - api_key: from config or env                        │   │
│  └────────────────────┬───────────────────────────────────────┘   │
│                       │                                             │
│                       ▼                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  3. Callbacks (Pre-Call Hook)                              │   │
│  │                                                             │   │
│  │     ┌─────────────────────────────────────────┐           │   │
│  │     │  cisco_callback.py                       │           │   │
│  │     │  ═════════════════════════                │           │   │
│  │     │  • Detects Cisco model/api_base         │           │   │
│  │     │  • Calls get_cisco_token()               │           │   │
│  │     │  • Injects fresh token into request     │           │   │
│  │     └────────────┬────────────────────────────┘           │   │
│  │                  │                                          │   │
│  │                  ▼                                          │   │
│  │     ┌─────────────────────────────────────────┐           │   │
│  │     │  cisco_provider.py (TokenManager)        │           │   │
│  │     │  ═══════════════════════════════════     │           │   │
│  │     │  1. Check cache (/tmp/.cisco_token.json)│           │   │
│  │     │  2. If expired/missing:                  │           │   │
│  │     │     - OAuth2 request to Cisco            │           │   │
│  │     │     - Base64 encode credentials          │           │   │
│  │     │     - POST to id.cisco.com/oauth2        │           │   │
│  │     │  3. Cache token with expiry              │           │   │
│  │     │  4. Return fresh token                   │           │   │
│  │     └─────────────────────────────────────────┘           │   │
│  │                                                             │   │
│  └────────────────────┬───────────────────────────────────────┘   │
│                       │                                             │
│                       ▼                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  4. OpenAI Provider Handler                                 │   │
│  │     - Formats request as OpenAI API                        │   │
│  │     - Adds Authorization: Bearer <fresh_token>             │   │
│  │     - Adds api-key header: <fresh_token>                   │   │
│  └────────────────────┬───────────────────────────────────────┘   │
└────────────────────────┼───────────────────────────────────────────┘
                         │
                         │ HTTPS Request
                         │ Authorization: Bearer eyJ...
                         │ api-key: eyJ...
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CISCO CIRCUIT API                                 │
│            https://chat-ai.cisco.com/openai/deployments/...         │
│                                                                      │
│  • Validates OAuth2 token                                           │
│  • Processes request                                                │
│  • Returns OpenAI-compatible response                               │
└─────────────────────────────────────────────────────────────────────┘
```

## How It Works

### 1. Configuration (`proxy_config_docker.yaml`)

```yaml
model_list:
  - model_name: "cisco-llm"
    litellm_params:
      model: openai/gpt-4.1
      api_base: "https://chat-ai.cisco.com/openai/deployments/gpt-4.1"
      api_key: os.environ/CISCO_API_TOKEN  # or fetched dynamically
      custom_llm_provider: openai

litellm_settings:
  callbacks: ["otel", "cisco_callback.cisco_handler"]  # Registers our callback
```

**Key Points:**
- `model: openai/gpt-4.1` - The `openai/` prefix tells LiteLLM to use OpenAI provider format
- `custom_llm_provider: openai` - Explicitly sets the provider type
- `api_base` - Points to Cisco's OpenAI-compatible endpoint
- `cisco_callback.cisco_handler` - Our custom callback instance for token injection

### 2. Token Management Flow

#### Step 1: Client Makes Request
```python
client = openai.OpenAI(
    api_key="sk-1234",  # LiteLLM master key
    base_url="http://localhost:4000/v1"
)
response = client.chat.completions.create(
    model="cisco-llm",
    messages=[...]
)
```

#### Step 2: LiteLLM Proxy Receives Request
- Validates master_key (`sk-1234`)
- Looks up `cisco-llm` in `model_list`
- Extracts litellm_params

#### Step 3: Pre-Call Hook (cisco_callback.py)
```python
def async_pre_call_hook(user_api_key_dict, cache, data, call_type):
    model = data.get("model")
    api_base = data.get("api_base")
    
    # Detect Cisco model
    if "cisco" in model or "chat-ai.cisco.com" in api_base:
        # Get fresh token
        fresh_token = get_cisco_token()  # ← Calls TokenManager
        app_key = os.getenv("CISCO_APP_KEY")
        
        # Inject token into request
        data["api_key"] = fresh_token
        
        # Add Cisco-specific headers for Apigee gateway validation
        extra_headers = data.get("extra_headers", {}) or {}
        extra_headers.update({
            "oauthtoken": fresh_token,  # Required by Apigee policy
            "api-key": fresh_token,
        })
        data["extra_headers"] = extra_headers
        
        # Inject user appkey if configured (required by Cisco API)
        if app_key and not data.get("user"):
            data["user"] = json.dumps({"appkey": app_key})
```

#### Step 4: Token Manager (cisco_provider.py)
```python
class CiscoTokenManager:
    def get_token(self):
        # 1. Check cache
        cached = self._get_cached_token()
        if cached and not_expired:
            return cached
        
        # 2. Fetch new token via OAuth2
        response = requests.post(
            "https://id.cisco.com/oauth2/default/v1/token",
            headers={"Authorization": f"Basic {base64_credentials}"},
            data="grant_type=client_credentials"
        )
        
        # 3. Cache token
        token = response.json()["access_token"]
        expires_in = response.json()["expires_in"]
        self._cache_token(token, expires_in)
        
        return token
```

#### Step 5: Request to Cisco
LiteLLM's OpenAI provider handler sends:
```http
POST https://chat-ai.cisco.com/openai/deployments/gpt-4.1/chat/completions
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
api-key: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "model": "gpt-4.1",
  "messages": [...],
  "stream": true
}
```

### 3. Token Lifecycle

```
Time: 0min          Token fetched (expires in 60min)
      ↓
Time: 5min          Request → Use cached token ✓
      ↓
Time: 30min         Request → Use cached token ✓
      ↓
Time: 55min         Token will expire in 5min
      ↓             get_token() sees expiry approaching
      ↓             Fetches new token automatically
Time: 55min         New token cached
      ↓
Time: 56min         Request → Use new cached token ✓
```

**Cache Policy:**
- Tokens cached in `/tmp/.cisco_token.json`
- Auto-refresh 5 minutes before expiry
- Thread-safe for concurrent requests
- Survives LiteLLM restarts (uses file cache)

## Two Integration Approaches

### Approach A: Environment Variable + Script (Simplest)
```bash
# start_proxy_with_cisco.sh fetches token and sets env
export CISCO_API_TOKEN=$(python -c "from cisco_provider import get_cisco_token; print(get_cisco_token())")
litellm --config proxy_config_docker.yaml
```

**Pros:** 
- Simple, no code changes
- Works with standard LiteLLM

**Cons:** 
- Token doesn't auto-refresh during runtime
- Need wrapper script

### Approach B: Callback Hook (Recommended)
```yaml
litellm_settings:
  callbacks: ["cisco_callback"]
```

**Pros:**
- Token refreshes automatically on every request
- No external scripts needed
- Works with Docker/Kubernetes

**Cons:**
- Requires callback implementation
- Slightly more complex

## Key Components

### 1. `cisco_provider.py`
- **CiscoTokenManager**: Handles OAuth2 flow and caching
- **get_cisco_token()**: Convenience function for getting tokens

### 2. `cisco_callback.py`
- **CiscoTokenCallback**: LiteLLM CustomLogger callback class
- **async_pre_call_hook()** & **pre_call_hook()**: Inject tokens, headers, and user appkey before requests
- **async_post_call_streaming_iterator_hook()**: Handles streaming responses
- Must expose `cisco_handler` instance at module level for registration

**Critical Requirements:**
- Injects `extra_headers` with `oauthtoken` and `api-key` for Apigee validation
- Injects `user` field with `{"appkey": "..."}` JSON string (required by Cisco API)
- Without these injections, requests fail with 401 (missing headers) or 422 (missing user field)

### 3. `proxy_config_docker.yaml`
- Defines the `cisco-llm` model
- Configures callbacks and settings
- Maps to Cisco's OpenAI-compatible endpoint

### 4. `test_cisco_integration.py`
- Tests token fetching and caching
- Validates environment setup
- Confirms integration works

## Environment Variables

```bash
# Required
export CISCO_CLIENT_ID=your_client_id
export CISCO_CLIENT_SECRET=your_client_secret
export CISCO_APP_KEY=your_app_key  # Required for user field injection

# The callback automatically injects:
# - OAuth2 token into api_key
# - oauthtoken header (for Apigee validation)
# - api-key header (for Apigee validation)
# - user field with {"appkey": "..."} (required by Cisco API)
```

## Usage Example

```python
import openai

client = openai.OpenAI(
    api_key="sk-1234",  # Your LiteLLM master key
    base_url="http://localhost:4000/v1"
)

# Just use it - tokens are handled automatically!
response = client.chat.completions.create(
    model="cisco-llm",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

## Testing

```bash
# 1. Test token manager
python litellm-custom/test_cisco_integration.py

# 2. Start proxy
cd litellm-custom
litellm --config proxy_config_docker.yaml --port 4000

# 3. Test with your app
python litellm-custom/proxy_test.py
```

## Security Notes

1. **Token Cache**: Stored in `/tmp/.cisco_token.json` with 0600 permissions
2. **Credentials**: Never logged or printed (except in debug mode)
3. **Token Expiry**: Always refreshed 5 minutes early to avoid expiration
4. **HTTPS Only**: All communication with Cisco uses HTTPS

## Troubleshooting

### 401 Error: "Failed to Resolve Variable: policy(JWT-validateToken)"
This means the Cisco Apigee gateway couldn't validate the OAuth token. The callback must inject both `oauthtoken` and `api-key` headers:
```python
extra_headers = {
    "oauthtoken": fresh_token,
    "api-key": fresh_token,
}
```

### 422 Error: Field required - "user"
The Cisco API requires a `user` field with appkey JSON:
```python
data["user"] = json.dumps({"appkey": app_key})
```
Make sure `CISCO_APP_KEY` environment variable is set.

### Token fetch fails
```bash
# Test credentials
python -c "from cisco_provider import get_cisco_token; print(get_cisco_token())"
```

### Callback not firing
Check that `cisco_callback.cisco_handler` is in your callbacks list and the file is importable:
```yaml
litellm_settings:
  callbacks: ["cisco_callback.cisco_handler"]
```

### Token expires mid-request
The 5-minute early refresh should prevent this. If it happens, increase the buffer in `_get_cached_token()`.

## Comparison with Pure OAuth2 Client

| Feature | Your TokenManager | LiteLLM Integration |
|---------|-------------------|---------------------|
| Token Refresh | Manual (call `get_token()`) | Automatic (per request) |
| Caching | File-based | File-based |
| Thread Safety | ✓ | ✓ |
| Langchain Compatible | ✓ (via `create_cisco_chat_llm()`) | N/A |
| Multi-Model Proxy | ✗ | ✓ |
| Cost Tracking | ✗ | ✓ (built into LiteLLM) |
| OpenTelemetry | Manual | ✓ (built into LiteLLM) |

## Why This Works

LiteLLM's architecture has three key extension points:

1. **`get_llm_provider()`** - Determines which provider to use
2. **Callbacks** - Hook into request lifecycle
3. **Environment Variables** - Dynamic credential injection

We use **callbacks** (#2) to inject fresh tokens just before each request, ensuring:
- Tokens never expire mid-request
- No manual token management needed
- Works seamlessly with LiteLLM's existing infrastructure

The token manager handles the OAuth2 complexity, while LiteLLM handles everything else (routing, streaming, cost tracking, logging).
