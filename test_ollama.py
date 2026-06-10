"""
Test script to verify Ollama is working correctly
"""

import requests
import json

def test_ollama():
    """Test Ollama connection and embeddings"""
    
    print("Testing Ollama connection...")
    print("-" * 50)
    
    # Test 1: Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        print("✓ Ollama is running")
        print(f"  Available models: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"✗ Ollama is not running or not accessible")
        print(f"  Error: {e}")
        print("\nPlease start Ollama:")
        print("  1. Open a new PowerShell window")
        print("  2. Run: ollama serve")
        return False
    
    print()
    
    # Test 2: Check if nomic-embed-text model is available
    try:
        models = response.json().get('models', [])
        model_names = [m['name'] for m in models]
        
        if 'nomic-embed-text:latest' in model_names or 'nomic-embed-text' in str(model_names):
            print("✓ nomic-embed-text model is available")
        else:
            print("✗ nomic-embed-text model not found")
            print(f"  Available models: {model_names}")
            print("\nPlease pull the model:")
            print("  ollama pull nomic-embed-text")
            return False
    except Exception as e:
        print(f"✗ Error checking models: {e}")
        return False
    
    print()
    
    # Test 3: Try to get an embedding
    try:
        print("Testing embeddings API...")
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": "Hello, world!"
            }
        )
        response.raise_for_status()
        embedding = response.json()['embedding']
        print(f"✓ Embeddings API working")
        print(f"  Embedding dimension: {len(embedding)}")
    except Exception as e:
        print(f"✗ Embeddings API failed")
        print(f"  Error: {e}")
        print(f"  Response: {response.text if 'response' in locals() else 'No response'}")
        return False
    
    print()
    print("=" * 50)
    print("✓ All tests passed! Ollama is ready to use.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_ollama()

# Made with Bob
