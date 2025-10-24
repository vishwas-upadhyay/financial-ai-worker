#!/usr/bin/env python3
"""
Diagnostic script to check Zerodha API status
"""
import requests
import json

def diagnose_zerodha_api():
    print("🔍 Zerodha API Diagnostic Tool")
    print("=" * 50)
    
    api_key = "3ikfyzsfz1eb2w5p"
    api_secret = "kv1mrgibkb039282kswvisuv6xv4cwyd"
    request_token = "TFWeKRMWkTx4kcPeD5KwHjA6bdQgKyIZ"
    
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 API Secret: {api_secret[:8]}...")
    print(f"🎫 Request Token: {request_token}")
    
    # Test 1: Check if API key can access basic endpoints
    print("\n📋 Test 1: Basic API Access")
    try:
        url = "https://api.kite.trade/instruments"
        headers = {'X-Kite-Version': '3'}
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ Instruments API Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ API key is valid and active")
        else:
            print(f"❌ API key issue: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Error accessing instruments API: {e}")
    
    # Test 2: Try token generation with detailed error info
    print("\n📋 Test 2: Token Generation")
    try:
        url = "https://api.kite.trade/session/token"
        data = {
            'api_key': api_key,
            'request_token': request_token,
            'checksum': api_secret
        }
        
        print("🔄 Attempting token generation...")
        response = requests.post(url, data=data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Success! Response: {json.dumps(token_data, indent=2)}")
        else:
            print(f"❌ Error Response: {response.text}")
            
            # Try to parse error response
            try:
                error_data = response.json()
                print(f"📋 Parsed Error: {json.dumps(error_data, indent=2)}")
            except:
                print("📋 Raw Error Response (not JSON)")
                
    except Exception as e:
        print(f"❌ Exception during token generation: {e}")
    
    # Test 3: Check if request token format is correct
    print("\n📋 Test 3: Request Token Analysis")
    print(f"Token Length: {len(request_token)}")
    print(f"Token Format: {request_token[:10]}...{request_token[-10:]}")
    print(f"Contains only alphanumeric: {request_token.isalnum()}")
    
    # Test 4: Try alternative checksum methods
    print("\n📋 Test 4: Alternative Checksum Methods")
    
    # Method 1: Use API secret as checksum (current method)
    print("🔄 Method 1: API Secret as Checksum")
    try:
        data1 = {
            'api_key': api_key,
            'request_token': request_token,
            'checksum': api_secret
        }
        response1 = requests.post(url, data=data1, timeout=10)
        print(f"Status: {response1.status_code}")
        if response1.status_code != 200:
            print(f"Error: {response1.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 2: Try without checksum
    print("\n🔄 Method 2: Without Checksum")
    try:
        data2 = {
            'api_key': api_key,
            'request_token': request_token
        }
        response2 = requests.post(url, data=data2, timeout=10)
        print(f"Status: {response2.status_code}")
        if response2.status_code != 200:
            print(f"Error: {response2.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Diagnostic Complete")
    print("\n💡 Common Issues:")
    print("1. Request token expired (get a fresh one)")
    print("2. API key not activated in Kite Connect")
    print("3. Wrong redirect URL in app settings")
    print("4. Account not linked to API key")

if __name__ == "__main__":
    diagnose_zerodha_api()

