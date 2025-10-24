"""
Data Visualization Components
Interactive charts and graphs for portfolio analysis
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate interactive charts for portfolio analysis"""
    
    def __init__(self):
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def create_portfolio_value_chart(
        self, 
        historical_data: pd.DataFrame,
        title: str = "Portfolio Value Over Time"
    ) -> go.Figure:
        """Create portfolio value chart over time"""
        try:
            fig = go.Figure()
            
            # Add portfolio value line
            fig.add_trace(go.Scatter(
                x=historical_data.index,
                y=historical_data['portfolio_value'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # Add investment line
            if 'investment' in historical_data.columns:
                fig.add_trace(go.Scatter(
                    x=historical_data.index,
                    y=historical_data['investment'],
                    mode='lines',
                    name='Total Investment',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Value",
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating portfolio value chart: {e}")
            raise
    
    def create_pnl_chart(
        self, 
        historical_data: pd.DataFrame,
        title: str = "P&L Over Time"
    ) -> go.Figure:
        """Create P&L chart over time"""
        try:
            fig = go.Figure()
            
            # Add P&L line
            fig.add_trace(go.Scatter(
                x=historical_data.index,
                y=historical_data['pnl'],
                mode='lines',
                name='P&L',
                line=dict(color='#2ca02c', width=2),
                fill='tonexty'
            ))
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="P&L",
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating P&L chart: {e}")
            raise
    
    def create_asset_allocation_pie_chart(
        self, 
        allocation_data: Dict[str, float],
        title: str = "Asset Allocation"
    ) -> go.Figure:
        """Create asset allocation pie chart"""
        try:
            # Filter out zero values
            filtered_data = {k: v for k, v in allocation_data.items() if v > 0}
            
            if not filtered_data:
                # Create empty chart
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            labels = list(filtered_data.keys())
            values = list(filtered_data.values())
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.3,
                marker_colors=self.color_palette[:len(labels)]
            )])
            
            fig.update_layout(
                title=title,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating asset allocation chart: {e}")
            raise
    
    def create_sector_allocation_chart(
        self, 
        holdings_data: List[Dict],
        title: str = "Sector Allocation"
    ) -> go.Figure:
        """Create sector allocation chart"""
        try:
            # Group by sector
            sector_data = {}
            for holding in holdings_data:
                sector = holding.get('sector', 'Unknown')
                value = holding.get('current_value', 0)
                sector_data[sector] = sector_data.get(sector, 0) + value
            
            # Filter out zero values
            filtered_data = {k: v for k, v in sector_data.items() if v > 0}
            
            if not filtered_data:
                fig = go.Figure()
                fig.add_annotation(
                    text="No sector data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            labels = list(filtered_data.keys())
            values = list(filtered_data.values())
            
            fig = go.Figure(data=[go.Bar(
                x=labels,
                y=values,
                marker_color=self.color_palette[:len(labels)]
            )])
            
            fig.update_layout(
                title=title,
                xaxis_title="Sector",
                yaxis_title="Value",
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sector allocation chart: {e}")
            raise
    
    def create_risk_return_scatter(
        self, 
        holdings_data: List[Dict],
        title: str = "Risk vs Return Analysis"
    ) -> go.Figure:
        """Create risk vs return scatter plot"""
        try:
            x_data = []  # Risk (volatility)
            y_data = []  # Return
            text_data = []  # Symbol names
            size_data = []  # Portfolio weight
            
            total_value = sum(holding.get('current_value', 0) for holding in holdings_data)
            
            for holding in holdings_data:
                symbol = holding.get('symbol', 'Unknown')
                value = holding.get('current_value', 0)
                weight = value / total_value if total_value > 0 else 0
                
                # Use default values if not available
                volatility = holding.get('volatility', 0.20)
                return_rate = holding.get('return_rate', 0.10)
                
                x_data.append(volatility)
                y_data.append(return_rate)
                text_data.append(symbol)
                size_data.append(weight * 100)  # Scale for bubble size
            
            fig = go.Figure(data=go.Scatter(
                x=x_data,
                y=y_data,
                mode='markers',
                text=text_data,
                marker=dict(
                    size=size_data,
                    color=y_data,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Return Rate")
                ),
                hovertemplate='<b>%{text}</b><br>' +
                             'Risk: %{x:.2%}<br>' +
                             'Return: %{y:.2%}<br>' +
                             'Weight: %{marker.size:.1f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Risk (Volatility)",
                yaxis_title="Return Rate",
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating risk-return scatter plot: {e}")
            raise
    
    def create_performance_comparison(
        self, 
        portfolio_data: pd.DataFrame,
        benchmark_data: pd.DataFrame,
        title: str = "Portfolio vs Benchmark Performance"
    ) -> go.Figure:
        """Create portfolio vs benchmark comparison chart"""
        try:
            fig = go.Figure()
            
            # Add portfolio line
            fig.add_trace(go.Scatter(
                x=portfolio_data.index,
                y=portfolio_data['cumulative_return'],
                mode='lines',
                name='Portfolio',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # Add benchmark line
            fig.add_trace(go.Scatter(
                x=benchmark_data.index,
                y=benchmark_data['cumulative_return'],
                mode='lines',
                name='Benchmark',
                line=dict(color='#ff7f0e', width=2)
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Cumulative Return",
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating performance comparison chart: {e}")
            raise
    
    def create_drawdown_chart(
        self, 
        historical_data: pd.DataFrame,
        title: str = "Portfolio Drawdown"
    ) -> go.Figure:
        """Create drawdown chart"""
        try:
            # Calculate drawdown
            peak = historical_data['portfolio_value'].expanding().max()
            drawdown = (historical_data['portfolio_value'] - peak) / peak * 100
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=historical_data.index,
                y=drawdown,
                mode='lines',
                name='Drawdown',
                line=dict(color='red', width=2),
                fill='tonexty'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Drawdown (%)",
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating drawdown chart: {e}")
            raise
    
    def create_metrics_dashboard(
        self, 
        metrics_data: Dict[str, float],
        title: str = "Portfolio Metrics Dashboard"
    ) -> go.Figure:
        """Create metrics dashboard with key performance indicators"""
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Total Return', 'Sharpe Ratio', 'Max Drawdown', 'Volatility'),
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # Total Return
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=metrics_data.get('total_pnl_percentage', 0),
                title={"text": "Total Return (%)"},
                delta={"reference": 0}
            ), row=1, col=1)
            
            # Sharpe Ratio
            fig.add_trace(go.Indicator(
                mode="number",
                value=metrics_data.get('sharpe_ratio', 0),
                title={"text": "Sharpe Ratio"}
            ), row=1, col=2)
            
            # Max Drawdown
            fig.add_trace(go.Indicator(
                mode="number",
                value=metrics_data.get('max_drawdown', 0),
                title={"text": "Max Drawdown (%)"}
            ), row=2, col=1)
            
            # Volatility
            fig.add_trace(go.Indicator(
                mode="number",
                value=metrics_data.get('volatility', 0),
                title={"text": "Volatility (%)"}
            ), row=2, col=2)
            
            fig.update_layout(
                title=title,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating metrics dashboard: {e}")
            raise
    
    def create_correlation_heatmap(
        self, 
        holdings_data: List[Dict],
        title: str = "Asset Correlation Matrix"
    ) -> go.Figure:
        """Create correlation heatmap for portfolio assets"""
        try:
            # Create correlation matrix
            symbols = [holding.get('symbol') for holding in holdings_data]
            n = len(symbols)
            
            # Generate random correlation matrix for demonstration
            # In practice, you would calculate actual correlations
            correlation_matrix = np.random.rand(n, n)
            correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
            np.fill_diagonal(correlation_matrix, 1)
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix,
                x=symbols,
                y=symbols,
                colorscale='RdBu',
                zmid=0
            ))
            
            fig.update_layout(
                title=title,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating correlation heatmap: {e}")
            raise
    
    def create_top_holdings_chart(
        self, 
        holdings_data: List[Dict],
        top_n: int = 10,
        title: str = "Top Holdings"
    ) -> go.Figure:
        """Create top holdings bar chart"""
        try:
            # Sort by value and take top N
            sorted_holdings = sorted(
                holdings_data, 
                key=lambda x: x.get('current_value', 0), 
                reverse=True
            )[:top_n]
            
            symbols = [h.get('symbol', 'Unknown') for h in sorted_holdings]
            values = [h.get('current_value', 0) for h in sorted_holdings]
            
            fig = go.Figure(data=[go.Bar(
                x=symbols,
                y=values,
                marker_color=self.color_palette[:len(symbols)]
            )])
            
            fig.update_layout(
                title=title,
                xaxis_title="Symbol",
                yaxis_title="Value",
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating top holdings chart: {e}")
            raise

