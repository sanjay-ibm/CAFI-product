#!/usr/bin/env python3
"""
Watson Orchestrate Authentication Diagnostic Tool

This script helps diagnose and fix authentication issues with Watson Orchestrate API.
"""

import base64
import os
import sys
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and not os.getenv(key):
                    os.environ[key] = value


def analyze_api_key():
    """Analyze the current API key format."""
    api_key = os.getenv("WATSON_ORCHESTRATE_API_KEY")
    
    if not api_key:
        print("❌ WATSON_ORCHESTRATE_API_KEY not found in environment")
        print("\nPlease set it in your .env file:")
        print("WATSON_ORCHESTRATE_API_KEY=your_api_key_here")
        return False
    
    print("🔍 Analyzing API Key...")
    print(f"Key length: {len(api_key)} characters")
    print(f"First 20 chars: {api_key[:20]}...")
    print(f"Last 10 chars: ...{api_key[-10:]}")
    
    # Check if it's base64 encoded
    try:
        decoded = base64.b64decode(api_key).decode('utf-8')
        print("\n✅ Key appears to be base64-encoded")
        print(f"Decoded format: {decoded[:50]}...")
        
        if ':' in decoded:
            parts = decoded.split(':')
            print(f"\n📋 Decoded key has {len(parts)} parts separated by ':'")
            print("This might be in format: k1:user_id:token:suffix")
            
            # Suggest authentication method
            print("\n💡 Suggested Authentication Methods:")
            print("1. Basic Authentication with username:password")
            print("2. Bearer token authentication")
            print("3. Custom header authentication")
            
    except Exception as e:
        print(f"\n⚠️  Key doesn't appear to be base64-encoded: {e}")
        print("This might be a plain API key or token")
    
    return True


def test_authentication_methods():
    """Test different authentication methods."""
    import requests
    
    api_key = os.getenv("WATSON_ORCHESTRATE_API_KEY")
    agent_id = os.getenv("WATSON_AGENT_ID", "6d473302-919e-4204-8c44-5302139947d3")
    base_url = os.getenv("WATSON_ORCHESTRATE_BASE_URL", "https://cio.watson-orchestrate.ibm.com/api/v1")
    
    url = f"{base_url}/agents/{agent_id}/message"
    test_payload = {"input": {"text": "Hello"}}
    
    print("\n🧪 Testing Authentication Methods...")
    print(f"URL: {url}")
    
    # Method 1: Authorization header with raw key
    print("\n1️⃣ Testing: Authorization header with raw key")
    try:
        response = requests.post(
            url,
            json=test_payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCCESS! Use this method.")
            return "bearer"
        else:
            print(f"   ❌ Failed: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 2: Try decoding and using Basic Auth
    print("\n2️⃣ Testing: Basic Authentication (if base64 encoded)")
    try:
        if not api_key:
            raise ValueError("API key is None")
        decoded = base64.b64decode(api_key).decode('utf-8')
        if ':' in decoded:
            parts = decoded.split(':', 1)
            username = parts[0]
            password = parts[1] if len(parts) > 1 else ""
            
            response = requests.post(
                url,
                json=test_payload,
                auth=(username, password),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ SUCCESS! Use Basic Auth with decoded credentials.")
                return "basic"
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 3: API Key in header
    print("\n3️⃣ Testing: X-API-Key header")
    try:
        response = requests.post(
            url,
            json=test_payload,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            },
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCCESS! Use X-API-Key header.")
            return "x-api-key"
        else:
            print(f"   ❌ Failed: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 4: Authorization with "apikey" prefix
    print("\n4️⃣ Testing: Authorization with 'apikey' prefix")
    try:
        response = requests.post(
            url,
            json=test_payload,
            headers={
                "Authorization": f"apikey {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCCESS! Use 'apikey' prefix.")
            return "apikey"
        else:
            print(f"   ❌ Failed: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return None


def provide_recommendations():
    """Provide recommendations for fixing the issue."""
    print("\n" + "="*70)
    print("📋 RECOMMENDATIONS")
    print("="*70)
    
    print("\n1. Get a New API Key:")
    print("   - Visit: https://cio.watson-orchestrate.ibm.com")
    print("   - Go to Settings → API Keys")
    print("   - Generate a new API key")
    print("   - Update your .env file")
    
    print("\n2. Try IBM Cloud IAM API Key:")
    print("   - Visit: https://cloud.ibm.com")
    print("   - Go to Manage → Access (IAM) → API keys")
    print("   - Create a new API key")
    print("   - Update your .env file")
    
    print("\n3. Check Watson Orchestrate Documentation:")
    print("   - Look for API authentication guide")
    print("   - Verify the correct authentication method")
    print("   - Check if additional permissions are needed")
    
    print("\n4. Verify Agent Access:")
    print("   - Visit: https://cio.watson-orchestrate.ibm.com/build/agent/edit/6d473302-919e-4204-8c44-5302139947d3")
    print("   - Make sure you can access the agent")
    print("   - Check if API access is enabled")
    
    print("\n5. Contact IBM Support:")
    print("   - IBM Support Portal: https://www.ibm.com/mysupport")
    print("   - Provide the 401 error details")
    print("   - Ask for correct API authentication method")


def main():
    """Main diagnostic function."""
    print("="*70)
    print("Watson Orchestrate Authentication Diagnostic Tool")
    print("="*70)
    
    # Step 1: Analyze API key
    if not analyze_api_key():
        sys.exit(1)
    
    # Step 2: Test authentication methods
    result = test_authentication_methods()
    
    if result:
        print(f"\n✅ Found working authentication method: {result}")
        print("\nUpdate your test_watson_orchestrate.py to use this method.")
    else:
        print("\n❌ None of the authentication methods worked.")
        provide_recommendations()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
