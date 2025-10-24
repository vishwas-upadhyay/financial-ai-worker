"""
FastAPI main application
Financial AI Worker API endpoints
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import settings
from src.brokers.zerodha_client import ZerodhaClient
from src.brokers.trading212_client import Trading212Client
from src.analytics.portfolio_analyzer import PortfolioAnalyzer, PortfolioMetrics
from src.models.portfolio_models import (
    PortfolioResponse,
    OrderRequest,
    OrderResponse,
    AnalysisRequest,
    AnalysisResponse
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Financial AI Worker - Portfolio Analysis and Trading Platform"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = PortfolioAnalyzer()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the interactive dashboard"""
    dashboard_path = Path(__file__).parent.parent / "web" / "dashboard.html"

    if not dashboard_path.exists():
        return HTMLResponse("""
        <html>
            <head>
                <title>Financial AI Worker</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { color: #2c3e50; }
                    .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .method { color: #28a745; font-weight: bold; }
                </style>
            </head>
            <body>
                <h1 class="header">Financial AI Worker</h1>
                <p>Portfolio Analysis and Trading Platform</p>

                <h2>API Endpoints:</h2>

                <div class="endpoint">
                    <span class="method">GET</span> /dashboard - Interactive Dashboard
                </div>

                <div class="endpoint">
                    <span class="method">GET</span> /health - Health check
                </div>

                <div class="endpoint">
                    <span class="method">GET</span> /portfolio/zerodha - Get Zerodha portfolio
                </div>

                <div class="endpoint">
                    <span class="method">GET</span> /portfolio/trading212 - Get Trading 212 portfolio
                </div>

                <div class="endpoint">
                    <span class="method">GET</span> /portfolio/combined - Get combined portfolio
                </div>

                <div class="endpoint">
                    <span class="method">GET</span> /analyze/{broker} - Analyze portfolio
                </div>

                <div class="endpoint">
                    <span class="method">POST</span> /analyze - Analyze portfolio (JSON)
                </div>

                <div class="endpoint">
                    <span class="method">GET</span> /docs - Interactive API documentation
                </div>
            </body>
        </html>
        """)

    with open(dashboard_path, 'r') as f:
        return HTMLResponse(content=f.read())


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the interactive dashboard"""
    dashboard_path = Path(__file__).parent.parent / "web" / "dashboard.html"

    if not dashboard_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")

    with open(dashboard_path, 'r') as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version
    }


@app.get("/portfolio/zerodha", response_model=PortfolioResponse)
async def get_zerodha_portfolio():
    """Get Zerodha portfolio holdings"""
    try:
        async with ZerodhaClient() as client:
            # Get portfolio data
            holdings_data = await client.get_portfolio()
            positions_data = await client.get_positions()
            margins_data = await client.get_margins()
            
            # Process holdings
            holdings = []
            # Extract holdings from response
            holdings_list = []
            if isinstance(holdings_data, dict):
                if 'data' in holdings_data:
                    holdings_list = holdings_data['data']
                elif 'holdings' in holdings_data:
                    holdings_list = holdings_data['holdings']
                else:
                    holdings_list = holdings_data.get('data', {})

            for holding in holdings_list:
                holdings.append({
                    'symbol': holding.get('tradingsymbol'),
                    'quantity': holding.get('quantity', 0),
                    'average_price': holding.get('average_price', 0),
                    'current_price': holding.get('last_price', 0),
                    'current_value': holding.get('quantity', 0) * holding.get('last_price', 0),
                    'invested_value': holding.get('quantity', 0) * holding.get('average_price', 0),
                    'pnl': holding.get('pnl', 0),
                    'pnl_percentage': holding.get('pnl_percentage', 0),
                    'day_pnl': holding.get('day_change', 0),
                    'asset_type': 'equity'
                })
            
            # Calculate total metrics
            total_value = sum(h['current_value'] for h in holdings)
            total_investment = sum(h['invested_value'] for h in holdings)
            total_pnl = total_value - total_investment
            total_pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0
            
            return PortfolioResponse(
                broker="zerodha",
                total_value=total_value,
                total_investment=total_investment,
                total_pnl=total_pnl,
                total_pnl_percentage=total_pnl_percentage,
                holdings=holdings,
                last_updated=datetime.now().isoformat()
            )
            
    except Exception as e:
        logger.error(f"Error fetching Zerodha portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/trading212", response_model=PortfolioResponse)
async def get_trading212_portfolio():
    """Get Trading 212 portfolio holdings"""
    try:
        async with Trading212Client() as client:
            # Get portfolio data (returns list of positions)
            positions_data = await client.get_portfolio()

            # Get account cash info for additional metrics
            try:
                cash_data = await client.get_account_cash()
            except Exception as e:
                logger.warning(f"Could not fetch cash data: {e}")
                cash_data = {}

            # Process holdings
            holdings = []
            total_value = 0
            total_investment = 0

            for position in positions_data:
                # Trading212 API returns: ticker, quantity, averagePrice, currentPrice, ppl, fxPpl
                ticker = position.get('ticker', '')
                quantity = position.get('quantity', 0)
                avg_price = position.get('averagePrice', 0)
                current_price = position.get('currentPrice', 0)
                ppl = position.get('ppl', 0)  # Profit/Loss in position currency

                # Calculate values
                invested_value = quantity * avg_price
                current_value = quantity * current_price
                pnl_percentage = (ppl / invested_value * 100) if invested_value > 0 else 0

                holdings.append({
                    'symbol': ticker,
                    'quantity': quantity,
                    'average_price': avg_price,
                    'current_price': current_price,
                    'current_value': current_value,
                    'invested_value': invested_value,
                    'pnl': ppl,
                    'pnl_percentage': pnl_percentage,
                    'day_pnl': 0,  # Trading212 doesn't provide daily P&L in basic API
                    'asset_type': 'equity'
                })

                total_value += current_value
                total_investment += invested_value

            # Calculate total metrics
            total_pnl = total_value - total_investment
            total_pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0

            return PortfolioResponse(
                broker="trading212",
                total_value=total_value,
                total_investment=total_investment,
                total_pnl=total_pnl,
                total_pnl_percentage=total_pnl_percentage,
                holdings=holdings,
                last_updated=datetime.now().isoformat()
            )

    except Exception as e:
        logger.error(f"Error fetching Trading 212 portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/combined", response_model=PortfolioResponse)
async def get_combined_portfolio():
    """Get combined portfolio from all brokers"""
    try:
        # Get portfolios from all brokers
        zerodha_portfolio = None
        trading212_portfolio = None
        
        # Try to get Zerodha portfolio
        try:
            zerodha_portfolio = await get_zerodha_portfolio()
        except Exception as e:
            logger.warning(f"Could not fetch Zerodha portfolio: {e}")
        
        # Try to get Trading 212 portfolio
        try:
            trading212_portfolio = await get_trading212_portfolio()
        except Exception as e:
            logger.warning(f"Could not fetch Trading 212 portfolio: {e}")
        
        # Combine portfolios
        all_holdings = []
        total_value = 0
        total_investment = 0
        total_pnl = 0
        
        if zerodha_portfolio:
            all_holdings.extend(zerodha_portfolio.holdings)
            total_value += zerodha_portfolio.total_value
            total_investment += zerodha_portfolio.total_investment
            total_pnl += zerodha_portfolio.total_pnl
        
        if trading212_portfolio:
            all_holdings.extend(trading212_portfolio.holdings)
            total_value += trading212_portfolio.total_value
            total_investment += trading212_portfolio.total_investment
            total_pnl += trading212_portfolio.total_pnl
        
        total_pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        
        return PortfolioResponse(
            broker="combined",
            total_value=total_value,
            total_investment=total_investment,
            total_pnl=total_pnl,
            total_pnl_percentage=total_pnl_percentage,
            holdings=all_holdings,
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error fetching combined portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _perform_portfolio_analysis(broker: str) -> AnalysisResponse:
    """Internal function to perform portfolio analysis"""
    # Get portfolio data
    if broker == "zerodha":
        portfolio = await get_zerodha_portfolio()
    elif broker == "trading212":
        portfolio = await get_trading212_portfolio()
    elif broker == "combined":
        portfolio = await get_combined_portfolio()
    else:
        raise HTTPException(status_code=400, detail="Invalid broker specified")

    # Convert Pydantic models to dictionaries for analyzer
    holdings_dicts = [holding.model_dump() if hasattr(holding, 'model_dump') else holding
                      for holding in portfolio.holdings]

    # Perform analysis
    metrics = analyzer.analyze_portfolio(holdings_dicts)
    asset_allocation = analyzer.get_asset_allocation(holdings_dicts)
    recommendations = analyzer.generate_recommendations(metrics)

    # Convert dataclass metrics to dict for Pydantic model
    metrics_dict = {
        "total_value": metrics.total_value,
        "total_pnl": metrics.total_pnl,
        "total_pnl_percentage": metrics.total_pnl_percentage,
        "day_pnl": metrics.day_pnl,
        "day_pnl_percentage": metrics.day_pnl_percentage,
        "sharpe_ratio": metrics.sharpe_ratio,
        "max_drawdown": metrics.max_drawdown,
        "volatility": metrics.volatility,
        "beta": metrics.beta,
        "alpha": metrics.alpha,
        "risk_level": metrics.risk_level.value,
        "diversification_ratio": metrics.diversification_ratio,
        "concentration_risk": metrics.concentration_risk
    }

    # Convert asset allocation dataclass to dict
    allocation_dict = {
        "equity": asset_allocation.equity,
        "debt": asset_allocation.debt,
        "commodities": asset_allocation.commodities,
        "forex": asset_allocation.forex,
        "crypto": asset_allocation.crypto,
        "others": asset_allocation.others
    }

    return AnalysisResponse(
        broker=broker,
        metrics=metrics_dict,
        asset_allocation=allocation_dict,
        recommendations=recommendations,
        analysis_date=datetime.now().isoformat()
    )


@app.get("/analyze/{broker}", response_model=AnalysisResponse)
async def analyze_portfolio_get(broker: str):
    """Analyze portfolio via GET request (browser-friendly)"""
    try:
        return await _perform_portfolio_analysis(broker)
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_portfolio(request: AnalysisRequest):
    """Analyze portfolio and provide insights via POST"""
    try:
        return await _perform_portfolio_analysis(request.broker)
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders/zerodha", response_model=OrderResponse)
async def place_zerodha_order(order: OrderRequest):
    """Place order on Zerodha"""
    try:
        async with ZerodhaClient() as client:
            result = await client.place_order(
                variety=order.variety,
                exchange=order.exchange,
                tradingsymbol=order.symbol,
                transaction_type=order.transaction_type,
                quantity=order.quantity,
                product=order.product,
                order_type=order.order_type,
                price=order.price,
                validity=order.validity
            )
            
            return OrderResponse(
                order_id=result.get('order_id'),
                status=result.get('status'),
                message=result.get('message', 'Order placed successfully'),
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        logger.error(f"Error placing Zerodha order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders/trading212", response_model=OrderResponse)
async def place_trading212_order(order: OrderRequest):
    """Place order on Trading 212"""
    try:
        async with Trading212Client() as client:
            result = await client.place_order(
                symbol=order.symbol,
                side=order.transaction_type,
                quantity=order.quantity,
                order_type=order.order_type,
                price=order.price
            )
            
            return OrderResponse(
                order_id=result.get('order_id'),
                status=result.get('status'),
                message=result.get('message', 'Order placed successfully'),
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        logger.error(f"Error placing Trading 212 order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )

