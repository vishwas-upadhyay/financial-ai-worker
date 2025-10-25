"""
AI Data Models
Pydantic models for AI recommendations and configuration
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class RecommendationAction(str, Enum):
    """Recommendation action types"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class TimeHorizon(str, Enum):
    """Investment time horizon"""
    SHORT = "short"  # 1-3 months
    MEDIUM = "medium"  # 3-12 months
    LONG = "long"  # 1+ years


class RiskTolerance(str, Enum):
    """User risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class AutomationLevel(str, Enum):
    """Trading automation levels"""
    MANUAL = "manual"  # All trades require manual approval
    SEMI_AUTO = "semi_auto"  # Some trades auto-execute based on rules
    FULL_AUTO = "full_auto"  # All recommended trades auto-execute


class RecommendationResponse(BaseModel):
    """AI recommendation response"""
    id: Optional[str] = None
    symbol: str
    exchange: str = "NSE"
    action: RecommendationAction
    confidence: float = Field(ge=0, le=100, description="Confidence score 0-100")
    current_price: float
    target_price: float
    stop_loss: float
    time_horizon: TimeHorizon
    reasoning: str
    technical_score: float = Field(ge=-1, le=1)
    sentiment_score: float = Field(ge=-1, le=1)
    ai_score: float = Field(ge=-1, le=1)
    key_points: List[str] = []
    risks: List[str] = []
    opportunities: List[str] = []
    created_at: datetime
    executed: bool = False
    executed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "INFY",
                "exchange": "NSE",
                "action": "buy",
                "confidence": 75.5,
                "current_price": 1525.40,
                "target_price": 1680.00,
                "stop_loss": 1450.00,
                "time_horizon": "medium",
                "reasoning": "Strong technical indicators with positive sentiment",
                "technical_score": 0.65,
                "sentiment_score": 0.45,
                "ai_score": 0.70,
                "key_points": [
                    "RSI showing oversold conditions",
                    "MACD bullish crossover",
                    "Positive earnings sentiment"
                ],
                "risks": [
                    "Market volatility",
                    "Sector headwinds"
                ],
                "opportunities": [
                    "Strong growth potential",
                    "Undervalued relative to peers"
                ]
            }
        }


class AIConfigResponse(BaseModel):
    """AI configuration response"""
    enabled: bool = False
    risk_tolerance: RiskTolerance = RiskTolerance.MODERATE
    automation_level: AutomationLevel = AutomationLevel.MANUAL
    daily_trade_limit: int = Field(default=5, ge=0, le=50)
    max_position_size_percent: float = Field(default=10.0, ge=1.0, le=50.0)
    max_portfolio_allocation_percent: float = Field(default=80.0, ge=10.0, le=100.0)
    enable_stop_loss: bool = True
    enable_take_profit: bool = True
    preferred_sectors: List[str] = []
    excluded_sectors: List[str] = []
    min_confidence_threshold: float = Field(default=60.0, ge=0, le=100)
    use_llm: bool = True
    llm_provider: str = "anthropic"  # "anthropic" or "openai"

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "risk_tolerance": "moderate",
                "automation_level": "semi_auto",
                "daily_trade_limit": 5,
                "max_position_size_percent": 10.0,
                "max_portfolio_allocation_percent": 80.0,
                "enable_stop_loss": True,
                "enable_take_profit": True,
                "preferred_sectors": ["Technology", "Finance"],
                "excluded_sectors": ["Tobacco"],
                "min_confidence_threshold": 65.0,
                "use_llm": True,
                "llm_provider": "anthropic"
            }
        }


class AIConfigUpdate(BaseModel):
    """AI configuration update request"""
    enabled: Optional[bool] = None
    risk_tolerance: Optional[RiskTolerance] = None
    automation_level: Optional[AutomationLevel] = None
    daily_trade_limit: Optional[int] = Field(default=None, ge=0, le=50)
    max_position_size_percent: Optional[float] = Field(default=None, ge=1.0, le=50.0)
    max_portfolio_allocation_percent: Optional[float] = Field(default=None, ge=10.0, le=100.0)
    enable_stop_loss: Optional[bool] = None
    enable_take_profit: Optional[bool] = None
    preferred_sectors: Optional[List[str]] = None
    excluded_sectors: Optional[List[str]] = None
    min_confidence_threshold: Optional[float] = Field(default=None, ge=0, le=100)
    use_llm: Optional[bool] = None
    llm_provider: Optional[str] = None


class StockAnalysisRequest(BaseModel):
    """Request for stock analysis"""
    symbol: str
    exchange: str = "NSE"
    include_portfolio_context: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "INFY",
                "exchange": "NSE",
                "include_portfolio_context": True
            }
        }


class MarketAnalysisResponse(BaseModel):
    """Market analysis response"""
    overall_sentiment: str
    market_trend: str
    volatility_index: str
    top_recommendations: List[RecommendationResponse] = []
    market_summary: str
    analyzed_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "overall_sentiment": "positive",
                "market_trend": "bullish",
                "volatility_index": "moderate",
                "market_summary": "Market showing positive momentum with moderate volatility",
                "analyzed_at": "2025-10-25T10:30:00"
            }
        }


class TechnicalIndicatorsResponse(BaseModel):
    """Technical indicators response"""
    symbol: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_20: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    atr: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    signals: Dict = {}

    class Config:
        from typing import Dict
        json_schema_extra = {
            "example": {
                "symbol": "INFY",
                "rsi": 45.5,
                "macd": 2.3,
                "macd_signal": 1.8,
                "sma_50": 1520.0,
                "sma_200": 1480.0,
                "signals": {
                    "rsi": {
                        "signal": "neutral",
                        "description": "RSI at 45.5 - Neutral range"
                    }
                }
            }
        }


class AIPerformanceResponse(BaseModel):
    """AI trading performance metrics"""
    total_recommendations: int
    executed_trades: int
    win_rate: float = Field(ge=0, le=100)
    average_return: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    best_trade: Optional[Dict] = None
    worst_trade: Optional[Dict] = None
    by_action: Dict = {}
    period_start: datetime
    period_end: datetime

    class Config:
        from typing import Dict
        json_schema_extra = {
            "example": {
                "total_recommendations": 50,
                "executed_trades": 30,
                "win_rate": 65.5,
                "average_return": 3.2,
                "total_return": 15.8,
                "sharpe_ratio": 1.45,
                "max_drawdown": -5.2,
                "period_start": "2025-01-01T00:00:00",
                "period_end": "2025-10-25T00:00:00"
            }
        }


class RecommendationApproval(BaseModel):
    """Approve/reject recommendation"""
    approved: bool
    quantity: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "approved": True,
                "quantity": 10,
                "notes": "Approved for execution"
            }
        }
