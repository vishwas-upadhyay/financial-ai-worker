#!/usr/bin/env python3
"""
Fixed Zerodha Token Generator with proper checksum
"""
import requests
import hashlib
import hmac
import json

def generate_checksum(api_key, request_token, api_secret):
    """Generate proper checksum for Zerodha API"""
    # Create the string to hash
    string_to_hash = f"{api_key}{request_token}{api_secret}"
    
    # Generate SHA256 hash
    checksum = hashlib.sha256(string_to_hash.encode()).hexdigest()
    
    return checksum

def generate_token_with_proper_checksum():
    """Generate access token with proper checksum"""
    
    # Your credentials
    api_key = "3ikfyzsfz1eb2w5p"
    api_secret = "kv1mrgibkb039282kswvisuv6xv4cwyd"
    request_token = "TFWeKRMWkTx4kcPeD5KwHjA6bdQgKyIZ"
    
    print("🔑 Zerodha Token Generator with Proper Checksum")
    print("=" * 60)
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 API Secret: {api_secret[:8]}...")
    print(f"🎫 Request Token: {request_token}")
    
    # Generate proper checksum
    print("\n🔄 Generating checksum...")
    checksum = generate_checksum(api_key, request_token, api_secret)
    print(f"✅ Checksum: {checksum}")
    
    # Generate access token
    print("\n🔄 Generating access token...")
    url = "https://api.kite.trade/session/token"
    data = {
        'api_key': api_key,
        'request_token': request_token,
        'checksum': checksum
    }
    
    try:
        response = requests.post(url, data=data, timeout=30)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"📋 Response: {json.dumps(token_data, indent=2)}")
            
            if token_data.get('status') == 'success':
                access_token = token_data['data']['access_token']
                print(f"\n🎉 SUCCESS!")
                print(f"✅ Access Token: {access_token}")
                
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
                    print("\n🎉 You can now run the Financial AI Worker!")
                    
                except Exception as e:
                    print(f"❌ Error saving to .env: {e}")
                    print(f"Please manually add this to your .env file:")
                    print(f"ZERODHA_ACCESS_TOKEN={access_token}")
                
                return access_token
            else:
                error_msg = token_data.get('message', 'Unknown error')
                print(f"❌ API Error: {error_msg}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    generate_token_with_proper_checksum()

