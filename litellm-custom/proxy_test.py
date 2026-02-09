import os
import random
import openai

# Team API keys from environment variables
TEAM_KEYS = {
    "team-a": os.getenv("LITELLM_TEAM_A_KEY", "sk-default-team-a"),
    "team-b": os.getenv("LITELLM_TEAM_B_KEY", "sk-default-team-b"),
}

def get_random_team_key():
    """Get a random team API key for load distribution."""
    team = random.choice(list(TEAM_KEYS.keys()))
    key = TEAM_KEYS[team]
    return team, key

def generate_poem_with_litellm_proxy():
    """Generate a poem using OpenAI via LiteLLM proxy."""
    # Set OpenAI API key (can be any string, LiteLLM will handle auth)
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY", "sk-1234"),
        base_url=os.getenv("LITELLM_PROXY_URL", "http://localhost:4000/v1")
    )

    messages = [
        {"role": "system", "content": "You are a poetic assistant, skilled in crafting beautiful poems about technical topics."},
        {"role": "user", "content": "Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems."}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            stream=True
        )
        poem = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                poem += chunk.choices[0].delta.content
        return poem
    except Exception as e:
        return f"Error generating poem via LiteLLM proxy: {str(e)}"

def generate_poem_with_deepseek():
    """Generate a poem using DeepSeek-R1 via LiteLLM proxy."""
    team, api_key = get_random_team_key()
    api_key = "sk-1234"
    
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
            model="deepseek-r1",
            messages=messages,
            stream=True
        )
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
        
        # Strip out reasoning tokens (everything between <think> and </think>)
        import re
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        return content.strip()
    except Exception as e:
        return f"Error generating poem with DeepSeek-R1: {str(e)}"

def generate_poem_with_ollama():
    """Generate a poem using Ollama via LiteLLM proxy."""
    team, api_key = get_random_team_key()
    api_key = "sk-1234"
    
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
            model="ollama/llama3.2:latest",
            messages=messages,
            stream=True
        )
        poem = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                poem += chunk.choices[0].delta.content
        return poem
    except Exception as e:
        return f"Error generating poem with Ollama: {str(e)}"

def generate_poem_with_cisco():
    """Generate a poem using Cisco LLM via LiteLLM proxy."""
    api_key = "sk-1234"
    
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
    team, api_key = get_random_team_key()
    print("=== OpenTelemetry Poetry Generator (via LiteLLM Proxy) ===")
    print(f"Using {team} ({api_key[:10]}...)\n")
    # print("=== Poem (GPT-4) ===")
    # poem = generate_poem_with_litellm_proxy()
    # print(poem)
    # print("\n" + "="*50 + "\n")
    
    # print("Generating poem with DeepSeek-R1...\n")
    # print("=== Poem (DeepSeek-R1) ===")
    # deepseek_poem = generate_poem_with_deepseek()
    # print(deepseek_poem)
    # print("\n" + "="*50 + "\n")
    
    # print("Generating poem with Ollama...\n")
    # print("=== Poem (Ollama) ===")
    # ollama_poem = generate_poem_with_ollama()
    # print(ollama_poem)
    # print("\n" + "="*50 + "\n")
    
    # Uncomment to test Cisco LLM (requires credentials)
    print("Generating poem with Cisco LLM...\n")
    print("=== Poem (Cisco) ===")
    cisco_poem = generate_poem_with_cisco()
    print(cisco_poem)

if __name__ == "__main__":
    main()