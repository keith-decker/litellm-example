import os
import openai


def generate_poem_with_cisco():
    """Generate a poem using Cisco LLM via LiteLLM proxy."""
    # Use LITELLM_PROXY_KEY to match what the docker container uses
    api_key = os.environ.get("LITELLM_PROXY_KEY", "sk-1234")
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url=os.getenv("LITELLM_PROXY_URL", "http://localhost:4000/v1")
    )

    messages = [
        {"role": "system", "content": "You are a poetic assistant, skilled in crafting beautiful poems about technical topics."},
        {"role": "user", "content": "Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems."}
    ]

    try:
        response = client.chat.completions.create(
            model="cisco-llm",
            messages=messages,
            stream=False  # Test without streaming first
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating poem with Cisco: {str(e)}"

def main():
    master_key = os.environ.get("LITELLM_PROXY_KEY", "sk-1234")
    print("=== OpenTelemetry Poetry Generator (via LiteLLM Proxy) ===")
    print(f"Using master key ({master_key[:10]}...)\n")
    # Uncomment to test Cisco LLM (requires credentials)
    print("Generating poem with Cisco LLM...\n")
    print("=== Poem (Cisco) ===")
    cisco_poem = generate_poem_with_cisco()
    print(cisco_poem)

if __name__ == "__main__":
    main()