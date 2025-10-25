"""
Recommendation Engine
Combines all AI components to generate investment recommendations
"""
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from enum import Enum
from dataclasses import dataclass

from src.ai.market_data_aggregator import market_data
from src.ai.technical_indicators import technical_indicators, Signal
from src.ai.sentiment_analyzer import sentiment_analyzer
from src.ai.llm_advisor import llm_advisor

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Recommendation types"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class Recommendation:
    """Stock recommendation"""
    symbol: str
    action: RecommendationType
    confidence: float  # 0-100
    current_price: float
    target_price: float
    stop_loss: float
    time_horizon: str
    reasoning: str
    technical_score: float
    sentiment_score: float
    ai_score: float
    key_points: List[str]
    risks: List[str]
    opportunities: List[str]
    created_at: datetime


class RecommendationEngine:
    """Generate comprehensive investment recommendations"""

    def __init__(self):
        self.weights = {
            'technical': 0.4,
            'sentiment': 0.2,
            'ai': 0.4
        }

    async def analyze_stock(
        self,
        symbol: str,
        exchange: str = "NSE",
        portfolio_context: Optional[Dict] = None
    ) -> Recommendation:
        """
        Generate comprehensive stock recommendation

        Args:
            symbol: Stock symbol
            exchange: Exchange (NSE, BSE, NYSE, NASDAQ)
            portfolio_context: Current portfolio holding information

        Returns:
            Recommendation object
        """
        try:
            logger.info(f"Analyzing stock {symbol} on {exchange}")

            # Step 1: Gather market data
            logger.debug("Fetching market data...")
            market_info_task = market_data.get_market_info(symbol, exchange)
            historical_data_task = market_data.get_historical_data(symbol, exchange, period="6mo")
            news_task = market_data.get_news_sentiment(symbol, exchange)

            market_info, historical_data, news = await asyncio.gather(
                market_info_task,
                historical_data_task,
                news_task,
                return_exceptions=True
            )

            if isinstance(market_info, Exception):
                logger.error(f"Error fetching market info: {market_info}")
                market_info = {'symbol': symbol, 'current_price': 0}

            if isinstance(historical_data, Exception):
                logger.error(f"Error fetching historical data: {historical_data}")
                historical_data = None

            if isinstance(news, Exception):
                logger.error(f"Error fetching news: {news}")
                news = []

            # Step 2: Calculate technical indicators
            logger.debug("Calculating technical indicators...")
            technical_analysis = {}
            if historical_data is not None and not historical_data.empty:
                technical_analysis = technical_indicators.get_all_indicators(historical_data)
            else:
                logger.warning(f"No historical data available for {symbol}, skipping technical analysis")
                technical_analysis = {'indicators': {}, 'signals': {}}

            # Step 3: Analyze sentiment
            logger.debug("Analyzing sentiment...")
            sentiment_result = await sentiment_analyzer.analyze_news_sentiment(news)

            # Step 4: Get AI recommendation (if available)
            logger.debug("Getting AI recommendation...")
            ai_analysis = {}
            if llm_advisor:
                try:
                    ai_analysis = await llm_advisor.analyze_stock(
                        symbol=symbol,
                        market_data=market_info,
                        technical_indicators=technical_analysis,
                        sentiment_data={
                            'category': sentiment_result.category.value,
                            'score': sentiment_result.score,
                            'summary': sentiment_result.summary,
                            'news_count': sentiment_result.news_count
                        },
                        portfolio_context=portfolio_context
                    )
                except Exception as e:
                    logger.error(f"Error getting AI analysis: {e}")
                    ai_analysis = {
                        'recommendation': 'HOLD',
                        'confidence': 50,
                        'analysis': 'AI analysis unavailable'
                    }
            else:
                ai_analysis = {
                    'recommendation': 'HOLD',
                    'confidence': 50,
                    'analysis': 'LLM advisor not configured'
                }

            # Step 5: Combine all analyses
            logger.debug("Combining analyses...")
            recommendation = self._combine_analyses(
                symbol=symbol,
                market_info=market_info,
                technical_analysis=technical_analysis,
                sentiment_result=sentiment_result,
                ai_analysis=ai_analysis,
                portfolio_context=portfolio_context
            )

            logger.info(f"Recommendation for {symbol}: {recommendation.action.value} (confidence: {recommendation.confidence}%)")
            return recommendation

        except Exception as e:
            logger.error(f"Error analyzing stock {symbol}: {e}", exc_info=True)
            # Return safe fallback recommendation
            return Recommendation(
                symbol=symbol,
                action=RecommendationType.HOLD,
                confidence=0,
                current_price=0,
                target_price=0,
                stop_loss=0,
                time_horizon="medium",
                reasoning=f"Error in analysis: {str(e)}",
                technical_score=0,
                sentiment_score=0,
                ai_score=0,
                key_points=["Analysis error"],
                risks=["Unable to complete analysis"],
                opportunities=[],
                created_at=datetime.now()
            )

    def _combine_analyses(
        self,
        symbol: str,
        market_info: Dict,
        technical_analysis: Dict,
        sentiment_result,
        ai_analysis: Dict,
        portfolio_context: Optional[Dict]
    ) -> Recommendation:
        """Combine all analysis components into final recommendation"""

        # Extract current price
        current_price = market_info.get('current_price', 0)

        # Calculate technical score
        technical_score = self._calculate_technical_score(technical_analysis.get('signals', {}))

        # Calculate sentiment score
        sentiment_score = sentiment_result.score

        # Calculate AI score
        ai_score = self._calculate_ai_score(ai_analysis.get('recommendation', 'HOLD'))

        # Weighted combined score
        combined_score = (
            technical_score * self.weights['technical'] +
            sentiment_score * self.weights['sentiment'] +
            ai_score * self.weights['ai']
        )

        # Determine recommendation type
        action = self._score_to_recommendation(combined_score)

        # Calculate confidence
        confidence = self._calculate_confidence(
            technical_analysis,
            sentiment_result,
            ai_analysis
        )

        # Determine target price and stop loss
        target_price = ai_analysis.get('target_price', 0)
        stop_loss = ai_analysis.get('stop_loss', 0)

        if not target_price and current_price:
            # Fallback target price calculation
            if action in [RecommendationType.STRONG_BUY, RecommendationType.BUY]:
                target_price = current_price * 1.15  # 15% upside
                stop_loss = current_price * 0.95     # 5% downside
            elif action in [RecommendationType.STRONG_SELL, RecommendationType.SELL]:
                target_price = current_price * 0.85  # 15% downside
                stop_loss = current_price * 1.05     # 5% upside protection
            else:
                target_price = current_price
                stop_loss = current_price * 0.95

        # Build reasoning
        reasoning = self._build_reasoning(
            technical_analysis,
            sentiment_result,
            ai_analysis,
            action
        )

        # Extract key points, risks, opportunities
        key_points = ai_analysis.get('key_points', [])
        if not key_points:
            key_points = self._generate_key_points(technical_analysis, sentiment_result)

        risks = ai_analysis.get('risks', [])
        if not risks:
            risks = ["Market volatility", "Sector-specific risks"]

        opportunities = ai_analysis.get('opportunities', [])
        if not opportunities:
            opportunities = self._generate_opportunities(action, technical_analysis)

        return Recommendation(
            symbol=symbol,
            action=action,
            confidence=confidence,
            current_price=current_price,
            target_price=target_price,
            stop_loss=stop_loss,
            time_horizon=ai_analysis.get('time_horizon', 'medium'),
            reasoning=reasoning,
            technical_score=technical_score,
            sentiment_score=sentiment_score,
            ai_score=ai_score,
            key_points=key_points,
            risks=risks,
            opportunities=opportunities,
            created_at=datetime.now()
        )

    def _calculate_technical_score(self, signals: Dict) -> float:
        """Calculate technical analysis score (-1 to 1)"""
        signal_values = {
            'strong_buy': 1.0,
            'buy': 0.5,
            'neutral': 0.0,
            'sell': -0.5,
            'strong_sell': -1.0
        }

        total_score = 0
        count = 0

        for signal_name, signal_data in signals.items():
            if isinstance(signal_data, dict) and 'signal' in signal_data:
                signal = signal_data['signal']
                confidence = signal_data.get('confidence', 50) / 100

                score = signal_values.get(signal, 0) * confidence
                total_score += score
                count += 1

        return total_score / count if count > 0 else 0

    def _calculate_ai_score(self, recommendation: str) -> float:
        """Convert AI recommendation to score (-1 to 1)"""
        scores = {
            'STRONG_BUY': 1.0,
            'BUY': 0.5,
            'HOLD': 0.0,
            'SELL': -0.5,
            'STRONG_SELL': -1.0
        }
        return scores.get(recommendation.upper(), 0)

    def _score_to_recommendation(self, score: float) -> RecommendationType:
        """Convert combined score to recommendation type"""
        if score >= 0.6:
            return RecommendationType.STRONG_BUY
        elif score >= 0.2:
            return RecommendationType.BUY
        elif score <= -0.6:
            return RecommendationType.STRONG_SELL
        elif score <= -0.2:
            return RecommendationType.SELL
        else:
            return RecommendationType.HOLD

    def _calculate_confidence(
        self,
        technical_analysis: Dict,
        sentiment_result,
        ai_analysis: Dict
    ) -> float:
        """Calculate overall confidence score (0-100)"""
        confidences = []

        # Technical confidence
        signals = technical_analysis.get('signals', {})
        if signals:
            tech_confidences = [
                s.get('confidence', 50)
                for s in signals.values()
                if isinstance(s, dict) and 'confidence' in s
            ]
            if tech_confidences:
                confidences.append(sum(tech_confidences) / len(tech_confidences))

        # Sentiment confidence
        if sentiment_result:
            confidences.append(sentiment_result.confidence)

        # AI confidence
        if ai_analysis.get('confidence'):
            confidences.append(ai_analysis['confidence'])

        # Calculate weighted average
        if confidences:
            return sum(confidences) / len(confidences)
        return 50

    def _build_reasoning(
        self,
        technical_analysis: Dict,
        sentiment_result,
        ai_analysis: Dict,
        action: RecommendationType
    ) -> str:
        """Build comprehensive reasoning for recommendation"""
        parts = []

        # AI reasoning
        if ai_analysis.get('analysis'):
            parts.append(ai_analysis['analysis'])

        # Technical reasoning
        signals = technical_analysis.get('signals', {})
        if signals:
            signal_summaries = [
                s.get('description', '')
                for s in signals.values()
                if isinstance(s, dict) and s.get('description')
            ]
            if signal_summaries:
                parts.append("Technical analysis shows: " + "; ".join(signal_summaries[:3]))

        # Sentiment reasoning
        if sentiment_result:
            parts.append(f"Market sentiment: {sentiment_result.summary}")

        return " | ".join(parts) if parts else f"Recommendation: {action.value}"

    def _generate_key_points(self, technical_analysis: Dict, sentiment_result) -> List[str]:
        """Generate key points from analysis"""
        points = []

        # Technical points
        signals = technical_analysis.get('signals', {})
        for name, signal in signals.items():
            if isinstance(signal, dict) and signal.get('signal') in ['strong_buy', 'buy', 'strong_sell', 'sell']:
                points.append(f"{name.replace('_', ' ').title()}: {signal.get('description', '')}")

        # Sentiment point
        if sentiment_result and sentiment_result.category.value != 'neutral':
            points.append(f"Sentiment: {sentiment_result.summary}")

        return points[:5]  # Max 5 points

    def _generate_opportunities(self, action: RecommendationType, technical_analysis: Dict) -> List[str]:
        """Generate opportunity list based on recommendation"""
        if action in [RecommendationType.STRONG_BUY, RecommendationType.BUY]:
            return [
                "Potential price appreciation based on technical indicators",
                "Favorable entry point based on current analysis"
            ]
        elif action in [RecommendationType.STRONG_SELL, RecommendationType.SELL]:
            return [
                "Opportunity to take profits at current levels",
                "Reallocation to better opportunities"
            ]
        return ["Monitor for better entry/exit points"]


# Global instance
recommendation_engine = RecommendationEngine()
