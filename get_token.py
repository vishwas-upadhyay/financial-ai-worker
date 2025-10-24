import requests

# Your credentials
api_key = "3ikfyzsfz1eb2w5p"
api_secret = "kv1mrgibkb039282kswvisuv6xv4cwyd"
request_token = "TFWeKRMWkTx4kcPeD5KwHjA6bdQgKyIZ"

# Generate access token
url = "https://api.kite.trade/session/token"
data = {
    'api_key': api_key,
    'request_token': request_token,
    'checksum': api_secret
}

response = requests.post(url, data=data)
if response.status_code == 200:
    token_data = response.json()
    if token_data.get('status') == 'success':
        access_token = token_data['data']['access_token']
        print(f"Access Token: {access_token}")
    else:
        print(f"Error: {token_data.get('message')}")
else:
    print(f"HTTP Error: {response.status_code}")
