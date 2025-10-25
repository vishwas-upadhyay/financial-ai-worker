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
from src.services.currency_converter import currency_converter
from src.services.token_manager import token_manager
from src.models.portfolio_models import (
    PortfolioResponse,
    OrderRequest,
    OrderResponse,
    AnalysisRequest,
    AnalysisResponse
)
from src.models.ai_models import (
    RecommendationResponse,
    AIConfigResponse,
    AIConfigUpdate,
    StockAnalysisRequest,
    MarketAnalysisResponse,
    TechnicalIndicatorsResponse,
    RecommendationApproval
)
from src.ai.recommendation_engine import recommendation_engine
from src.ai.market_data_aggregator import market_data
from src.ai.technical_indicators import technical_indicators
from pydantic import BaseModel

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


# Pydantic models for authentication
class ZerodhaLoginRequest(BaseModel):
    api_key: str
    api_secret: str
    request_token: str


class Trading212LoginRequest(BaseModel):
    api_key: str
    api_secret: Optional[str] = None


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


@app.get("/ai-dashboard", response_class=HTMLResponse)
async def ai_dashboard():
    """Serve the AI recommendations dashboard"""
    dashboard_path = Path(__file__).parent.parent / "web" / "ai_dashboard.html"

    if not dashboard_path.exists():
        raise HTTPException(status_code=404, detail="AI Dashboard not found")

    with open(dashboard_path, 'r') as f:
        return HTMLResponse(content=f.read())


@app.get("/settings", response_class=HTMLResponse)
async def get_settings_page():
    """Serve the broker settings page"""
    settings_path = Path(__file__).parent.parent / "web" / "settings.html"

    if not settings_path.exists():
        raise HTTPException(status_code=404, detail="Settings page not found")

    with open(settings_path, 'r') as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version
    }


@app.get("/auth/status")
async def get_auth_status():
    """Get authentication status for all brokers"""
    return token_manager.get_all_tokens_status()


@app.get("/auth/zerodha/login-url")
async def get_zerodha_login_url(api_key: Optional[str] = None):
    """Get Zerodha login URL for OAuth"""
    # Use provided API key or fall back to settings
    key = api_key or settings.zerodha_api_key

    if not key:
        raise HTTPException(
            status_code=400,
            detail="Please provide API key in the form first. Get it from https://developers.kite.trade/"
        )

    redirect_url = settings.zerodha_redirect_url
    login_url = f"https://kite.zerodha.com/connect/login?api_key={key}&v=3"

    return {
        "login_url": login_url,
        "redirect_url": redirect_url,
        "api_key": key,
        "instructions": "After login, you'll be redirected with a request_token. Use that token to complete authentication."
    }


@app.post("/auth/zerodha/login")
async def zerodha_login(request: ZerodhaLoginRequest):
    """Complete Zerodha authentication with request token"""
    try:
        import hashlib

        # Generate checksum
        checksum_string = f"{request.api_key}{request.request_token}{request.api_secret}"
        checksum = hashlib.sha256(checksum_string.encode()).hexdigest()

        # Generate access token
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.kite.trade/session/token",
                data={
                    "api_key": request.api_key,
                    "request_token": request.request_token,
                    "checksum": checksum
                }
            )
            response.raise_for_status()
            data = response.json()

            access_token = data['data']['access_token']

            # Save tokens
            token_manager.save_zerodha_token(
                api_key=request.api_key,
                api_secret=request.api_secret,
                access_token=access_token,
                request_token=request.request_token
            )

            return {
                "success": True,
                "message": "Zerodha authentication successful",
                "expires_at": token_manager.get_zerodha_token()['expires_at']
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"Zerodha authentication failed: {e.response.text}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {e.response.text}")
    except Exception as e:
        logger.error(f"Error during Zerodha authentication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/trading212/login")
async def trading212_login(request: Trading212LoginRequest):
    """Save Trading212 API credentials"""
    try:
        # Save tokens
        token_manager.save_trading212_token(
            api_key=request.api_key,
            api_secret=request.api_secret
        )

        return {
            "success": True,
            "message": "Trading212 credentials saved successfully"
        }

    except Exception as e:
        logger.error(f"Error saving Trading212 credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/auth/zerodha/logout")
async def zerodha_logout():
    """Logout from Zerodha (delete tokens)"""
    try:
        token_manager.delete_zerodha_token()
        return {"success": True, "message": "Zerodha logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/auth/trading212/logout")
async def trading212_logout():
    """Logout from Trading212 (delete credentials)"""
    try:
        token_manager.delete_trading212_token()
        return {"success": True, "message": "Trading212 logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/currencies")
async def get_supported_currencies():
    """Get list of supported currencies"""
    return {
        "currencies": currency_converter.get_supported_currencies(),
        "default": "INR",
        "note": "Trading212 portfolio is in EUR, Zerodha portfolio is in INR"
    }


@app.get("/exchange-rate/{from_currency}/{to_currency}")
async def get_exchange_rate(from_currency: str, to_currency: str):
    """Get exchange rate between two currencies"""
    try:
        rates = await currency_converter.get_exchange_rates(from_currency.upper())
        if not rates:
            raise HTTPException(status_code=500, detail="Could not fetch exchange rates")

        to_currency = to_currency.upper()
        if to_currency not in rates:
            raise HTTPException(status_code=404, detail=f"Currency {to_currency} not found")

        return {
            "from": from_currency.upper(),
            "to": to_currency,
            "rate": rates[to_currency],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching exchange rate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/zerodha", response_model=PortfolioResponse)
async def get_zerodha_portfolio(currency: Optional[str] = None):
    """
    Get Zerodha portfolio holdings

    Query Parameters:
        currency: Target currency for display (INR or EUR). Default: INR (original)
    """
    try:
        # Validate currency
        if currency and currency.upper() not in ['INR', 'EUR']:
            raise HTTPException(
                status_code=400,
                detail="Only INR and EUR currencies are supported"
            )
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

            # Convert currency if requested
            source_currency = "INR"  # Zerodha default currency
            display_currency = currency.upper() if currency else source_currency

            if display_currency != source_currency:
                logger.info(f"Converting Zerodha portfolio from {source_currency} to {display_currency}")
                holdings, total_value, total_investment, total_pnl = await currency_converter.convert_portfolio(
                    holdings, source_currency, display_currency
                )
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
async def get_trading212_portfolio(currency: Optional[str] = None):
    """
    Get Trading 212 portfolio holdings

    Query Parameters:
        currency: Target currency for display (INR or EUR). Default: EUR (original)
    """
    try:
        # Validate currency
        if currency and currency.upper() not in ['INR', 'EUR']:
            raise HTTPException(
                status_code=400,
                detail="Only INR and EUR currencies are supported"
            )
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

            # Convert currency if requested
            source_currency = "EUR"  # Trading212 default currency
            display_currency = currency.upper() if currency else source_currency

            if display_currency != source_currency:
                logger.info(f"Converting portfolio from {source_currency} to {display_currency}")
                holdings, total_value, total_investment, total_pnl = await currency_converter.convert_portfolio(
                    holdings, source_currency, display_currency
                )
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
async def get_combined_portfolio(currency: Optional[str] = "INR"):
    """
    Get combined portfolio from all brokers

    Query Parameters:
        currency: Target currency for display (INR or EUR). Default: INR
    """
    try:
        # Validate currency
        if currency and currency.upper() not in ['INR', 'EUR']:
            raise HTTPException(
                status_code=400,
                detail="Only INR and EUR currencies are supported"
            )
        # Get portfolios from all brokers
        zerodha_portfolio = None
        trading212_portfolio = None
        
        # Try to get Zerodha portfolio (convert to target currency)
        try:
            zerodha_portfolio = await get_zerodha_portfolio(currency=currency)
        except Exception as e:
            logger.warning(f"Could not fetch Zerodha portfolio: {e}")

        # Try to get Trading 212 portfolio (convert to target currency)
        try:
            trading212_portfolio = await get_trading212_portfolio(currency=currency)
        except Exception as e:
            logger.warning(f"Could not fetch Trading 212 portfolio: {e}")

        # Combine portfolios
        all_holdings = []
        total_value = 0
        total_investment = 0
        total_pnl = 0

        if zerodha_portfolio:
            # Zerodha is already converted to target currency
            all_holdings.extend(zerodha_portfolio.holdings)
            total_value += zerodha_portfolio.total_value
            total_investment += zerodha_portfolio.total_investment
            total_pnl += zerodha_portfolio.total_pnl

        if trading212_portfolio:
            # Trading212 is already converted to target currency
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


# ============================================================================
# AI RECOMMENDATION ENDPOINTS
# ============================================================================

# Global AI config storage (in production, use database)
ai_config = AIConfigResponse()
recommendations_store = {}  # Store recommendations by ID


@app.post("/ai/analyze", response_model=RecommendationResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """
    Analyze a stock and generate AI recommendation

    Args:
        request: Stock analysis request with symbol and exchange

    Returns:
        AI recommendation with buy/sell/hold signal
    """
    try:
        logger.info(f"AI analysis requested for {request.symbol}")

        # Get portfolio context if requested
        portfolio_context = None
        if request.include_portfolio_context:
            try:
                # Check if stock is in portfolio
                portfolio = await get_combined_portfolio()
                for holding in portfolio.holdings:
                    if holding.get('symbol') == request.symbol:
                        portfolio_context = holding
                        break
            except Exception as e:
                logger.warning(f"Could not fetch portfolio context: {e}")

        # Generate recommendation
        recommendation = await recommendation_engine.analyze_stock(
            symbol=request.symbol,
            exchange=request.exchange,
            portfolio_context=portfolio_context
        )

        # Convert to response model
        rec_id = f"{request.symbol}_{int(datetime.now().timestamp())}"
        response = RecommendationResponse(
            id=rec_id,
            symbol=recommendation.symbol,
            exchange=request.exchange,
            action=recommendation.action.value,
            confidence=recommendation.confidence,
            current_price=recommendation.current_price,
            target_price=recommendation.target_price,
            stop_loss=recommendation.stop_loss,
            time_horizon=recommendation.time_horizon,
            reasoning=recommendation.reasoning,
            technical_score=recommendation.technical_score,
            sentiment_score=recommendation.sentiment_score,
            ai_score=recommendation.ai_score,
            key_points=recommendation.key_points,
            risks=recommendation.risks,
            opportunities=recommendation.opportunities,
            created_at=recommendation.created_at
        )

        # Store recommendation
        recommendations_store[rec_id] = response

        return response

    except Exception as e:
        logger.error(f"Error in AI analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/recommendations")
async def get_recommendations(
    limit: int = 10,
    action: Optional[str] = None
):
    """
    Get all AI recommendations

    Args:
        limit: Maximum number of recommendations to return
        action: Filter by action type (buy, sell, hold)

    Returns:
        List of recommendations
    """
    try:
        recs = list(recommendations_store.values())

        # Filter by action if specified
        if action:
            recs = [r for r in recs if r.action == action.lower()]

        # Sort by created_at descending
        recs.sort(key=lambda x: x.created_at, reverse=True)

        return {
            "recommendations": recs[:limit],
            "total": len(recs)
        }

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/recommendations/{rec_id}", response_model=RecommendationResponse)
async def get_recommendation(rec_id: str):
    """Get a specific recommendation by ID"""
    if rec_id not in recommendations_store:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return recommendations_store[rec_id]


@app.post("/ai/recommendations/{rec_id}/approve")
async def approve_recommendation(rec_id: str, approval: RecommendationApproval):
    """
    Approve or reject a recommendation

    Args:
        rec_id: Recommendation ID
        approval: Approval decision

    Returns:
        Success message and execution details
    """
    try:
        if rec_id not in recommendations_store:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        recommendation = recommendations_store[rec_id]

        if not approval.approved:
            return {
                "success": True,
                "message": "Recommendation rejected",
                "recommendation_id": rec_id
            }

        # TODO: Implement actual trade execution
        # This will be implemented in Phase 3 (Automation)
        return {
            "success": True,
            "message": "Recommendation approved. Trade execution will be implemented in Phase 3.",
            "recommendation_id": rec_id,
            "symbol": recommendation.symbol,
            "action": recommendation.action,
            "quantity": approval.quantity,
            "notes": approval.notes,
            "warning": "Manual execution required - automated trading not yet implemented"
        }

    except Exception as e:
        logger.error(f"Error approving recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/config", response_model=AIConfigResponse)
async def get_ai_config():
    """Get current AI configuration"""
    return ai_config


@app.put("/ai/config", response_model=AIConfigResponse)
async def update_ai_config(config_update: AIConfigUpdate):
    """
    Update AI configuration

    Args:
        config_update: AI configuration updates

    Returns:
        Updated AI configuration
    """
    try:
        global ai_config

        # Update only provided fields
        update_data = config_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ai_config, field, value)

        logger.info(f"AI config updated: {update_data}")

        return ai_config

    except Exception as e:
        logger.error(f"Error updating AI config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/technical-indicators/{symbol}")
async def get_technical_indicators(symbol: str, exchange: str = "NSE"):
    """
    Get technical indicators for a stock

    Args:
        symbol: Stock symbol
        exchange: Exchange (NSE, BSE, NYSE, NASDAQ)

    Returns:
        Technical indicators and signals
    """
    try:
        # Fetch historical data
        historical_data = await market_data.get_historical_data(
            symbol, exchange, period="6mo"
        )

        if historical_data is None or historical_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for {symbol}"
            )

        # Calculate indicators
        indicators_data = technical_indicators.get_all_indicators(historical_data)

        return {
            "symbol": symbol,
            "exchange": exchange,
            **indicators_data
        }

    except Exception as e:
        logger.error(f"Error getting technical indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/market-analysis")
async def get_market_analysis():
    """
    Get overall market analysis

    Returns:
        Market sentiment, trends, and top recommendations
    """
    try:
        # Get market indices
        indices = await market_data.get_market_indices()

        # Calculate market sentiment
        positive_count = sum(1 for idx in indices.values() if idx.get('change_percent', 0) > 0)
        total_count = len(indices)

        overall_sentiment = "positive" if positive_count > total_count / 2 else "negative" if positive_count < total_count / 2 else "neutral"

        # Calculate average volatility
        avg_change = sum(abs(idx.get('change_percent', 0)) for idx in indices.values()) / total_count if total_count > 0 else 0
        volatility = "high" if avg_change > 2 else "moderate" if avg_change > 1 else "low"

        # Get recent recommendations
        recent_recs = list(recommendations_store.values())
        recent_recs.sort(key=lambda x: x.created_at, reverse=True)
        top_recommendations = recent_recs[:5]

        return {
            "overall_sentiment": overall_sentiment,
            "market_trend": "bullish" if overall_sentiment == "positive" else "bearish" if overall_sentiment == "negative" else "sideways",
            "volatility_index": volatility,
            "market_indices": indices,
            "top_recommendations": top_recommendations,
            "market_summary": f"Market showing {overall_sentiment} sentiment with {volatility} volatility",
            "analyzed_at": datetime.now()
        }

    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/portfolio-suggestions")
async def get_portfolio_suggestions():
    """
    Get AI suggestions for current portfolio holdings

    Returns:
        Recommendations for each holding (hold, add more, reduce, exit)
    """
    try:
        # Get current portfolio
        portfolio = await get_combined_portfolio()

        suggestions = []

        # Analyze each holding
        for holding in portfolio.holdings[:10]:  # Limit to top 10 for performance
            symbol = holding.get('symbol', '')

            if not symbol:
                continue

            try:
                # Analyze stock
                recommendation = await recommendation_engine.analyze_stock(
                    symbol=symbol,
                    exchange="NSE" if ".NS" not in symbol else "NSE",
                    portfolio_context=holding
                )

                suggestions.append({
                    "symbol": symbol,
                    "current_quantity": holding.get('quantity', 0),
                    "current_value": holding.get('current_value', 0),
                    "pnl": holding.get('pnl', 0),
                    "recommendation": recommendation.action.value,
                    "confidence": recommendation.confidence,
                    "reasoning": recommendation.reasoning[:200] + "..." if len(recommendation.reasoning) > 200 else recommendation.reasoning
                })

            except Exception as e:
                logger.warning(f"Could not analyze {symbol}: {e}")
                continue

        return {
            "suggestions": suggestions,
            "analyzed_count": len(suggestions),
            "total_holdings": len(portfolio.holdings),
            "generated_at": datetime.now()
        }

    except Exception as e:
        logger.error(f"Error generating portfolio suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )

