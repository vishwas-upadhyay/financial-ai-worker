"""
Portfolio Analysis Engine
Comprehensive portfolio analysis and risk assessment
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
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


@dataclass
class AssetAllocation:
    """Asset allocation breakdown"""
    equity: float
    debt: float
    commodities: float
    forex: float
    crypto: float
    others: float


class PortfolioAnalyzer:
    """Advanced portfolio analysis engine"""
    
    def __init__(self):
        self.risk_free_rate = 0.05  # 5% risk-free rate
        self.market_return = 0.12   # 12% expected market return
        
    def analyze_portfolio(
        self, 
        holdings: List[Dict], 
        historical_data: pd.DataFrame = None
    ) -> PortfolioMetrics:
        """Comprehensive portfolio analysis"""
        try:
            # Calculate basic metrics
            total_value = sum(holding.get('current_value', 0) for holding in holdings)
            total_investment = sum(holding.get('invested_value', 0) for holding in holdings)
            total_pnl = total_value - total_investment
            total_pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0
            
            # Calculate day P&L
            day_pnl = sum(holding.get('day_pnl', 0) for holding in holdings)
            day_pnl_percentage = (day_pnl / total_value * 100) if total_value > 0 else 0
            
            # Calculate risk metrics
            volatility = self._calculate_volatility(holdings, historical_data)
            sharpe_ratio = self._calculate_sharpe_ratio(total_pnl_percentage, volatility)
            max_drawdown = self._calculate_max_drawdown(holdings, historical_data)
            beta = self._calculate_beta(holdings, historical_data)
            alpha = self._calculate_alpha(total_pnl_percentage, beta)
            
            # Calculate diversification metrics
            diversification_ratio = self._calculate_diversification_ratio(holdings)
            concentration_risk = self._calculate_concentration_risk(holdings)
            
            # Determine risk level
            risk_level = self._determine_risk_level(volatility, concentration_risk, max_drawdown)
            
            return PortfolioMetrics(
                total_value=total_value,
                total_pnl=total_pnl,
                total_pnl_percentage=total_pnl_percentage,
                day_pnl=day_pnl,
                day_pnl_percentage=day_pnl_percentage,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                volatility=volatility,
                beta=beta,
                alpha=alpha,
                risk_level=risk_level,
                diversification_ratio=diversification_ratio,
                concentration_risk=concentration_risk
            )
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            raise
    
    def _calculate_volatility(self, holdings: List[Dict], historical_data: pd.DataFrame = None) -> float:
        """Calculate portfolio volatility"""
        if not historical_data or historical_data.empty:
            # Use individual stock volatilities weighted by portfolio allocation
            total_value = sum(holding.get('current_value', 0) for holding in holdings)
            weighted_volatility = 0
            
            for holding in holdings:
                weight = holding.get('current_value', 0) / total_value if total_value > 0 else 0
                # Assume 20% volatility for individual stocks (can be improved with actual data)
                stock_volatility = holding.get('volatility', 0.20)
                weighted_volatility += weight * stock_volatility
                
            return weighted_volatility
        
        # Calculate portfolio returns
        portfolio_returns = self._calculate_portfolio_returns(holdings, historical_data)
        return portfolio_returns.std() * np.sqrt(252)  # Annualized volatility
    
    def _calculate_sharpe_ratio(self, portfolio_return: float, volatility: float) -> float:
        """Calculate Sharpe ratio"""
        if volatility == 0:
            return 0
        return (portfolio_return - self.risk_free_rate) / volatility
    
    def _calculate_max_drawdown(self, holdings: List[Dict], historical_data: pd.DataFrame = None) -> float:
        """Calculate maximum drawdown"""
        if not historical_data or historical_data.empty:
            # Estimate based on individual holdings
            max_dd = 0
            for holding in holdings:
                # Assume max drawdown is 30% of volatility
                stock_volatility = holding.get('volatility', 0.20)
                max_dd = max(max_dd, stock_volatility * 1.5)
            return max_dd
        
        # Calculate rolling maximum and drawdown
        portfolio_returns = self._calculate_portfolio_returns(holdings, historical_data)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        return abs(drawdown.min())
    
    def _calculate_beta(self, holdings: List[Dict], historical_data: pd.DataFrame = None) -> float:
        """Calculate portfolio beta"""
        if not historical_data or historical_data.empty:
            # Estimate beta based on sector allocation
            total_value = sum(holding.get('current_value', 0) for holding in holdings)
            weighted_beta = 0
            
            for holding in holdings:
                weight = holding.get('current_value', 0) / total_value if total_value > 0 else 0
                # Assume beta of 1.0 for individual stocks (can be improved with actual data)
                stock_beta = holding.get('beta', 1.0)
                weighted_beta += weight * stock_beta
                
            return weighted_beta
        
        # Calculate beta using regression
        portfolio_returns = self._calculate_portfolio_returns(holdings, historical_data)
        market_returns = historical_data['market_return']  # Assuming market return column exists
        
        if len(portfolio_returns) != len(market_returns):
            return 1.0  # Default beta
        
        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        return covariance / market_variance if market_variance > 0 else 1.0
    
    def _calculate_alpha(self, portfolio_return: float, beta: float) -> float:
        """Calculate portfolio alpha"""
        expected_return = self.risk_free_rate + beta * (self.market_return - self.risk_free_rate)
        return portfolio_return - expected_return
    
    def _calculate_diversification_ratio(self, holdings: List[Dict]) -> float:
        """Calculate diversification ratio"""
        if len(holdings) <= 1:
            return 0.0
        
        total_value = sum(holding.get('current_value', 0) for holding in holdings)
        if total_value == 0:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        weights = [holding.get('current_value', 0) / total_value for holding in holdings]
        hhi = sum(w**2 for w in weights)
        
        # Convert to diversification ratio (1 - HHI)
        return 1 - hhi
    
    def _calculate_concentration_risk(self, holdings: List[Dict]) -> float:
        """Calculate concentration risk"""
        if not holdings:
            return 0.0
        
        total_value = sum(holding.get('current_value', 0) for holding in holdings)
        if total_value == 0:
            return 0.0
        
        # Calculate the weight of the largest holding
        weights = [holding.get('current_value', 0) / total_value for holding in holdings]
        max_weight = max(weights)
        
        # Concentration risk is the percentage of the largest holding
        return max_weight
    
    def _determine_risk_level(
        self, 
        volatility: float, 
        concentration_risk: float, 
        max_drawdown: float
    ) -> RiskLevel:
        """Determine portfolio risk level"""
        risk_score = 0
        
        # Volatility scoring
        if volatility < 0.15:
            risk_score += 1
        elif volatility < 0.25:
            risk_score += 2
        elif volatility < 0.35:
            risk_score += 3
        else:
            risk_score += 4
        
        # Concentration risk scoring
        if concentration_risk < 0.2:
            risk_score += 1
        elif concentration_risk < 0.4:
            risk_score += 2
        elif concentration_risk < 0.6:
            risk_score += 3
        else:
            risk_score += 4
        
        # Drawdown scoring
        if max_drawdown < 0.1:
            risk_score += 1
        elif max_drawdown < 0.2:
            risk_score += 2
        elif max_drawdown < 0.3:
            risk_score += 3
        else:
            risk_score += 4
        
        # Determine risk level
        if risk_score <= 3:
            return RiskLevel.LOW
        elif risk_score <= 6:
            return RiskLevel.MEDIUM
        elif risk_score <= 9:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _calculate_portfolio_returns(self, holdings: List[Dict], historical_data: pd.DataFrame) -> pd.Series:
        """Calculate portfolio returns from historical data"""
        # This is a simplified implementation
        # In practice, you would calculate weighted returns based on holdings
        if 'portfolio_return' in historical_data.columns:
            return historical_data['portfolio_return']
        
        # Fallback: use market returns
        if 'market_return' in historical_data.columns:
            return historical_data['market_return']
        
        # Default: generate random returns for demonstration
        return pd.Series(np.random.normal(0.001, 0.02, len(historical_data)))
    
    def get_asset_allocation(self, holdings: List[Dict]) -> AssetAllocation:
        """Get asset allocation breakdown"""
        total_value = sum(holding.get('current_value', 0) for holding in holdings)
        if total_value == 0:
            return AssetAllocation(0, 0, 0, 0, 0, 0)
        
        equity = 0
        debt = 0
        commodities = 0
        forex = 0
        crypto = 0
        others = 0
        
        for holding in holdings:
            weight = holding.get('current_value', 0) / total_value
            asset_type = holding.get('asset_type', 'equity').lower()
            
            if asset_type in ['equity', 'stock', 'shares']:
                equity += weight
            elif asset_type in ['debt', 'bond', 'fixed_income']:
                debt += weight
            elif asset_type in ['commodity', 'gold', 'silver', 'oil']:
                commodities += weight
            elif asset_type in ['forex', 'currency']:
                forex += weight
            elif asset_type in ['crypto', 'cryptocurrency', 'bitcoin']:
                crypto += weight
            else:
                others += weight
        
        return AssetAllocation(
            equity=equity * 100,
            debt=debt * 100,
            commodities=commodities * 100,
            forex=forex * 100,
            crypto=crypto * 100,
            others=others * 100
        )
    
    def generate_recommendations(self, metrics: PortfolioMetrics) -> List[str]:
        """Generate portfolio recommendations based on analysis"""
        recommendations = []
        
        # Risk-based recommendations
        if metrics.risk_level == RiskLevel.VERY_HIGH:
            recommendations.append("Portfolio risk is very high. Consider diversifying holdings.")
        elif metrics.risk_level == RiskLevel.HIGH:
            recommendations.append("Portfolio risk is high. Consider reducing position sizes.")
        
        # Concentration risk recommendations
        if metrics.concentration_risk > 0.4:
            recommendations.append("High concentration risk detected. Consider spreading investments across more assets.")
        
        # Diversification recommendations
        if metrics.diversification_ratio < 0.3:
            recommendations.append("Low diversification. Consider adding assets from different sectors.")
        
        # Performance recommendations
        if metrics.sharpe_ratio < 0.5:
            recommendations.append("Low risk-adjusted returns. Consider rebalancing portfolio.")
        
        if metrics.alpha < -0.05:
            recommendations.append("Negative alpha. Consider reviewing investment strategy.")
        
        # Volatility recommendations
        if metrics.volatility > 0.3:
            recommendations.append("High volatility detected. Consider adding defensive assets.")
        
        return recommendations

