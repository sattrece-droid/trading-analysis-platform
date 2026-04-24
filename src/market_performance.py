#!/usr/bin/env python3
"""
Calculate market performance metrics (5-day, 30-day changes)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class MarketPerformance:
    @staticmethod
    def get_price_changes(ticker):
        """Get price changes over different periods"""
        try:
            # Fetch 6 months of data
            data = yf.download(ticker, period='6mo', progress=False)

            if data.empty:
                return None

            # Handle multi-index columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # Get current and historical prices
            current_price = float(data['Close'].iloc[-1])
            price_5d_ago = float(data['Close'].iloc[-5]) if len(data) >= 5 else current_price
            price_30d_ago = float(data['Close'].iloc[-30]) if len(data) >= 30 else current_price
            price_90d_ago = float(data['Close'].iloc[-90]) if len(data) >= 90 else current_price

            # Calculate changes
            change_5d = current_price - price_5d_ago
            change_5d_pct = (change_5d / price_5d_ago * 100) if price_5d_ago != 0 else 0

            change_30d = current_price - price_30d_ago
            change_30d_pct = (change_30d / price_30d_ago * 100) if price_30d_ago != 0 else 0

            change_90d = current_price - price_90d_ago
            change_90d_pct = (change_90d / price_90d_ago * 100) if price_90d_ago != 0 else 0

            # Calculate average daily change over 5 days
            recent_data = data['Close'].iloc[-5:]
            daily_changes = recent_data.pct_change().dropna()
            avg_daily_change = daily_changes.mean() * 100 if len(daily_changes) > 0 else 0

            # Determine trend
            if change_5d_pct > 2:
                trend_5d = "📈 Strong Uptrend"
            elif change_5d_pct > 0:
                trend_5d = "📈 Uptrend"
            elif change_5d_pct > -2:
                trend_5d = "📉 Downtrend"
            else:
                trend_5d = "📉 Strong Downtrend"

            return {
                'current_price': round(current_price, 2),
                'price_5d_ago': round(price_5d_ago, 2),
                'price_30d_ago': round(price_30d_ago, 2),
                'price_90d_ago': round(price_90d_ago, 2),
                'change_5d': round(change_5d, 2),
                'change_5d_pct': round(change_5d_pct, 2),
                'change_30d': round(change_30d, 2),
                'change_30d_pct': round(change_30d_pct, 2),
                'change_90d': round(change_90d, 2),
                'change_90d_pct': round(change_90d_pct, 2),
                'avg_daily_change': round(avg_daily_change, 2),
                'trend_5d': trend_5d,
                'trend_status': 'uptrend' if change_5d > 0 else 'downtrend'
            }

        except Exception as e:
            print(f"Error fetching performance for {ticker}: {str(e)}")
            return None

    @staticmethod
    def format_performance_narrative(ticker, performance):
        """Generate narrative about market performance"""
        if not performance:
            return "Unable to fetch market performance data"

        lines = []
        lines.append("📊 Market Performance (Last 5 Days):")
        lines.append("")
        lines.append(f"  Price 5 days ago:  ${performance['price_5d_ago']:.2f}")
        lines.append(f"  Current price:     ${performance['current_price']:.2f}")
        lines.append(f"  Change:            {performance['change_5d']:+.2f} ({performance['change_5d_pct']:+.2f}%)")
        lines.append(f"  {performance['trend_5d']}")
        lines.append(f"  Avg daily change:  {performance['avg_daily_change']:+.2f}% per day")
        lines.append("")
        lines.append("📈 Longer Term Performance:")
        lines.append(f"  30-day change:     {performance['change_30d_pct']:+.2f}%")
        lines.append(f"  90-day change:     {performance['change_90d_pct']:+.2f}%")
        lines.append("")

        # Interpretation
        if abs(performance['change_5d_pct']) > 5:
            lines.append("  ⚠️ NOTE: Large 5-day move — check for catalyst (earnings, news, etc.)")
        elif abs(performance['avg_daily_change']) > 3:
            lines.append("  ⚠️ NOTE: High volatility — larger than normal price swings")
        elif abs(performance['avg_daily_change']) < 0.5:
            lines.append("  ℹ️ NOTE: Low volatility — consolidation phase expected")

        return "\n".join(lines)

if __name__ == '__main__':
    # Test
    for ticker in ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'UBER']:
        perf = MarketPerformance.get_price_changes(ticker)
        if perf:
            print(MarketPerformance.format_performance_narrative(ticker, perf))
            print()
