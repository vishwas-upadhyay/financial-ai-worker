#!/usr/bin/env python3
"""
Robust Zerodha Token Generator with better error handling
"""
import requests
import json
import time

def generate_token_with_retry(api_key, api_secret, request_token, max_retries=3):
    """Generate access token with retry logic"""
    
    url = "https://api.kite.trade/session/token"
    
    for attempt in range(max_retries):
        print(f"🔄 Attempt {attempt + 1}/{max_retries}")
        
        data = {
            'api_key': api_key,
            'request_token': request_token,
            'checksum': api_secret
        }
        
        try:
            response = requests.post(url, data=data, timeout=30)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"📋 Response: {json.dumps(token_data, indent=2)}")
                
                if token_data.get('status') == 'success':
                    access_token = token_data['data']['access_token']
                    print(f"✅ SUCCESS! Access Token: {access_token}")
                    return access_token
                else:
                    error_msg = token_data.get('message', 'Unknown error')
                    print(f"❌ API Error: {error_msg}")
                    
                    if 'Invalid request token' in error_msg:
                        print("🔄 Request token expired. Please get a fresh one.")
                        return None
                    elif 'Invalid API key' in error_msg:
                        print("❌ Invalid API key. Please check your credentials.")
                        return None
                    else:
                        print(f"❌ Other error: {error_msg}")
                        return None
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 403:
                    print("🔍 403 Forbidden - Possible causes:")
                    print("   - Request token expired")
                    print("   - Invalid API credentials")
                    print("   - API key not activated")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timeout. Retrying...")
        except requests.exceptions.ConnectionError:
            print("🌐 Connection error. Retrying...")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        if attempt < max_retries - 1:
            print("⏳ Waiting 2 seconds before retry...")
            time.sleep(2)
    
    print("❌ All attempts failed!")
    return None

def main():
    print("🔑 Zerodha Access Token Generator (Robust Version)")
    print("=" * 60)
    
    # Your credentials
    api_key = "3ikfyzsfz1eb2w5p"
    api_secret = "kv1mrgibkb039282kswvisuv6xv4cwyd"
    
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 API Secret: {api_secret[:8]}...")
    
    # Get request token from user
    print("\n📋 Step 1: Get Request Token")
    print("1. Go to: https://kite.trade/connect/login?api_key=3ikfyzsfz1eb2w5p")
    print("2. Login with your Zerodha credentials")
    print("3. Copy the request_token from the redirect URL")
    
    request_token = input("\nEnter your request token: ").strip()
    
    if not request_token:
        print("❌ Request token is required!")
        return
    
    print(f"🎫 Request Token: {request_token}")
    
    # Generate access token
    print("\n📋 Step 2: Generate Access Token")
    access_token = generate_token_with_retry(api_key, api_secret, request_token)
    
    if access_token:
        print(f"\n🎉 SUCCESS!")
        print(f"Access Token: {access_token}")
        
        # Save to .env file
        print("\n💾 Saving to .env file...")
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            # Update or add the access token
            lines = content.split('\n')
            updated = False
            
            for i, line in enumerate(lines):
                if line.startswith('ZERODHA_ACCESS_TOKEN='):
                    lines[i] = f'ZERODHA_ACCESS_TOKEN={access_token}'
                    updated = True
                    break
            
            if not updated:
                lines.append(f'ZERODHA_ACCESS_TOKEN={access_token}')
            
            with open('.env', 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ Access token saved to .env file!")
            
        except Exception as e:
            print(f"❌ Error saving to .env: {e}")
            print(f"Please manually add this to your .env file:")
            print(f"ZERODHA_ACCESS_TOKEN={access_token}")
    else:
        print("\n❌ Failed to generate access token!")
        print("Please try again with a fresh request token.")

if __name__ == "__main__":
    main()

