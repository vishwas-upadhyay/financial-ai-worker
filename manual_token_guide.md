# Manual Access Token Generation Guide

## Method 1: Using the Python Script (Recommended)

Run the token generator script:
```bash
python generate_token.py
```

## Method 2: Manual Steps

### Step 1: Create Login URL
Replace `YOUR_API_KEY` with your actual API key:
```
https://kite.trade/connect/login?api_key=YOUR_API_KEY
```

### Step 2: Login and Get Request Token
1. Open the URL in your browser
2. Login with your Zerodha credentials
3. You'll be redirected to a URL like:
   ```
   http://localhost:8000/zerodha/callback?request_token=XXXXXX&action=login&status=success
   ```
4. Copy the `request_token` value from the URL

### Step 3: Generate Access Token
Use this Python code to generate the access token:

```python
import requests

# Your credentials
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"
request_token = "REQUEST_TOKEN_FROM_STEP_2"

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
```

### Step 4: Update .env File
Add these lines to your `.env` file:
```
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
ZERODHA_ACCESS_TOKEN=your_access_token_here
```

## Method 3: Using Postman or curl

### Using curl:
```bash
curl -X POST "https://api.kite.trade/session/token" \
  -d "api_key=YOUR_API_KEY" \
  -d "request_token=REQUEST_TOKEN" \
  -d "checksum=YOUR_API_SECRET"
```

### Using Postman:
1. Method: POST
2. URL: `https://api.kite.trade/session/token`
3. Body (form-data):
   - `api_key`: Your API key
   - `request_token`: Request token from login
   - `checksum`: Your API secret

## Troubleshooting

### Common Issues:
1. **Invalid API Key**: Make sure you're using the correct API key from Kite Connect
2. **Request Token Expired**: Request tokens expire quickly, generate a new one
3. **Invalid Checksum**: Make sure you're using the API secret as checksum
4. **Network Issues**: Check your internet connection

### Error Messages:
- `"Invalid API key"`: Check your API key
- `"Invalid request token"`: Generate a new request token
- `"Invalid checksum"`: Use your API secret as checksum

## Security Notes:
- Never share your API credentials
- Store them securely in environment variables
- Regenerate tokens if compromised
- Use HTTPS for all API calls

