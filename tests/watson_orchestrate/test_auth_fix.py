import base64
import requests
import os

# Your current key
encoded_key = "azE6dXNyX2NiODJmNGU0LTZkMDctMzU0OC04ZTdlLTBiOWZiZTQ0MTJmODpRcWJxcHpobzYxLy9nODMvcWl5blRjcGVjRHh5VHFPUU5nY3FlRUNDM2FVPTpSOVJy"

# Try decoding
try:
    decoded = base64.b64decode(encoded_key).decode('utf-8')
    print(f"Decoded key: {decoded}")
    
    # If it's username:password format
    if ':' in decoded:
        username, password = decoded.split(':', 1)
        print(f"Username: {username}")
        print(f"Password: {password[:10]}...")  # Show first 10 chars only
        
        # Test with Basic Auth
        url = "https://cio.watson-orchestrate.ibm.com/api/v1/agents/6d473302-919e-4204-8c44-5302139947d3/message"
        
        response = requests.post(
            url,
            auth=(username, password),
            json={"input": {"text": "test"}},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"Error: {e}")