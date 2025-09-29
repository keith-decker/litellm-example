import os
import litellm

def generate_poem_with_openai(api_key):
    """Generate a poem using OpenAI's GPT-4."""
    try:
        messages = [
            {"role": "system", "content": "You are a poetic assistant, skilled in crafting beautiful poems about technical topics."},
            {"role": "user", "content": "Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems."}
        ]
        response = litellm.completion(
            model="gpt-4.1",
            messages=messages,
            api_key=api_key
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating poem with OpenAI: {str(e)}"

def generate_poem_with_ollama():
    """Generate a poem using a local Ollama model."""
    try:
        messages = [
            {"role": "system", "content": "You are a poetic assistant, skilled in crafting beautiful poems about technical topics."},
            {"role": "user", "content": "Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems."}
        ]
        response = litellm.completion(
            model="ollama/llama3.2:latest",  # or any other model you have with Ollama
            messages=messages,
            api_base="http://localhost:11434"  # Default Ollama API endpoint
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating poem with Ollama: {str(e)}"

def main():
    # Get OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    litellm.callbacks = ["otel"]
    
    print("=== OpenTelemetry Poetry Generator ===\n")
    
    if openai_api_key:
        print("Generating poem with OpenAI GPT-4...\n")
        openai_poem = generate_poem_with_openai(openai_api_key)
        print("=== OpenAI GPT-4 Poem ===")
        print(openai_poem)
        print("\n" + "="*50 + "\n")
    else:
        print("Skipping OpenAI (OPENAI_API_KEY not found in environment variables)\n")
    
    print("Generating poem with local Ollama model...\n")
    ollama_poem = generate_poem_with_ollama()
    print("=== Local Ollama Poem ===")
    print(ollama_poem)

if __name__ == "__main__":
    main()
