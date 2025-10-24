# Financial AI Worker - Interactive Dashboard Guide

## Dashboard Access

The interactive dashboard is now fully functional and accessible at:

**Main Dashboard URL**: http://localhost:8000/

Alternative access: http://localhost:8000/dashboard

## Features

### 1. **Portfolio Overview**
- Real-time portfolio value tracking
- Total P&L (Profit & Loss) with percentage returns
- Number of holdings
- Visual metrics cards with color-coded positive/negative indicators

### 2. **Interactive Charts**

#### Portfolio Value Chart
- Bar chart showing current portfolio value
- Real-time updates

#### Asset Allocation Chart
- Pie chart (donut style) showing distribution across asset types
- Equity, Debt, Commodities, Forex, Crypto, Others

#### P&L Analysis
- Visual representation of profit/loss
- Color-coded (green for profit, red for loss)

#### Risk vs Return Chart
- Scatter plot showing risk-return profile of each holding
- Bubble size represents position size
- Interactive hover for details

#### Top Holdings Chart
- Bar chart of top 10 holdings by value
- Quick overview of portfolio concentration

#### Portfolio Metrics Dashboard
- Key performance indicators
- Delta comparison against benchmarks

### 3. **Controls**

#### Broker Selection
- **Combined Portfolio**: View all brokers together
- **Zerodha**: View Zerodha holdings only
- **Trading 212**: View Trading 212 holdings only

#### Action Buttons
- **Refresh Data**: Update portfolio data in real-time
- **Analyze Portfolio**: Get AI-powered analysis and recommendations

### 4. **AI Recommendations**
When you click "Analyze Portfolio", you'll receive:
- Risk assessment (Low/Medium/High/Very High)
- Portfolio diversification score
- Concentration risk analysis
- Performance metrics (Sharpe ratio, Alpha, Beta)
- Actionable recommendations for portfolio improvement

## How to Use

1. **Open Dashboard**
   ```
   http://localhost:8000/
   ```

2. **Select Broker**
   - Use the dropdown to choose which portfolio to view
   - Default is "Combined Portfolio"

3. **View Data**
   - Dashboard automatically loads on page load
   - All charts are interactive (hover, zoom, pan)

4. **Refresh Data**
   - Click "Refresh Data" to get latest portfolio values
   - Success message will appear

5. **Get Analysis**
   - Click "Analyze Portfolio" button
   - Wait for analysis to complete
   - AI recommendations will appear at the bottom

## Technical Details

### Technologies Used
- **Frontend**: HTML5, CSS3, JavaScript
- **Charting**: Plotly.js
- **HTTP Client**: Axios
- **Backend**: FastAPI (Python)

### API Endpoints Used by Dashboard

The dashboard communicates with these endpoints:

```
GET  /portfolio/{broker}     - Fetch portfolio data
POST /analyze                - Get AI analysis
GET  /analyze/{broker}       - Alternative analysis endpoint
```

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Features Breakdown

### Metrics Displayed

1. **Total Value**: Current market value of all holdings
2. **Total P&L**: Absolute profit/loss in currency
3. **Return %**: Percentage return on investment
4. **Holdings**: Number of stocks/assets in portfolio

### Analysis Metrics

- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest portfolio decline
- **Volatility**: Portfolio price fluctuation measure
- **Beta**: Market correlation (1.0 = moves with market)
- **Alpha**: Performance vs expected returns
- **Diversification Ratio**: How well diversified
- **Concentration Risk**: Percentage in largest holding

## Current Portfolio Status

Based on latest data:
- **Total Value**: ₹196,827.50
- **Total P&L**: -₹8,435.10 (-4.11%)
- **Holdings**: 2 stocks (INFY, TATACAP)
- **Risk Level**: Very High (92% concentration in INFY)

## Recommendations

The AI has identified:
1. ⚠️ Very high portfolio risk - diversify holdings
2. ⚠️ High concentration (92% in one stock) - spread investments
3. ⚠️ Low diversification - add different sectors
4. ⚠️ Negative alpha - review investment strategy

## Troubleshooting

### Dashboard not loading?
- Check if application is running: `ps aux | grep python3`
- Verify port 8000 is not blocked
- Check browser console for errors (F12)

### Charts not showing?
- Ensure internet connection (loads Plotly.js from CDN)
- Check if API endpoints are responding
- Clear browser cache

### "Failed to fetch data" error?
- Check if Zerodha access token is valid (expires daily)
- Verify API is running on port 8000
- Check network tab in browser DevTools

## Daily Token Refresh

**IMPORTANT**: Zerodha access tokens expire daily at midnight.

To refresh token:
```bash
python3 generate_token.py
```

Then restart the application:
```bash
python3 main.py
```

## Support

For issues or questions:
- Check logs: `tail -f logs/financial_ai_worker.log`
- API docs: http://localhost:8000/docs
- GitHub issues (if repository configured)

## Future Enhancements

Potential improvements:
- Historical performance graphs
- Real-time price updates via WebSocket
- Order placement from dashboard
- Alerts and notifications
- Mobile responsive improvements
- Dark mode toggle
- Export reports (PDF/Excel)
- Comparison with indices (NIFTY, SENSEX)
