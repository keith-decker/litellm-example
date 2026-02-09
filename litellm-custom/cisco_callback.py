"""
LiteLLM callback for dynamic Cisco token injection.
This hooks into LiteLLM's request lifecycle to inject fresh tokens.
"""

import json
import os
import sys
from typing import Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cisco_provider import get_cisco_token
from litellm.integrations.custom_logger import CustomLogger


class CiscoTokenCallback(CustomLogger):
    """
    LiteLLM callback that injects fresh Cisco tokens before each request.
    
    This integrates with LiteLLM's callback system to ensure tokens are
    always fresh, even for long-running proxy instances.
    """

    def __init__(self):
        """Initialize the Cisco token callback."""
        self.name = "cisco_token_callback"

    async def async_pre_call_hook(
        self,
        user_api_key_dict: dict,
        cache: Any,
        data: dict,
        call_type: str,
    ) -> Optional[Exception]:
        """
        Called before each LiteLLM API call.
        Injects fresh Cisco token if the model is a Cisco model.
        
        Args:
            user_api_key_dict: User API key information
            cache: LiteLLM cache instance
            data: Request data containing model and parameters
            call_type: Type of call (completion, embedding, etc.)
            
        Returns:
            None if successful, Exception if there's an error
        """
        try:
            # Check if this is a Cisco model request
            model = data.get("model", "")
            
            # Check model name or litellm_params for Cisco indicators
            litellm_params = data.get("litellm_params", {})
            api_base = litellm_params.get("api_base", data.get("api_base", ""))
            
            # If this is a Cisco request, inject fresh token
            if "cisco" in model.lower() or "chat-ai.cisco.com" in api_base:
                fresh_token = get_cisco_token()
                app_key = os.getenv("CISCO_APP_KEY")

                # Inject the token into the request
                if "litellm_params" in data:
                    data["litellm_params"]["api_key"] = fresh_token
                else:
                    data["api_key"] = fresh_token

                # Add Cisco-specific headers (Apigee expects oauthtoken)
                extra_headers = data.get("extra_headers", {}) or {}
                extra_headers.update({
                    "oauthtoken": fresh_token,
                    "api-key": fresh_token,
                })
                data["extra_headers"] = extra_headers

                if app_key and not data.get("user"):
                    data["user"] = json.dumps({"appkey": app_key})

                print(f"[CiscoTokenCallback] Injected fresh token for model: {model}")
                
        except Exception as e:
            print(f"[CiscoTokenCallback] Error injecting token: {e}")
            return e
        
        return None

    def pre_call_hook(
        self,
        user_api_key_dict: dict,
        cache: Any,
        data: dict,
        call_type: str,
    ) -> Optional[Exception]:
        """
        Synchronous pre-call hook (fallback for sync operations).
        """
        try:
            model = data.get("model", "")
            litellm_params = data.get("litellm_params", {})
            api_base = litellm_params.get("api_base", data.get("api_base", ""))
            
            if "cisco" in model.lower() or "chat-ai.cisco.com" in api_base:
                fresh_token = get_cisco_token()
                app_key = os.getenv("CISCO_APP_KEY")

                if "litellm_params" in data:
                    data["litellm_params"]["api_key"] = fresh_token
                else:
                    data["api_key"] = fresh_token

                # Add Cisco-specific headers (Apigee expects oauthtoken)
                extra_headers = data.get("extra_headers", {}) or {}
                extra_headers.update({
                    "oauthtoken": fresh_token,
                    "api-key": fresh_token,
                })
                data["extra_headers"] = extra_headers

                if app_key and not data.get("user"):
                    data["user"] = json.dumps({"appkey": app_key})

                print(f"[CiscoTokenCallback] Injected fresh token for model: {model}")
                
        except Exception as e:
            print(f"[CiscoTokenCallback] Error injecting token: {e}")
            return e
        
        return None

    async def async_post_call_streaming_iterator_hook(
        self,
        user_api_key_dict: dict,
        response: Any,
        request_data: dict,
    ):
        """
        Pass through streaming responses without modification.
        Required for streaming support in LiteLLM callbacks.
        """
        async for item in response:
            yield item


# Create callback instance for proxy config import
cisco_handler = CiscoTokenCallback()
print("[CiscoTokenCallback] Initialized cisco_handler for proxy callbacks")
