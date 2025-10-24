# Financial AI Worker

A comprehensive investment portfolio analysis and tracking system that connects to Zerodha and Trading 212 brokers via MCP servers.

## Features

- **Portfolio Analysis**: Real-time portfolio tracking and performance analysis
- **Multi-Broker Support**: Integration with Zerodha and Trading 212
- **Data Visualization**: Interactive charts and reports
- **AI-Powered Insights**: Automated analysis and recommendations
- **Risk Management**: Portfolio risk assessment and alerts

## Architecture

- **Backend**: Python-based MCP server integration
- **Frontend**: Modern web interface with real-time updates
- **Data Layer**: Secure broker API connections
- **Analytics**: Advanced portfolio analytics engine

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Configure broker credentials in `config/settings.py`
3. Run the application: `python main.py`

## Broker Integration

### Zerodha
- Uses Zerodha's Kite API via MCP server
- Supports equity, derivatives, and mutual funds
- Real-time market data and order management

### Trading 212
- Integration with Trading 212 API
- Multi-asset support (stocks, forex, commodities)
- Advanced charting and analysis tools

## Security

- Encrypted credential storage
- Secure API communication
- GDPR compliant data handling
- Regular security audits

## License

MIT License - see LICENSE file for details 


## Current Status
Zeroda analysis is not possible as thowing 500 error. 
Trading 212 yet to integrate 
 

