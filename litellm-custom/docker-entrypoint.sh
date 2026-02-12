#!/bin/bash
# Entrypoint script for LiteLLM with Cisco integration
# This ensures the Cisco callback is loaded before starting the proxy

set -e

echo "================================================"
echo "LiteLLM Proxy with Cisco Integration"
echo "================================================"

# Check for Cisco credentials
if [ -n "$CISCO_CLIENT_ID" ] && [ -n "$CISCO_CLIENT_SECRET" ]; then
    echo "✓ Cisco credentials detected"
    echo "  - CISCO_CLIENT_ID: ${CISCO_CLIENT_ID:0:20}..."
    echo "  - CISCO_CLIENT_SECRET: [REDACTED]"
    
    # Pre-load the Cisco callback module to register it
    echo ""
    echo "Loading Cisco callback module..."
    python3 -c "
import sys
sys.path.insert(0, '/app')
import cisco_callback
print('Cisco callback module loaded successfully')
" || echo "Warning: Failed to pre-load Cisco callback"
    
else
    echo "⚠ Cisco credentials not set"
    echo "  Set CISCO_CLIENT_ID and CISCO_CLIENT_SECRET to enable Cisco LLM support"
fi

echo ""
echo "Starting LiteLLM proxy..."
echo "================================================"
echo ""

# Start key initialization in background (runs after proxy is ready)
if [ -n "$LITELLM_MASTER_KEY" ] && [ -n "$TEAM_A_KEY" ]; then
    echo "Key initialization will run in background..."
    /app/init-keys.sh > /var/log/init-keys.log 2>&1 &
fi

# Start LiteLLM with the provided arguments
exec litellm "$@"
