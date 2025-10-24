# Trading212 Integration Setup Guide

This guide will help you set up Trading212 API integration to view your portfolio in the Financial AI Worker application.

## Prerequisites

- Active Trading212 account (https://www.trading212.com/)
- Access to Trading212 web platform
- Python 3.8+ installed
- Financial AI Worker project set up

## Step 1: Generate Trading212 API Key

1. **Login to Trading212**
   - Go to https://www.trading212.com/
   - Login with your credentials

2. **Navigate to API Settings**
   - Click on your profile/account icon
   - Go to **Settings**
   - Look for **API (Beta)** section

3. **Generate API Key**
   - Click on **Generate API Key**
   - You will receive an API Key (this is shown only once!)
   - **IMPORTANT**: Copy and save this key securely
   - Never share your API key with anyone

4. **Optional: Set IP Restrictions**
   - For added security, you can restrict API access to specific IP addresses
   - This is recommended if you have a static IP address

## Step 2: Configure Your Application

1. **Update .env File**

   Open your `.env` file and update the Trading212 API key:

   ```bash
   TRADING212_API_KEY=your_actual_api_key_here
   ```

   Replace `your_actual_api_key_here` with the API key you generated in Step 1.

2. **Save the File**

   Make sure to save the `.env` file after making changes.

## Step 3: Test the Integration

Run the test script to verify your setup:

```bash
python test_trading212.py
```

This script will:
- Verify your API key is configured
- Test connection to Trading212 API
- Fetch and display your account information
- Show your current portfolio positions
- Display total portfolio value and P&L

### Expected Output

If everything is configured correctly, you should see:

```
============================================================
Trading212 API Connection Test
============================================================

✓ API Key configured: abcd1234...

1. Initializing Trading212 client...
   ✓ Client initialized successfully

2. Fetching account information...
   ✓ Account ID: 123456
   ✓ Currency: USD

3. Fetching cash balance...
   ✓ Free Cash: 1000.00
   ✓ Invested: 5000.00
   ✓ Total: 6000.00
   ✓ P&L: 500.00

4. Fetching portfolio positions...
   ✓ Found 5 position(s)

--------------------------------------------------------------------------------
Ticker          Qty        Avg Price    Current      P&L
--------------------------------------------------------------------------------
AAPL_US_EQ      10.00      $150.00      $155.00      $50.00
...
--------------------------------------------------------------------------------

✅ SUCCESS: Trading212 integration is working correctly!
```

## Step 4: Start the Application

Once the test is successful, start the main application:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 5: Access Your Portfolio

### Option 1: Web Dashboard
Open your browser and navigate to:
```
http://localhost:8000/
```

### Option 2: Direct API Endpoint
Access the Trading212 portfolio API endpoint:
```
http://localhost:8000/portfolio/trading212
```

### Option 3: Combined Portfolio (Zerodha + Trading212)
View your combined portfolio from all brokers:
```
http://localhost:8000/portfolio/combined
```

## API Endpoints

### Portfolio Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio/trading212` | GET | Get Trading212 portfolio |
| `/portfolio/zerodha` | GET | Get Zerodha portfolio |
| `/portfolio/combined` | GET | Get combined portfolio |
| `/analyze/trading212` | GET | Analyze Trading212 portfolio |
| `/analyze/combined` | GET | Analyze combined portfolio |

### Account Endpoints

All API documentation is available at:
```
http://localhost:8000/docs
```

## Troubleshooting

### Error: "Trading212 API key is not configured"

**Solution**: Make sure you've updated the `.env` file with your actual API key.

### Error: "401 Unauthorized"

**Possible Causes**:
- Invalid API key
- API key has been revoked
- Incorrect API key format

**Solution**:
- Double-check your API key in the `.env` file
- Generate a new API key from Trading212
- Make sure there are no extra spaces or characters

### Error: "403 Forbidden"

**Possible Causes**:
- IP restriction is enabled and your IP is not whitelisted
- API key doesn't have required permissions

**Solution**:
- Check IP restrictions in Trading212 settings
- Add your current IP to the whitelist
- Regenerate API key with proper permissions

### Error: "Empty portfolio" or "No positions found"

**Possible Causes**:
- You don't have any open positions
- Using demo account instead of live account

**Solution**:
- Verify you have open positions in your Trading212 account
- If testing, you can use demo mode by modifying the client initialization

### Network/Connection Errors

**Solution**:
- Check your internet connection
- Verify Trading212 API is operational: https://status.trading212.com/
- Check firewall settings

## API Rate Limits

Trading212 API has rate limits on different endpoints:

| Endpoint | Rate Limit |
|----------|------------|
| Account Info | 1 request per 30 seconds |
| Cash Balance | 1 request per 2 seconds |
| Portfolio | 1 request per 5 seconds |
| Orders | 1 request per 5 seconds |
| Place Order | 1 request per 5 seconds |

**Note**: The application automatically handles these rate limits, but be aware when making manual API calls.

## Security Best Practices

1. **Never commit your .env file** - It's already in `.gitignore`
2. **Use environment-specific keys** - Different keys for development/production
3. **Enable IP restrictions** - Limit API access to trusted IPs
4. **Rotate keys regularly** - Generate new API keys periodically
5. **Monitor API usage** - Check for unauthorized access in Trading212 settings
6. **Use HTTPS in production** - Never transmit API keys over HTTP

## Demo Mode (Paper Trading)

To use Trading212's demo/paper trading environment for testing:

```python
# Modify client initialization in your code:
async with Trading212Client(use_demo=True) as client:
    # Your code here
```

Demo mode uses a different base URL: `https://demo.trading212.com/api/v0`

## Support

For issues with:
- **Trading212 API**: Contact Trading212 support
- **This application**: Open an issue on the GitHub repository
- **API Documentation**: https://t212public-api-docs.redoc.ly/

## Additional Resources

- Trading212 Website: https://www.trading212.com/
- Trading212 API Docs: https://t212public-api-docs.redoc.ly/
- Trading212 Help Center: https://helpcentre.trading212.com/
- Project GitHub: https://github.com/vishwas-upadhyay/financial-ai-worker

## What's Next?

Now that your Trading212 integration is working, you can:

1. ✅ View your real-time portfolio
2. ✅ Track performance and P&L
3. ✅ Combine with Zerodha portfolio for full picture
4. ✅ Get AI-powered portfolio analysis
5. ✅ Monitor risk metrics and diversification
6. ✅ Receive automated recommendations

Happy trading! 📈
