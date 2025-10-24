# API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication. In production, implement proper authentication mechanisms.

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Portfolio Endpoints

#### Get Zerodha Portfolio
```http
GET /portfolio/zerodha
```

**Response:**
```json
{
  "broker": "zerodha",
  "total_value": 100000.0,
  "total_investment": 95000.0,
  "total_pnl": 5000.0,
  "total_pnl_percentage": 5.26,
  "holdings": [
    {
      "symbol": "RELIANCE",
      "quantity": 100,
      "average_price": 2500.0,
      "current_price": 2600.0,
      "current_value": 260000.0,
      "invested_value": 250000.0,
      "pnl": 10000.0,
      "pnl_percentage": 4.0,
      "day_pnl": 500.0,
      "asset_type": "equity"
    }
  ],
  "last_updated": "2024-01-01T12:00:00Z"
}
```

#### Get Trading 212 Portfolio
```http
GET /portfolio/trading212
```

**Response:** Same format as Zerodha portfolio

#### Get Combined Portfolio
```http
GET /portfolio/combined
```

**Response:** Combined data from all connected brokers

### Analysis Endpoints

#### Analyze Portfolio
```http
POST /analyze
Content-Type: application/json

{
  "broker": "combined",
  "include_recommendations": true,
  "include_risk_analysis": true
}
```

**Response:**
```json
{
  "broker": "combined",
  "metrics": {
    "total_value": 100000.0,
    "total_pnl": 5000.0,
    "total_pnl_percentage": 5.26,
    "day_pnl": 200.0,
    "day_pnl_percentage": 0.2,
    "sharpe_ratio": 1.2,
    "max_drawdown": 0.15,
    "volatility": 0.18,
    "beta": 1.1,
    "alpha": 0.02,
    "risk_level": "medium",
    "diversification_ratio": 0.7,
    "concentration_risk": 0.3
  },
  "asset_allocation": {
    "equity": 70.0,
    "debt": 20.0,
    "commodities": 5.0,
    "forex": 3.0,
    "crypto": 2.0,
    "others": 0.0
  },
  "recommendations": [
    "Portfolio risk is medium. Consider diversifying holdings.",
    "Low diversification. Consider adding assets from different sectors."
  ],
  "analysis_date": "2024-01-01T12:00:00Z"
}
```

### Order Endpoints

#### Place Zerodha Order
```http
POST /orders/zerodha
Content-Type: application/json

{
  "symbol": "RELIANCE",
  "quantity": 10,
  "transaction_type": "BUY",
  "order_type": "MARKET",
  "product": "CNC",
  "variety": "regular",
  "exchange": "NSE"
}
```

**Response:**
```json
{
  "order_id": "240101000123456",
  "status": "success",
  "message": "Order placed successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Place Trading 212 Order
```http
POST /orders/trading212
Content-Type: application/json

{
  "symbol": "AAPL",
  "quantity": 5,
  "transaction_type": "BUY",
  "order_type": "MARKET"
}
```

**Response:** Same format as Zerodha order

## Data Models

### PortfolioResponse
```typescript
interface PortfolioResponse {
  broker: string;
  total_value: number;
  total_investment: number;
  total_pnl: number;
  total_pnl_percentage: number;
  holdings: HoldingModel[];
  last_updated: string;
}
```

### HoldingModel
```typescript
interface HoldingModel {
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  current_value: number;
  invested_value: number;
  pnl: number;
  pnl_percentage: number;
  day_pnl: number;
  asset_type: string;
}
```

### OrderRequest
```typescript
interface OrderRequest {
  broker: string;
  symbol: string;
  quantity: number;
  transaction_type: "BUY" | "SELL";
  order_type: "MARKET" | "LIMIT" | "STOP_LOSS" | "STOP_LOSS_MARKET";
  product: "CNC" | "MIS" | "NRML" | "BO" | "CO";
  variety: "regular" | "bo" | "co" | "amo";
  exchange: string;
  price?: number;
  validity: string;
}
```

### OrderResponse
```typescript
interface OrderResponse {
  order_id?: string;
  status: string;
  message: string;
  timestamp: string;
}
```

### AnalysisRequest
```typescript
interface AnalysisRequest {
  broker: string;
  include_recommendations: boolean;
  include_risk_analysis: boolean;
}
```

### AnalysisResponse
```typescript
interface AnalysisResponse {
  broker: string;
  metrics: PortfolioMetricsModel;
  asset_allocation: AssetAllocationModel;
  recommendations: string[];
  analysis_date: string;
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid broker specified"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error fetching portfolio data"
}
```

## Rate Limits

- Portfolio requests: 100 per minute
- Order requests: 10 per minute
- Analysis requests: 20 per minute

## WebSocket Endpoints

### Real-time Portfolio Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/portfolio');
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Portfolio update:', data);
};
```

### Real-time Market Data
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/market');
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Market data:', data);
};
```

## SDK Examples

### Python SDK
```python
import requests

# Get portfolio
response = requests.get('http://localhost:8000/portfolio/combined')
portfolio = response.json()

# Analyze portfolio
analysis = requests.post('http://localhost:8000/analyze', json={
    'broker': 'combined',
    'include_recommendations': True
}).json()

# Place order
order = requests.post('http://localhost:8000/orders/zerodha', json={
    'symbol': 'RELIANCE',
    'quantity': 10,
    'transaction_type': 'BUY',
    'order_type': 'MARKET'
}).json()
```

### JavaScript SDK
```javascript
// Get portfolio
const portfolio = await fetch('http://localhost:8000/portfolio/combined')
  .then(response => response.json());

// Analyze portfolio
const analysis = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    broker: 'combined',
    include_recommendations: true
  })
}).then(response => response.json());

// Place order
const order = await fetch('http://localhost:8000/orders/zerodha', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    symbol: 'RELIANCE',
    quantity: 10,
    transaction_type: 'BUY',
    order_type: 'MARKET'
  })
}).then(response => response.json());
```

## Testing

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Get portfolio
curl http://localhost:8000/portfolio/combined

# Analyze portfolio
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"broker": "combined", "include_recommendations": true}'

# Place order
curl -X POST http://localhost:8000/orders/zerodha \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "quantity": 10, "transaction_type": "BUY", "order_type": "MARKET"}'
```

### Using Postman
1. Import the API collection
2. Set base URL to `http://localhost:8000`
3. Configure environment variables
4. Run the test suite

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with:
- Try-it-out functionality
- Request/response examples
- Schema definitions
- Authentication testing

