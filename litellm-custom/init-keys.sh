#!/bin/bash
# Initialize team API keys automatically on startup
# This script runs after LiteLLM proxy starts and creates team keys via API

set -e

echo "========================================"
echo "Initializing Team API Keys"
echo "========================================"

# Wait for LiteLLM proxy to be ready
echo "Waiting for LiteLLM proxy to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/health/readiness', timeout=1)" > /dev/null 2>&1; then
        echo "✓ LiteLLM proxy is ready"
        break
    fi
    attempt=$((attempt + 1))
    echo "  Attempt $attempt/$max_attempts - waiting..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "✗ Failed to connect to LiteLLM proxy after $max_attempts attempts"
    exit 1
fi

# Function to create or update a key
create_key() {
    local key_name=$1
    local key_value=$2
    local team_id=$3
    local max_budget=$4
    
    echo ""
    echo "Creating key: $key_name (team: $team_id)"
    
    python3 << EOF
import json
import urllib.request

url = "http://localhost:4000/key/generate"
headers = {
    "Authorization": "Bearer ${LITELLM_MASTER_KEY}",
    "Content-Type": "application/json"
}
data = {
    "key": "${key_value}",
    "team_id": "${team_id}",
    "max_budget": ${max_budget},
    "models": ["cisco-llm", "gpt-4.1"],
    "metadata": {
        "description": "${key_name}",
        "auto_created": True
    }
}

req = urllib.request.Request(url, json.dumps(data).encode(), headers)
try:
    response = urllib.request.urlopen(req)
    print("✓ Key created successfully: ${key_name}")
    exit(0)
except urllib.error.HTTPError as e:
    response_body = e.read().decode()
    if "already exists" in response_body:
        print("✓ Key already exists: ${key_name}")
        exit(0)
    else:
        print(f"✗ Failed to create key: ${key_name}")
        print(f"  HTTP Code: {e.code}")
        print(f"  Response: {response_body}")
        exit(1)
EOF
    
    return $?
}

# Create Team A key
create_key "Team A API Key" "${TEAM_A_KEY}" "team-a" 100.0

# Create Team B key
create_key "Team B API Key" "${TEAM_B_KEY}" "team-b" 50.0

echo ""
echo "========================================"
echo "Key Initialization Complete"
echo "========================================"
echo ""
echo "Available keys:"
echo "  - Team A: ${TEAM_A_KEY:0:20}..."
echo "  - Team B: ${TEAM_B_KEY:0:20}..."
echo ""
