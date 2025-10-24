#!/usr/bin/env python3
"""
Simple script to generate Zerodha access token
"""
import requests
import hashlib

# Replace these with your actual credentials
API_KEY = "YOUR_API_KEY_HERE"
API_SECRET = "YOUR_API_SECRET_HERE"
REQUEST_TOKEN = "YOUR_REQUEST_TOKEN_HERE"

def generate_token():
    # Generate proper checksum using SHA256
    checksum_string = API_KEY + REQUEST_TOKEN + API_SECRET
    checksum = hashlib.sha256(checksum_string.encode()).hexdigest()

    url = "https://api.kite.trade/session/token"
    data = {
        'api_key': API_KEY,
        'request_token': REQUEST_TOKEN,
        'checksum': checksum
    }
    
    print("🔄 Generating access token...")
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        if token_data.get('status') == 'success':
            access_token = token_data['data']['access_token']
            print(f"✅ Access token generated successfully!")
            print(f"Access Token: {access_token}")
            return access_token
        else:
            print(f"❌ Error: {token_data.get('message', 'Unknown error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
    
    return None

if __name__ == "__main__":
    print("🔑 Zerodha Access Token Generator")
    print("=" * 40)
    print("1. Update the credentials in this script")
    print("2. Run: python3 simple_token.py")
    print("3. Copy the access token to your .env file")
    print("\n⚠️  Make sure to replace the placeholder values!")
    
    # Uncomment the line below after updating credentials
    # generate_token()

