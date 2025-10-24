#!/usr/bin/env python3
"""
Zerodha Access Token Generator
This script helps you generate an access token for Zerodha API
"""
import webbrowser
import urllib.parse
from urllib.parse import urlparse, parse_qs
import requests
import json
import hashlib
from config.settings import settings

def generate_access_token():
    """Generate access token for Zerodha API"""
    
    print("🔑 Zerodha Access Token Generator")
    print("=" * 50)
    
    # Get API credentials from user
    api_key = input("Enter your Zerodha API Key: ").strip()
    api_secret = input("Enter your Zerodha API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("❌ API Key and Secret are required!")
        return
    
    # Step 1: Generate login URL
    login_url = f"https://kite.trade/connect/login?api_key={api_key}"
    
    print(f"\n📋 Step 1: Login to Zerodha")
    print(f"Login URL: {login_url}")
    print("\n🌐 Opening browser for Zerodha login...")
    
    # Open browser for login
    webbrowser.open(login_url)
    
    print("\n📝 After logging in, you'll be redirected to a URL that looks like:")
    print("http://localhost:8000/zerodha/callback?request_token=XXXXXX&action=login&status=success")
    
    # Step 2: Get request token from user
    print("\n" + "="*50)
    print("📋 Step 2: Get Request Token")
    redirect_url = input("\nPaste the full redirect URL here: ").strip()
    
    if not redirect_url:
        print("❌ Redirect URL is required!")
        return
    
    # Parse request token from URL
    try:
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        
        if 'request_token' not in query_params:
            print("❌ Request token not found in URL!")
            return
            
        request_token = query_params['request_token'][0]
        print(f"✅ Request token extracted: {request_token}")
        
    except Exception as e:
        print(f"❌ Error parsing URL: {e}")
        return
    
    # Step 3: Generate access token
    print("\n" + "="*50)
    print("📋 Step 3: Generate Access Token")

    try:
        # Generate proper checksum using SHA256
        checksum_string = api_key + request_token + api_secret
        checksum = hashlib.sha256(checksum_string.encode()).hexdigest()

        print(f"🔐 Generated checksum for authentication")

        # Make request to generate access token
        url = "https://api.kite.trade/session/token"
        data = {
            'api_key': api_key,
            'request_token': request_token,
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
                
                # Save to .env file
                update_env_file(api_key, api_secret, access_token)
                
            else:
                print(f"❌ Error generating token: {token_data.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error generating access token: {e}")

def update_env_file(api_key, api_secret, access_token):
    """Update .env file with credentials"""
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update or add credentials
        updated_lines = []
        api_key_found = False
        api_secret_found = False
        access_token_found = False
        
        for line in lines:
            if line.startswith('ZERODHA_API_KEY='):
                updated_lines.append(f'ZERODHA_API_KEY={api_key}\n')
                api_key_found = True
            elif line.startswith('ZERODHA_API_SECRET='):
                updated_lines.append(f'ZERODHA_API_SECRET={api_secret}\n')
                api_secret_found = True
            elif line.startswith('ZERODHA_ACCESS_TOKEN='):
                updated_lines.append(f'ZERODHA_ACCESS_TOKEN={access_token}\n')
                access_token_found = True
            else:
                updated_lines.append(line)
        
        # Add missing credentials
        if not api_key_found:
            updated_lines.append(f'ZERODHA_API_KEY={api_key}\n')
        if not api_secret_found:
            updated_lines.append(f'ZERODHA_API_SECRET={api_secret}\n')
        if not access_token_found:
            updated_lines.append(f'ZERODHA_ACCESS_TOKEN={access_token}\n')
        
        # Write updated .env file
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        print(f"\n✅ Credentials saved to .env file!")
        print("🎉 You can now run the Financial AI Worker application!")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        print(f"Please manually add these to your .env file:")
        print(f"ZERODHA_API_KEY={api_key}")
        print(f"ZERODHA_API_SECRET={api_secret}")
        print(f"ZERODHA_ACCESS_TOKEN={access_token}")

def test_connection():
    """Test the API connection"""
    print("\n" + "="*50)
    print("🧪 Testing API Connection")
    
    try:
        from src.brokers.zerodha_client import ZerodhaClient
        import asyncio
        
        async def test():
            async with ZerodhaClient() as client:
                profile = await client.get_profile()
                print("✅ API connection successful!")
                print(f"User: {profile.get('data', {}).get('user_name', 'Unknown')}")
                return True
        
        result = asyncio.run(test())
        return result
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Financial AI Worker - Token Generator")
    print("This script will help you generate a Zerodha access token")
    print("\n⚠️  Make sure you have:")
    print("   1. Zerodha trading account")
    print("   2. API Key and Secret from Kite Connect")
    print("   3. Internet connection")
    
    proceed = input("\nDo you want to continue? (y/n): ").lower().strip()
    
    if proceed == 'y':
        generate_access_token()
        
        # Ask if user wants to test connection
        test = input("\nDo you want to test the API connection? (y/n): ").lower().strip()
        if test == 'y':
            test_connection()
    else:
        print("👋 Goodbye!")

