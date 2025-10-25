"""
LLM-based AI Advisor
Uses Large Language Models (Claude/OpenAI) for intelligent stock analysis and recommendations
"""
import asyncio
import httpx
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class LLMAdvisor:
    """AI Advisor using LLM for stock analysis"""

    def __init__(self, api_key: Optional[str] = None, provider: str = "anthropic"):
        """
        Initialize LLM Advisor

        Args:
            api_key: API key for LLM provider
            provider: "anthropic" for Claude or "openai" for GPT
        """
        self.provider = provider
        self.api_key = api_key or getattr(settings, f'{provider}_api_key', None)

        if provider == "anthropic":
            self.api_url = "https://api.anthropic.com/v1/messages"
            self.model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5
        elif provider == "openai":
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.model = "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def analyze_stock(
        self,
        symbol: str,
        market_data: Dict,
        technical_indicators: Dict,
        sentiment_data: Dict,
        portfolio_context: Optional[Dict] = None
    ) -> Dict:
        """
        Comprehensive stock analysis using LLM

        Args:
            symbol: Stock symbol
            market_data: Market and company information
            technical_indicators: Technical analysis data
            sentiment_data: News sentiment analysis
            portfolio_context: Current portfolio context (optional)

        Returns:
            Dictionary with AI analysis and recommendation
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_analysis_prompt(
                symbol,
                market_data,
                technical_indicators,
                sentiment_data,
                portfolio_context
            )

            # Get LLM response
            response = await self._call_llm(prompt)

            # Parse and structure the response
            analysis = self._parse_llm_response(response)

            return analysis

        except Exception as e:
            logger.error(f"Error in LLM analysis for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendation': 'HOLD',
                'confidence': 0
            }

    def _build_analysis_prompt(
        self,
        symbol: str,
        market_data: Dict,
        technical_indicators: Dict,
        sentiment_data: Dict,
        portfolio_context: Optional[Dict]
    ) -> str:
        """Build comprehensive analysis prompt for LLM"""

        prompt = f"""You are an expert financial advisor AI analyzing stock {symbol}.
Provide a comprehensive investment recommendation based on the following data:

## Company Information:
- Symbol: {symbol}
- Name: {market_data.get('name', 'Unknown')}
- Sector: {market_data.get('sector', 'Unknown')}
- Industry: {market_data.get('industry', 'Unknown')}
- Market Cap: ${market_data.get('market_cap', 0):,.0f}
- Current Price: ${market_data.get('current_price', 0):.2f}
- Previous Close: ${market_data.get('previous_close', 0):.2f}
- Day Change: {market_data.get('day_change', {}).get('percent', 0):.2f}%

## Valuation Metrics:
- P/E Ratio: {market_data.get('pe_ratio', 'N/A')}
- Forward P/E: {market_data.get('forward_pe', 'N/A')}
- EPS: {market_data.get('eps', 'N/A')}
- Dividend Yield: {market_data.get('dividend_yield', 0)*100 if market_data.get('dividend_yield') else 'N/A'}%
- Beta: {market_data.get('beta', 'N/A')}
- 52 Week High: ${market_data.get('52_week_high', 0):.2f}
- 52 Week Low: ${market_data.get('52_week_low', 0):.2f}

## Technical Indicators:
"""

        # Add technical indicators
        if 'indicators' in technical_indicators:
            indicators = technical_indicators['indicators']
            prompt += f"""- RSI (14): {indicators.get('rsi', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')}
- MACD Signal: {indicators.get('macd_signal', 'N/A')}
- Bollinger Bands: Upper ${indicators.get('bb_upper', 0):.2f}, Lower ${indicators.get('bb_lower', 0):.2f}
- SMA 50: ${indicators.get('sma_50', 0):.2f}
- SMA 200: ${indicators.get('sma_200', 0):.2f}
- ATR: {indicators.get('atr', 'N/A')}
"""

        # Add technical signals
        if 'signals' in technical_indicators:
            prompt += "\n## Technical Signals:\n"
            for name, signal in technical_indicators['signals'].items():
                if isinstance(signal, dict):
                    prompt += f"- {name.title()}: {signal.get('signal', 'N/A')} ({signal.get('description', '')})\n"

        # Add sentiment analysis
        prompt += f"""
## Market Sentiment:
- News Sentiment: {sentiment_data.get('category', 'neutral')}
- Sentiment Score: {sentiment_data.get('score', 0):.2f}
- Summary: {sentiment_data.get('summary', 'No data')}
- News Articles Analyzed: {sentiment_data.get('news_count', 0)}
"""

        # Add portfolio context if provided
        if portfolio_context:
            prompt += f"""
## Portfolio Context:
- Current Holdings: {portfolio_context.get('current_quantity', 0)} shares
- Average Price: ${portfolio_context.get('average_price', 0):.2f}
- Current Value: ${portfolio_context.get('current_value', 0):.2f}
- Unrealized P&L: ${portfolio_context.get('pnl', 0):.2f}
- Portfolio Risk Level: {portfolio_context.get('risk_level', 'Unknown')}
"""

        prompt += """
## Your Task:
Provide a detailed investment analysis with the following structure:

1. **Recommendation**: BUY, SELL, or HOLD
2. **Confidence Score**: 0-100 (how confident are you in this recommendation)
3. **Target Price**: Your price target for the stock
4. **Stop Loss**: Recommended stop-loss level
5. **Time Horizon**: Short-term (1-3 months), Medium-term (3-12 months), or Long-term (1+ years)
6. **Key Points**: 3-5 bullet points summarizing your analysis
7. **Risks**: 2-3 key risks to consider
8. **Opportunities**: 2-3 potential opportunities
9. **Detailed Analysis**: A comprehensive explanation of your recommendation (2-3 paragraphs)

Format your response as JSON with the following structure:
{
    "recommendation": "BUY|SELL|HOLD",
    "confidence": 0-100,
    "target_price": number,
    "stop_loss": number,
    "time_horizon": "short|medium|long",
    "key_points": ["point1", "point2", ...],
    "risks": ["risk1", "risk2", ...],
    "opportunities": ["opp1", "opp2", ...],
    "analysis": "detailed explanation"
}

Be objective, data-driven, and consider both technical and fundamental factors in your analysis.
"""

        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM API"""
        try:
            if not self.api_key:
                logger.warning("No LLM API key configured, using fallback analysis")
                return self._get_fallback_response()

            async with httpx.AsyncClient(timeout=60.0) as client:
                if self.provider == "anthropic":
                    headers = {
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    }
                    data = {
                        "model": self.model,
                        "max_tokens": 2048,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }

                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=data
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result['content'][0]['text']

                elif self.provider == "openai":
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert financial advisor providing stock analysis and recommendations."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2048
                    }

                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=data
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result['choices'][0]['message']['content']

        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API error: {e.response.status_code} - {e.response.text}")
            return self._get_fallback_response()
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return self._get_fallback_response()

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response into structured data"""
        try:
            # Try to extract JSON from response
            # LLMs sometimes wrap JSON in markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            # Parse JSON
            analysis = json.loads(json_str)

            # Ensure required fields exist
            analysis.setdefault('recommendation', 'HOLD')
            analysis.setdefault('confidence', 50)
            analysis.setdefault('target_price', 0)
            analysis.setdefault('stop_loss', 0)
            analysis.setdefault('time_horizon', 'medium')
            analysis.setdefault('key_points', [])
            analysis.setdefault('risks', [])
            analysis.setdefault('opportunities', [])
            analysis.setdefault('analysis', 'Analysis unavailable')

            analysis['success'] = True
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM JSON response: {e}")
            logger.debug(f"Response was: {response}")

            # Fallback parsing
            return {
                'success': False,
                'recommendation': 'HOLD',
                'confidence': 50,
                'analysis': response,
                'error': 'Could not parse structured response'
            }

    def _get_fallback_response(self) -> str:
        """Get fallback response when LLM is unavailable"""
        return json.dumps({
            "recommendation": "HOLD",
            "confidence": 50,
            "target_price": 0,
            "stop_loss": 0,
            "time_horizon": "medium",
            "key_points": [
                "LLM analysis unavailable",
                "Using technical indicators only",
                "Consider waiting for more data"
            ],
            "risks": [
                "Limited analysis due to API unavailability"
            ],
            "opportunities": [],
            "analysis": "AI analysis is currently unavailable. Please refer to technical indicators and market data for manual analysis."
        })


# Global instance (will use settings from config)
try:
    llm_advisor = LLMAdvisor()
except Exception as e:
    logger.warning(f"Could not initialize LLM advisor: {e}")
    llm_advisor = None
