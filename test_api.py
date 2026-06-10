"""
Test script to verify API works with example file
"""
import requests
import json

# Read example file
with open('example_input.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 60)
print("Testing Slack Question Analyzer API")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing health check...")
try:
    response = requests.get('http://localhost:5000/api/health')
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   [OK] Health check passed")
except Exception as e:
    print(f"   [ERROR] Health check failed: {e}")
    print("\n   Make sure the API server is running!")
    print("   Run: python api_server.py")
    exit(1)

# Test 2: Analyze example file
print("\n2. Testing analysis with example_input.txt...")
print(f"   File size: {len(content)} characters")
print("   Sending to API... (this may take 30-60 seconds)")

try:
    response = requests.post(
        'http://localhost:5000/api/analyze',
        json={'content': content, 'provider': 'ollama', 'threshold': 0.85},
        timeout=180  # 3 minute timeout
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data['success']:
            results = data['data']
            print("\n   [OK] Analysis successful!")
            print(f"   Total questions: {results['total_questions']}")
            print(f"   Total groups: {results['total_groups']}")
            print(f"   Ungrouped: {len(results['ungrouped_questions'])}")
            
            if results['groups']:
                print(f"\n   Top 3 question groups:")
                for i, group in enumerate(results['groups'][:3], 1):
                    print(f"   {i}. {group['representative_question'][:60]}...")
                    print(f"      Count: {group['count']}, Similarity: {group['avg_similarity']:.0%}")
                    print(f"      Keywords: {', '.join(group['keywords'][:5])}")
            
            # Save results for inspection
            with open('test_api_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"\n   Results saved to: test_api_results.json")
            
        else:
            print(f"   [ERROR] Analysis failed: {data.get('error', 'Unknown error')}")
            exit(1)
    else:
        print(f"   [ERROR] API returned error: {response.text}")
        exit(1)
        
except requests.exceptions.Timeout:
    print("   [ERROR] Request timed out (>3 minutes)")
    exit(1)
except Exception as e:
    print(f"   [ERROR] Analysis failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("All tests passed! [OK]")
print("=" * 60)
print("\nThe API is working correctly with real data.")
print("You can now test the React UI by:")
print("1. Opening: Question Analyzer Design System/ui_kits/analyzer/index.html")
print("2. Clicking 'Upload transcript'")
print("3. Selecting example_input.txt")
print("4. Watching the results populate dynamically!")

# Made with Bob
