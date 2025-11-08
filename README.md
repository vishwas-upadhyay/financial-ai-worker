# Financial AI Worker 🤖💰

A comprehensive AI-powered investment portfolio management and analysis system with intelligent stock recommendations powered by Claude Sonnet 4.5. Integrates with Zerodha (India) and Trading212 (Europe/US) brokers for real-time portfolio tracking.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Features

### Portfolio Management
- **Multi-Broker Support**: Zerodha (Indian markets) and Trading212 (Global markets)
- **Real-Time Tracking**: Live portfolio updates with P&L calculations
- **Multi-Currency**: Support for INR, USD, EUR with automatic conversion
- **Combined View**: Unified dashboard for all broker accounts
- **Performance Analytics**: ROI, total returns, and risk metrics

### AI-Powered Stock Analysis
- **Technical Analysis**: 13+ indicators including RSI, MACD, Bollinger Bands, Moving Averages
- **Sentiment Analysis**: News headline analysis for market sentiment
- **LLM Integration**: Claude Sonnet 4.5 and GPT-4 for intelligent recommendations
- **Weighted Scoring**: Technical (40%) + Sentiment (20%) + AI (40%)
- **Recommendation Types**: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
- **Target Prices**: AI-generated price targets and stop-loss levels

### Interactive Dashboards
- **Main Dashboard**: Portfolio overview with charts and analytics
- **AI Dashboard**: Stock analysis with interactive recommendation cards
- **Settings Page**: Easy broker authentication and configuration
- **Responsive Design**: Works on desktop and mobile devices

### API Features
- **RESTful API**: 20+ endpoints for portfolio and AI operations
- **Interactive Docs**: Swagger UI at `/docs` and ReDoc at `/redoc`
- **CORS Enabled**: Cross-origin support for web applications
- **Authentication**: Secure token-based broker authentication

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Broker Setup](#broker-setup)
- [AI Configuration](#ai-configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Architecture](#architecture)

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vishwas-upadhyay/financial-ai-worker.git
cd financial-ai-worker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Start the server
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Open in browser
open http://localhost:8000
```

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client
- `yfinance` - Market data
- `anthropic` - Claude API
- `openai` - GPT-4 API
- `pandas-ta` - Technical analysis
- `pydantic-settings` - Configuration management

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the root directory:

```env
# Application Settings
APP_NAME=Financial AI Worker
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./financial_ai_worker.db

# Zerodha API Credentials
# Get from: https://kite.zerodha.com/
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret
ZERODHA_ACCESS_TOKEN=your_access_token
ZERODHA_REDIRECT_URL=http://localhost:8000/zerodha/callback

# Trading 212 API Credentials
# Get from: https://www.trading212.com/ -> Settings -> API (Beta)
TRADING212_API_KEY=your_trading212_api_key
TRADING212_API_SECRET=your_trading212_api_secret

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (optional - for caching)
REDIS_URL=redis://localhost:6379

# AI Configuration
# Get Anthropic key from: https://console.anthropic.com/
# Get OpenAI key from: https://platform.openai.com/api-keys
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/financial_ai_worker.log
```

## 🏃 Running the Application

### Start Server (Development)
```bash
# Standard mode with auto-reload
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# With custom host/port
python3 -m uvicorn src.api.main:app --host 127.0.0.1 --port 5000 --reload

# With specific log level
python3 -m uvicorn src.api.main:app --log-level debug --reload
```

### Start Server (Production)
```bash
# Using multiple workers
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn (recommended for production)
gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Stop Server
```bash
# Find the process
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or using pkill
pkill -f uvicorn
```

### Run in Background
```bash
# Using nohup
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &

# Using systemd (create service file)
sudo systemctl start financial-ai-worker
```

## 📚 API Documentation

### Access Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Portfolio Endpoints
```bash
GET  /health                          # Health check
GET  /                                # Main dashboard
GET  /dashboard                       # Dashboard (HTML)
GET  /ai-dashboard                    # AI recommendations dashboard
GET  /settings                        # Settings page

# Portfolio
GET  /portfolio/zerodha              # Zerodha portfolio
GET  /portfolio/trading212           # Trading212 portfolio
GET  /portfolio/combined             # Combined portfolio
POST /analyze                        # Analyze portfolio

# Authentication
GET  /auth/status                    # Check auth status
POST /auth/zerodha/login            # Login to Zerodha
POST /auth/trading212/login         # Login to Trading212
DELETE /auth/zerodha/logout         # Logout from Zerodha
DELETE /auth/trading212/logout      # Logout from Trading212
```

#### AI Endpoints
```bash
POST /ai/analyze                     # Analyze specific stock
GET  /ai/recommendations             # List all recommendations
GET  /ai/recommendations/{id}        # Get specific recommendation
POST /ai/recommendations/{id}/approve # Approve/reject recommendation
GET  /ai/config                      # Get AI configuration
PUT  /ai/config                      # Update AI configuration
GET  /ai/technical-indicators/{symbol} # Get technical indicators
GET  /ai/market-analysis             # Overall market sentiment
GET  /ai/portfolio-suggestions       # AI suggestions for holdings
```

### Example API Calls

```bash
# Analyze a stock
curl -X POST http://localhost:8000/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","exchange":"US"}'

# Get market overview
curl http://localhost:8000/ai/market-analysis

# Get technical indicators
curl http://localhost:8000/ai/technical-indicators/INFY?exchange=NSE

# Update AI config
curl -X PUT http://localhost:8000/ai/config \
  -H "Content-Type: application/json" \
  -d '{"risk_tolerance":"aggressive","min_confidence_threshold":70.0}'
```

## 🏦 Broker Setup

### Zerodha Setup

1. **Create API App**:
   - Go to https://kite.zerodha.com/
   - Navigate to "My Account" → "Apps"
   - Create a new app

2. **Get Credentials**:
   - Note down API Key and API Secret
   - Set redirect URL: `http://localhost:8000/zerodha/callback`

3. **Login Flow**:
   - Visit http://localhost:8000/settings
   - Click "Login to Zerodha"
   - Authorize the app
   - You'll be redirected back with access

### Trading212 Setup

1. **Enable API Access**:
   - Login to https://www.trading212.com/
   - Go to Settings → API (Beta)
   - Enable API access

2. **Generate API Key**:
   - Click "Generate API Key"
   - Copy the key immediately (shown only once)
   - Store securely in `.env` file

3. **Login**:
   - Visit http://localhost:8000/settings
   - Enter your API key
   - Click "Login to Trading212"

### Important Notes

- **Zerodha tokens expire daily** - Need to re-login each day
- **Trading212 API keys can be regenerated** - Old keys become invalid
- **Rate Limits**: Trading212 has strict rate limits (60 requests/minute)
- **Security**: Never commit `.env` file to version control

## 🤖 AI Configuration

### AI Settings

Configure AI behavior via API or web UI:

```python
{
    "enabled": true,                      # Enable AI recommendations
    "risk_tolerance": "moderate",         # conservative, moderate, aggressive
    "automation_level": "manual",         # manual, semi_auto, full_auto
    "daily_trade_limit": 5,              # Max trades per day
    "max_position_size_percent": 10.0,   # Max % of portfolio per position
    "min_confidence_threshold": 65.0,    # Minimum confidence to recommend
    "use_llm": true,                     # Use LLM for analysis
    "llm_provider": "anthropic"          # anthropic or openai
}
```

### Technical Indicators

The system calculates:
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands**
- **Moving Averages** (SMA 50, SMA 200, EMA 20)
- **ATR** (Average True Range)
- **Stochastic Oscillator**
- **Volume Analysis**
- **Support/Resistance Levels**

### Recommendation Logic

```
Final Score = (Technical Score × 0.4) + (Sentiment Score × 0.2) + (AI Score × 0.4)

Recommendation:
- STRONG_BUY: Score ≥ 0.6
- BUY: Score ≥ 0.2
- HOLD: -0.2 < Score < 0.2
- SELL: Score ≤ -0.2
- STRONG_SELL: Score ≤ -0.6
```

## 🐛 Troubleshooting

### Common Issues

**1. Server won't start**
```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Try different port
python3 -m uvicorn src.api.main:app --port 8001
```

**2. Zerodha 403 Forbidden**
- Token expired - Re-login via settings page
- API key invalid - Check credentials in `.env`
- Wrong redirect URL - Update in Zerodha app settings

**3. Trading212 401 Unauthorized**
- API key expired - Generate new key from Trading212
- Update `.env` with new key
- Restart server

**4. AI not working (reasoning shows "unavailable")**
- Check API keys in `.env`
- Verify model name: `claude-sonnet-4-5-20250929`
- Check API quota/limits
- Review logs for errors

**5. Database locked**
```bash
# Remove database lock
rm financial_ai_worker.db-lock

# Recreate database
rm financial_ai_worker.db
# Server will recreate on next start
```

### Debug Commands

```bash
# Check environment variables
python3 -c "from config.settings import settings; print(settings)"

# Test Zerodha connection
python3 -c "from src.brokers.zerodha_client import ZerodhaClient; print('OK')"

# Test Trading212 connection
python3 -c "from src.brokers.trading212_client import Trading212Client; print('OK')"

# Check AI API keys
python3 -c "from config.settings import settings; print('Anthropic:', 'SET' if settings.anthropic_api_key else 'NOT SET')"

# View logs
tail -f logs/financial_ai_worker.log

# Test API endpoint
curl http://localhost:8000/health
```

### Logs

Logs are stored in:
- **File**: `logs/financial_ai_worker.log`
- **Console**: Standard output (when running with `--reload`)

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

Change log level in `.env`:
```env
LOG_LEVEL=DEBUG
```

## 👨‍💻 Development

### Project Structure
```
Financial AI Worker/
├── src/
│   ├── ai/                      # AI modules
│   │   ├── market_data_aggregator.py
│   │   ├── technical_indicators.py
│   │   ├── sentiment_analyzer.py
│   │   ├── llm_advisor.py
│   │   └── recommendation_engine.py
│   ├── api/                     # API endpoints
│   │   └── main.py
│   ├── brokers/                 # Broker clients
│   │   ├── zerodha_client.py
│   │   └── trading212_client.py
│   ├── models/                  # Data models
│   │   ├── portfolio_models.py
│   │   └── ai_models.py
│   ├── services/                # Services
│   │   ├── currency_converter.py
│   │   └── token_manager.py
│   └── web/                     # Web UI
│       ├── dashboard.html
│       ├── ai_dashboard.html
│       └── settings.html
├── config/
│   └── settings.py              # Configuration
├── logs/                        # Log files
├── .env                         # Environment variables
├── requirements.txt             # Dependencies
├── AI_SYSTEM_GUIDE.md          # AI system documentation
└── README.md                    # This file
```

### Adding New Features

1. **New Broker**:
   - Create client in `src/brokers/`
   - Implement authentication and portfolio fetching
   - Add endpoints in `main.py`

2. **New Technical Indicator**:
   - Add to `src/ai/technical_indicators.py`
   - Update `get_all_indicators()` method
   - Document in `AI_SYSTEM_GUIDE.md`

3. **New AI Provider**:
   - Update `src/ai/llm_advisor.py`
   - Add provider logic in `LLMAdvisor.__init__()`
   - Update configuration models

### Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_portfolio.py

# With coverage
pytest --cov=src tests/
```

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.9+)
- **AI**: Claude Sonnet 4.5, GPT-4
- **Data**: Yahoo Finance, Broker APIs
- **Frontend**: Vanilla JS, HTML5, CSS3
- **Database**: SQLite (token storage)
- **Deployment**: Uvicorn, Gunicorn

### Data Flow
```
User Request → FastAPI → Broker APIs → Data Processing → AI Analysis → Response
                  ↓
            Token Manager
                  ↓
            SQLite Database
```

### AI Pipeline
```
Market Data → Technical Analysis → Sentiment Analysis → LLM Analysis
                                                              ↓
                                                    Recommendation Engine
                                                              ↓
                                                    Weighted Score + Decision
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: https://github.com/vishwas-upadhyay/financial-ai-worker/issues
- **Documentation**: See `AI_SYSTEM_GUIDE.md` for AI features
- **API Docs**: http://localhost:8000/docs

## ⚠️ Disclaimer

This software is for educational and informational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions. The authors are not responsible for any financial losses incurred from using this software.

## 🙏 Acknowledgments

- **Zerodha** for Kite API
- **Trading212** for Trading API
- **Anthropic** for Claude AI
- **OpenAI** for GPT-4
- **Yahoo Finance** for market data
- **FastAPI** community for excellent framework

---

**Made with ❤️ by Vishwas Upadhyay**

**Version**: 1.0.0
**Last Updated**: November 2025
**Status**: ✅ Production Ready
