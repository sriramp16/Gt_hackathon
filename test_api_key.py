import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import requests

print("="*70)
print("GROK API KEY VALIDATION")
print("="*70)

api_key = config.GROK_API_KEY
print(f"\nGrok API Key Details:")
print(f"  - Length: {len(api_key) if api_key else 0} characters")
print(f"  - Starts with: {api_key[:10] if api_key else 'N/A'}...")
print(f"  - Ends with: ...{api_key[-10:] if api_key else 'N/A'}")
print(f"  - Configured Model: {config.LLM_MODEL}")

if not api_key:
    print("\n✗ No Grok API key configured")
    sys.exit(1)

print("\n[Test 1] Making API call with current key...")
try:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers=headers,
        json={
            "model": "grok-2",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'hello world' in one word."}
            ],
            "max_tokens": 100
        },
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
    
    if response.status_code == 200:
        print("\n✓ API call successful!")
        result = response.json()
        if "choices" in result:
            print(f"✓ Response format valid")
            print(f"  Content: {result['choices'][0]['message']['content']}")
    else:
        print(f"\n✗ API error: {response.status_code}")
        error_msg = response.json() if response.text else response.text
        print(f"  Error details: {error_msg}")

except Exception as e:
    print(f"\n✗ Request failed: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
