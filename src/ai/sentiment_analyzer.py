"""
Sentiment Analyzer
Analyzes news and market sentiment for stocks
"""
import asyncio
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SentimentScore(Enum):
    """Sentiment score categories"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class SentimentAnalysis:
    """Result of sentiment analysis"""
    score: float  # -1 to 1
    category: SentimentScore
    confidence: float  # 0-100
    summary: str
    news_count: int


class SentimentAnalyzer:
    """Analyze sentiment from news and social media"""

    def __init__(self):
        self.positive_keywords = [
            'growth', 'profit', 'surge', 'gain', 'rally', 'bullish', 'upgrade',
            'beat', 'exceed', 'strong', 'robust', 'positive', 'momentum', 'breakthrough',
            'innovation', 'expansion', 'record', 'high', 'success', 'optimistic'
        ]

        self.negative_keywords = [
            'loss', 'decline', 'fall', 'drop', 'crash', 'bearish', 'downgrade',
            'miss', 'weak', 'poor', 'negative', 'concern', 'risk', 'warning',
            'lawsuit', 'scandal', 'bankruptcy', 'cut', 'layoff', 'pessimistic'
        ]

    async def analyze_news_sentiment(
        self,
        news_articles: List[Dict]
    ) -> SentimentAnalysis:
        """
        Analyze sentiment from news articles

        Args:
            news_articles: List of news articles with title and content

        Returns:
            SentimentAnalysis result
        """
        try:
            if not news_articles:
                return SentimentAnalysis(
                    score=0.0,
                    category=SentimentScore.NEUTRAL,
                    confidence=0,
                    summary="No news articles available",
                    news_count=0
                )

            total_score = 0
            scored_articles = 0

            for article in news_articles:
                title = article.get('title', '').lower()

                # Simple keyword-based sentiment scoring
                positive_count = sum(1 for word in self.positive_keywords if word in title)
                negative_count = sum(1 for word in self.negative_keywords if word in title)

                if positive_count > 0 or negative_count > 0:
                    article_score = (positive_count - negative_count) / (positive_count + negative_count)
                    total_score += article_score
                    scored_articles += 1

            if scored_articles == 0:
                return SentimentAnalysis(
                    score=0.0,
                    category=SentimentScore.NEUTRAL,
                    confidence=50,
                    summary="Neutral sentiment - no clear signals",
                    news_count=len(news_articles)
                )

            # Calculate average sentiment
            avg_score = total_score / scored_articles

            # Categorize sentiment
            category = self._categorize_sentiment(avg_score)

            # Calculate confidence based on number of articles
            confidence = min(100, 50 + (scored_articles * 10))

            # Generate summary
            summary = self._generate_sentiment_summary(category, scored_articles, len(news_articles))

            return SentimentAnalysis(
                score=avg_score,
                category=category,
                confidence=confidence,
                summary=summary,
                news_count=len(news_articles)
            )

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return SentimentAnalysis(
                score=0.0,
                category=SentimentScore.NEUTRAL,
                confidence=0,
                summary="Error analyzing sentiment",
                news_count=0
            )

    def _categorize_sentiment(self, score: float) -> SentimentScore:
        """Categorize sentiment score"""
        if score >= 0.5:
            return SentimentScore.VERY_POSITIVE
        elif score >= 0.15:
            return SentimentScore.POSITIVE
        elif score <= -0.5:
            return SentimentScore.VERY_NEGATIVE
        elif score <= -0.15:
            return SentimentScore.NEGATIVE
        else:
            return SentimentScore.NEUTRAL

    def _generate_sentiment_summary(
        self,
        category: SentimentScore,
        scored_articles: int,
        total_articles: int
    ) -> str:
        """Generate human-readable sentiment summary"""
        summaries = {
            SentimentScore.VERY_POSITIVE: f"Very positive sentiment across {scored_articles}/{total_articles} news articles",
            SentimentScore.POSITIVE: f"Positive sentiment in recent news ({scored_articles}/{total_articles} articles)",
            SentimentScore.NEUTRAL: f"Neutral sentiment - mixed signals from {scored_articles}/{total_articles} articles",
            SentimentScore.NEGATIVE: f"Negative sentiment detected in {scored_articles}/{total_articles} articles",
            SentimentScore.VERY_NEGATIVE: f"Very negative sentiment across {scored_articles}/{total_articles} news articles"
        }
        return summaries.get(category, "Neutral sentiment")

    async def get_market_sentiment(self) -> Dict[str, str]:
        """
        Get overall market sentiment

        Returns:
            Dictionary with market sentiment indicators
        """
        try:
            # This is a simplified version
            # In production, you would fetch VIX, Put/Call ratio, etc.

            return {
                'overall': 'neutral',
                'volatility': 'moderate',
                'fear_greed_index': 'neutral',
                'description': 'Market showing moderate volatility with mixed signals'
            }

        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return {
                'overall': 'unknown',
                'volatility': 'unknown',
                'fear_greed_index': 'unknown',
                'description': 'Unable to determine market sentiment'
            }

    def combine_sentiments(
        self,
        news_sentiment: SentimentAnalysis,
        technical_signals: Dict
    ) -> Dict:
        """
        Combine news sentiment with technical signals for comprehensive analysis

        Args:
            news_sentiment: Sentiment analysis from news
            technical_signals: Technical indicator signals

        Returns:
            Combined analysis
        """
        try:
            # Weight sentiment and technical signals
            sentiment_weight = 0.3
            technical_weight = 0.7

            # Convert sentiment score to -1 to 1 scale
            sentiment_score = news_sentiment.score

            # Calculate average technical signal
            technical_score = 0
            signal_count = 0

            signal_values = {
                'strong_buy': 1.0,
                'buy': 0.5,
                'neutral': 0.0,
                'sell': -0.5,
                'strong_sell': -1.0
            }

            for signal_name, signal_data in technical_signals.items():
                if isinstance(signal_data, dict) and 'signal' in signal_data:
                    signal = signal_data['signal']
                    technical_score += signal_values.get(signal, 0)
                    signal_count += 1

            if signal_count > 0:
                technical_score /= signal_count

            # Combined score
            combined_score = (sentiment_score * sentiment_weight) + (technical_score * technical_weight)

            # Determine overall recommendation
            if combined_score >= 0.4:
                recommendation = "BUY"
                confidence = min(100, 50 + abs(combined_score) * 50)
            elif combined_score <= -0.4:
                recommendation = "SELL"
                confidence = min(100, 50 + abs(combined_score) * 50)
            else:
                recommendation = "HOLD"
                confidence = 50

            return {
                'recommendation': recommendation,
                'confidence': round(confidence, 2),
                'combined_score': round(combined_score, 3),
                'sentiment_contribution': round(sentiment_score * sentiment_weight, 3),
                'technical_contribution': round(technical_score * technical_weight, 3),
                'sentiment_analysis': {
                    'score': news_sentiment.score,
                    'category': news_sentiment.category.value,
                    'summary': news_sentiment.summary,
                    'news_count': news_sentiment.news_count
                },
                'reasoning': self._generate_reasoning(
                    recommendation,
                    sentiment_score,
                    technical_score,
                    news_sentiment
                )
            }

        except Exception as e:
            logger.error(f"Error combining sentiments: {e}")
            return {
                'recommendation': 'HOLD',
                'confidence': 0,
                'combined_score': 0,
                'reasoning': 'Error in analysis'
            }

    def _generate_reasoning(
        self,
        recommendation: str,
        sentiment_score: float,
        technical_score: float,
        news_sentiment: SentimentAnalysis
    ) -> str:
        """Generate reasoning for recommendation"""
        reasons = []

        # Sentiment reasoning
        if sentiment_score > 0.3:
            reasons.append(f"Positive news sentiment ({news_sentiment.summary})")
        elif sentiment_score < -0.3:
            reasons.append(f"Negative news sentiment ({news_sentiment.summary})")

        # Technical reasoning
        if technical_score > 0.3:
            reasons.append("Technical indicators show bullish signals")
        elif technical_score < -0.3:
            reasons.append("Technical indicators show bearish signals")

        # Combined reasoning
        if recommendation == "BUY":
            if not reasons:
                reasons.append("Moderate positive signals from analysis")
        elif recommendation == "SELL":
            if not reasons:
                reasons.append("Moderate negative signals from analysis")
        else:
            if not reasons:
                reasons.append("Mixed signals suggest waiting for clearer direction")

        return "; ".join(reasons)


# Global instance
sentiment_analyzer = SentimentAnalyzer()
