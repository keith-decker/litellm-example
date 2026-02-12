import os
import openai
import time
import random


def generate_poem_with_cisco():
    """Generate a poem using Cisco LLM via LiteLLM proxy with streaming."""
    # Randomly select between Team A and Team B keys
    team = random.choice(["A", "B"])
    api_key = os.environ.get(f"TEAM_{team}_KEY", f"sk-team-{team.lower()}-key-{'12345' if team == 'A' else '67890'}")
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url=os.getenv("LITELLM_PROXY_URL", "http://localhost:4000/v1")
    )

    messages = [
        {"role": "system", "content": "You are a poetic assistant, skilled in crafting beautiful poems about technical topics."},
        {"role": "user", "content": "Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems."}
    ]

    try:
        start_time = time.time()
        time_to_first_token = None
        full_response = ""
        
        response = client.chat.completions.create(
            model="cisco-llm",
            messages=messages,
            stream=True  # Enable streaming for TTFT measurement
        )
        
        # Process streaming response
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                
                # Measure time to first token
                if time_to_first_token is None:
                    time_to_first_token = time.time() - start_time
                    print(f"\n[Time to First Token: {time_to_first_token:.3f}s]\n")
                
                # Print streaming output
                print(content, end='', flush=True)
        
        total_time = time.time() - start_time
        print(f"\n\n[Total time: {total_time:.3f}s]")
        
        return full_response
    except Exception as e:
        return f"Error generating poem with Cisco: {str(e)}"

def main():
    team = random.choice(["A", "B"])
    team_key = os.environ.get(f"TEAM_{team}_KEY", f"sk-team-{team.lower()}-key-{'12345' if team == 'A' else '67890'}")
    print("=== OpenTelemetry Poetry Generator (via LiteLLM Proxy) ===")
    print(f"Using Team {team} key ({team_key[:20]}...)\n")
    # Uncomment to test Cisco LLM (requires credentials)
    print("Generating poem with Cisco LLM...\n")
    print("=== Poem (Cisco) ===")
    cisco_poem = generate_poem_with_cisco()
    print(cisco_poem)

if __name__ == "__main__":
    main()