# AI-Powered Portfolio Management System - User Guide

## Overview
Your Financial AI Worker now has intelligent stock analysis and recommendation capabilities powered by AI (Claude/GPT-4), technical indicators, and sentiment analysis.

## Features Implemented

### 1. **Market Data Analysis**
- Real-time and historical price data
- Support for Indian (NSE, BSE) and US markets (NYSE, NASDAQ)
- Market indices tracking (NIFTY50, SENSEX, S&P500, NASDAQ, DOW)
- News sentiment analysis

### 2. **Technical Analysis**
- **RSI** (Relative Strength Index) - Identifies overbought/oversold conditions
- **MACD** (Moving Average Convergence Divergence) - Trend following indicator
- **Bollinger Bands** - Volatility and price level indicator
- **Moving Averages** (SMA 50, SMA 200, EMA 20) - Trend identification
- **ATR** (Average True Range) - Volatility measurement
- **Stochastic Oscillator** - Momentum indicator

### 3. **AI-Powered Recommendations**
- Combines technical + sentiment + AI analysis
- Provides BUY, SELL, or HOLD recommendations
- Confidence scores (0-100%)
- Target price and stop-loss suggestions
- Risk assessment and key points

## API Endpoints

### Get Market Overview
```bash
GET http://localhost:8000/ai/market-analysis
```
Returns overall market sentiment, trend, and volatility index.

### Analyze a Stock
```bash
POST http://localhost:8000/ai/analyze
Content-Type: application/json

{
  "symbol": "AAPL",
  "exchange": "US",  # or "NSE" for Indian stocks
  "include_portfolio_context": false
}
```

**Response:**
```json
{
  "id": "AAPL_1234567890",
  "symbol": "AAPL",
  "action": "buy",  # or "sell", "hold", "strong_buy", "strong_sell"
  "confidence": 75.5,
  "current_price": 185.50,
  "target_price": 205.00,
  "stop_loss": 175.00,
  "time_horizon": "medium",  # short, medium, or long
  "reasoning": "Strong technical indicators with positive sentiment...",
  "technical_score": 0.65,
  "sentiment_score": 0.45,
  "ai_score": 0.70,
  "key_points": [
    "RSI showing oversold conditions",
    "MACD bullish crossover detected",
    "Positive earnings sentiment"
  ],
  "risks": [
    "Market volatility",
    "Sector headwinds"
  ],
  "opportunities": [
    "Strong growth potential",
    "Undervalued relative to peers"
  ],
  "created_at": "2025-10-25T10:30:00"
}
```

### Get Technical Indicators
```bash
GET http://localhost:8000/ai/technical-indicators/AAPL?exchange=US
```

Returns all calculated technical indicators with buy/sell signals.

### Get All Recommendations
```bash
GET http://localhost:8000/ai/recommendations?limit=10&action=buy
```

### Get Portfolio Suggestions
```bash
GET http://localhost:8000/ai/portfolio-suggestions
```

Analyzes your current holdings and provides AI recommendations for each.

### Approve/Reject Recommendation
```bash
POST http://localhost:8000/ai/recommendations/{rec_id}/approve
Content-Type: application/json

{
  "approved": true,
  "quantity": 10,
  "notes": "Approved for execution"
}
```
*Note: Actual trade execution will be implemented in Phase 3*

### AI Configuration
```bash
# Get current config
GET http://localhost:8000/ai/config

# Update config
PUT http://localhost:8000/ai/config
Content-Type: application/json

{
  "enabled": true,
  "risk_tolerance": "moderate",  # conservative, moderate, aggressive
  "automation_level": "manual",  # manual, semi_auto, full_auto
  "min_confidence_threshold": 65.0,
  "use_llm": true,
  "llm_provider": "anthropic"  # or "openai"
}
```

## How It Works

### Analysis Flow:
1. **Data Collection**
   - Fetches 6 months of historical price data
   - Gets current market information
   - Retrieves recent news articles

2. **Technical Analysis**
   - Calculates 13+ technical indicators
   - Generates buy/sell signals for each indicator
   - Assigns confidence scores

3. **Sentiment Analysis**
   - Analyzes news headlines
   - Categorizes sentiment (very positive to very negative)
   - Calculates sentiment score

4. **AI Analysis** (if API key provided)
   - Sends all data to Claude/GPT-4
   - AI provides comprehensive analysis
   - Generates target price and stop-loss levels

5. **Recommendation Generation**
   - Combines all analyses with weighted scores:
     - Technical: 40%
     - Sentiment: 20%
     - AI: 40%
   - Generates final recommendation
   - Calculates overall confidence

### Recommendation Types:
- **STRONG_BUY**: Combined score ≥ 0.6 (Very bullish)
- **BUY**: Combined score ≥ 0.2 (Bullish)
- **HOLD**: Combined score between -0.2 and 0.2 (Neutral)
- **SELL**: Combined score ≤ -0.2 (Bearish)
- **STRONG_SELL**: Combined score ≤ -0.6 (Very bearish)

## Configuration

### API Keys (`.env` file)
```env
# Required for AI-powered analysis
ANTHROPIC_API_KEY=your_key_here  # Get from https://console.anthropic.com/
OPENAI_API_KEY=your_key_here     # Get from https://platform.openai.com/api-keys
```

**Note:** The system works without API keys using technical + sentiment analysis only, but AI analysis provides more comprehensive recommendations.

## Example Use Cases

### 1. Daily Market Check
```bash
# Check overall market
curl http://localhost:8000/ai/market-analysis

# Analyze your holdings
curl http://localhost:8000/ai/portfolio-suggestions
```

### 2. Before Buying a Stock
```bash
# Get comprehensive analysis
curl -X POST http://localhost:8000/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"INFY","exchange":"NSE"}'
```

### 3. Monitor Technical Indicators
```bash
# Check if stock is overbought/oversold
curl http://localhost:8000/ai/technical-indicators/INFY?exchange=NSE
```

## Interpreting Results

### Confidence Score
- **80-100%**: Very high confidence, strong signals
- **60-79%**: High confidence, good signals
- **40-59%**: Moderate confidence, mixed signals
- **20-39%**: Low confidence, unclear direction
- **0-19%**: Very low confidence, avoid trading

### Technical Scores
- **RSI < 30**: Oversold (potential buy)
- **RSI > 70**: Overbought (potential sell)
- **MACD crossover**: Bullish (buy) or bearish (sell) signal
- **Price near lower Bollinger Band**: Potential buy
- **Price near upper Bollinger Band**: Potential sell

## Next Steps

### Phase 3 (Automation) - Coming Soon:
- **Order Execution**: Automatically execute recommended trades
- **Risk Management**: Position sizing, daily limits, circuit breakers
- **Paper Trading**: Test strategies without real money
- **Backtesting**: Test AI performance on historical data
- **Performance Tracking**: Track AI vs manual trades

### Phase 4 (Advanced Features):
- **Portfolio Rebalancing**: AI-suggested portfolio optimization
- **Tax-Loss Harvesting**: Identify tax-saving opportunities
- **Dividend Tracking**: Monitor and predict dividend income
- **Custom Strategies**: Define your own trading rules

## API Documentation

Full interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Common Issues:

**1. No AI recommendations (fallback mode)**
- Check if API keys are set in `.env`
- Verify internet connection
- Check API key validity

**2. "No historical data found"**
- Symbol might be incorrect
- Exchange parameter might be wrong
- Stock might be delisted

**3. Low confidence scores**
- Mixed technical signals
- Neutral sentiment
- Market uncertainty
- This is normal - wait for clearer signals

**4. API rate limits**
- Yahoo Finance: Free tier limitations
- LLM APIs: Check your usage limits
- Trading212: Rate limited, use caching

## Support

For issues or questions:
1. Check server logs: Look for ERROR messages
2. Verify broker connections: GET `/auth/status`
3. Test individual components: Use specific endpoints

## Security Notes

- API keys are stored in `.env` (NOT committed to git)
- Recommendations are suggestions only
- Always review before executing trades
- Use stop-loss orders to limit risk
- Never invest more than you can afford to lose

---

**Version**: 1.0.0 (Phase 1 & 2 Complete)
**Last Updated**: October 25, 2025
**Status**: ✅ Ready for testing
