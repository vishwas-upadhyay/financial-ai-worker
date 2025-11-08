"""
Pydantic models for portfolio data
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class BrokerType(str, Enum):
    """Broker type enumeration"""
    ZERODHA = "zerodha"
    TRADING212 = "trading212"
    COMBINED = "combined"


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"


class ProductType(str, Enum):
    """Product type enumeration"""
    CNC = "CNC"  # Cash and Carry
    MIS = "MIS"  # Intraday
    NRML = "NRML"  # Normal
    BO = "BO"  # Bracket Order
    CO = "CO"  # Cover Order


class VarietyType(str, Enum):
    """Order variety enumeration"""
    REGULAR = "regular"
    BO = "bo"  # Bracket Order
    CO = "co"  # Cover Order
    AMO = "amo"  # After Market Order


class HoldingModel(BaseModel):
    """Individual holding model"""
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    current_value: float
    invested_value: float
    pnl: float
    pnl_percentage: float
    day_pnl: float
    asset_type: str = "equity"


class PortfolioResponse(BaseModel):
    """Portfolio response model"""
    broker: str
    total_value: float
    total_investment: float
    total_pnl: float
    total_pnl_percentage: float
    holdings: List[HoldingModel]
    last_updated: str
    free_cash: Optional[float] = 0.0  # Available cash (only for Trading212)


class OrderRequest(BaseModel):
    """Order request model"""
    broker: str
    symbol: str
    quantity: int
    transaction_type: TransactionType
    order_type: OrderType
    product: ProductType = ProductType.CNC
    variety: VarietyType = VarietyType.REGULAR
    exchange: str = "NSE"
    price: Optional[float] = None
    validity: str = "DAY"


class OrderResponse(BaseModel):
    """Order response model"""
    order_id: Optional[str]
    status: str
    message: str
    timestamp: str


class AnalysisRequest(BaseModel):
    """Portfolio analysis request model"""
    broker: str
    include_recommendations: bool = True
    include_risk_analysis: bool = True


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PortfolioMetricsModel(BaseModel):
    """Portfolio metrics model"""
    total_value: float
    total_pnl: float
    total_pnl_percentage: float
    day_pnl: float
    day_pnl_percentage: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    beta: float
    alpha: float
    risk_level: RiskLevel
    diversification_ratio: float
    concentration_risk: float


class AssetAllocationModel(BaseModel):
    """Asset allocation model"""
    equity: float
    debt: float
    commodities: float
    forex: float
    crypto: float
    others: float


class AnalysisResponse(BaseModel):
    """Portfolio analysis response model"""
    broker: str
    metrics: PortfolioMetricsModel
    asset_allocation: AssetAllocationModel
    recommendations: List[str]
    analysis_date: str


class MarketDataRequest(BaseModel):
    """Market data request model"""
    symbols: List[str]
    broker: str


class MarketDataResponse(BaseModel):
    """Market data response model"""
    broker: str
    data: Dict[str, Dict[str, Any]]
    timestamp: str


class HistoricalDataRequest(BaseModel):
    """Historical data request model"""
    symbol: str
    from_date: str
    to_date: str
    interval: str = "day"
    broker: str


class HistoricalDataResponse(BaseModel):
    """Historical data response model"""
    symbol: str
    data: List[Dict[str, Any]]
    broker: str
    timestamp: str


class AlertRequest(BaseModel):
    """Alert request model"""
    symbol: str
    condition: str  # "price_above", "price_below", "volume_above", etc.
    value: float
    broker: str


class AlertResponse(BaseModel):
    """Alert response model"""
    alert_id: str
    status: str
    message: str
    timestamp: str


class RebalanceRequest(BaseModel):
    """Portfolio rebalancing request model"""
    target_allocation: Dict[str, float]  # symbol -> target_percentage
    broker: str
    tolerance: float = 0.05  # 5% tolerance


class RebalanceResponse(BaseModel):
    """Portfolio rebalancing response model"""
    rebalance_id: str
    orders: List[OrderRequest]
    status: str
    message: str
    timestamp: str

