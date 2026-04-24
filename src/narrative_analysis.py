#!/usr/bin/env python3
"""
Generate narrative explanations for trading signals
Explains WHAT the signal is and WHY it's being generated
"""

class TradingNarrative:

    # Glossary definitions for indicators
    GLOSSARY = {
        'RSI': {
            'name': 'Relative Strength Index',
            'definition': 'Measures momentum on a scale of 0-100. Shows if a stock is overbought (too high) or oversold (too low).',
            'ranges': [
                ('0-30', 'OVERSOLD - Potential reversal up', '#27ae60'),
                ('30-70', 'Neutral - No directional bias', '#3498db'),
                ('70-100', 'OVERBOUGHT - Potential pullback', '#e74c3c'),
            ]
        },
        'MACD': {
            'name': 'Moving Average Convergence Divergence',
            'definition': 'Tracks momentum by comparing two moving averages. Shows trend direction and strength.',
            'ranges': [
                ('MACD > Signal Line', 'Bullish momentum (uptrend)', '#27ae60'),
                ('MACD < Signal Line', 'Bearish momentum (downtrend)', '#e74c3c'),
                ('MACD > 0', 'Uptrend bias', '#3498db'),
                ('MACD < 0', 'Downtrend bias', '#e67e22'),
            ]
        },
        'Bollinger Bands': {
            'name': 'Bollinger Bands',
            'definition': 'Shows price volatility and support/resistance levels. Band width indicates how volatile the stock is.',
            'ranges': [
                ('Band width < 15%', 'Low volatility - consolidating', '#3498db'),
                ('Band width 15-25%', 'Normal volatility', '#27ae60'),
                ('Band width > 30%', 'High volatility - potential breakout', '#e74c3c'),
                ('Price at upper band', 'Near resistance - potential pullback', '#e74c3c'),
                ('Price at lower band', 'Near support - potential bounce', '#27ae60'),
            ]
        },
        'Moving Averages': {
            'name': 'Moving Averages (MA)',
            'definition': 'Smoothed price trends over different time periods. Shows long-term direction.',
            'ranges': [
                ('Price > 20-MA', 'Short-term uptrend', '#27ae60'),
                ('Price > 50-MA', 'Medium-term uptrend', '#3498db'),
                ('Price > 200-MA', 'Long-term uptrend', '#1f77b4'),
                ('Price below all MAs', 'Downtrend', '#e74c3c'),
            ]
        }
    }
    """Generate human-readable explanations for technical analysis"""

    @staticmethod
    def _create_tooltip(indicator_name, content=None):
        """Create a tooltip HTML element for an indicator"""
        if indicator_name not in TradingNarrative.GLOSSARY:
            return ""

        glossary = TradingNarrative.GLOSSARY[indicator_name]
        ranges_html = "".join([
            f'<div style="margin: 5px 0; padding: 5px; background: {color}20; border-left: 3px solid {color};">'
            f'<strong>{range_label}:</strong> {description}</div>'
            for range_label, description, color in glossary['ranges']
        ])

        return f'''
        <span class="indicator-tooltip" title="Click for more info">
            <span class="indicator-name">{indicator_name}</span>
            <span class="tooltip-icon">?</span>
            <div class="tooltip-content" style="display:none;">
                <strong>{glossary['name']}</strong><br>
                <em>{glossary['definition']}</em><br><br>
                <strong>Interpretation Guide:</strong><br>
                {ranges_html}
            </div>
        </span>
        '''

    @staticmethod
    def explain_signal(ticker, analysis):
        """Generate detailed narrative for a signal"""

        signal = analysis['signal_type']
        confidence = analysis['confidence']
        rsi = analysis['rsi']
        macd = analysis['macd']
        macd_signal = analysis['macd_signal']
        price = analysis['current_price']
        bb_upper = analysis['bb_upper']
        bb_middle = analysis['bb_middle']
        bb_lower = analysis['bb_lower']
        ma_20 = analysis['ma_20']
        ma_50 = analysis['ma_50']
        ma_200 = analysis['ma_200']
        signals_aligned = analysis['signals_aligned']

        # Build narrative
        lines = []
        lines.append(f"📊 {ticker} — {signal} Signal ({confidence:.0f}% Confidence)")
        lines.append("")

        # Signal strength explanation
        if signals_aligned == 1:
            strength_desc = "weak signal (only 1 indicator aligned)"
        elif signals_aligned == 2:
            strength_desc = "moderate signal (2 indicators aligned)"
        elif signals_aligned == 3:
            strength_desc = "strong signal (3 indicators aligned)"
        else:
            strength_desc = "very strong signal (all 4 indicators aligned)"

        lines.append(f"Signal Strength: {strength_desc}")
        lines.append("")

        # RSI explanation
        lines.append("📈 Momentum (RSI):")
        if rsi < 30:
            lines.append(f"  • RSI {rsi:.1f}: OVERSOLD — strong potential reversal signal")
        elif rsi < 40:
            lines.append(f"  • RSI {rsi:.1f}: Weak momentum — setup for potential rally")
        elif rsi < 60:
            lines.append(f"  • RSI {rsi:.1f}: Neutral momentum — no directional bias")
        elif rsi < 70:
            lines.append(f"  • RSI {rsi:.1f}: Rising momentum — strength building")
        else:
            lines.append(f"  • RSI {rsi:.1f}: OVERBOUGHT — watch for pullback or reversal")

        # MACD explanation
        lines.append("")
        lines.append("📊 Trend (MACD):")
        if macd > macd_signal:
            histogram = abs(macd - macd_signal)
            if histogram > 2:
                lines.append(f"  • MACD {macd:.2f} > Signal {macd_signal:.2f}: STRONG bullish trend, momentum expanding")
            else:
                lines.append(f"  • MACD {macd:.2f} > Signal {macd_signal:.2f}: Bullish, but momentum flattening")
        else:
            histogram = abs(macd - macd_signal)
            if histogram > 2:
                lines.append(f"  • MACD {macd:.2f} < Signal {macd_signal:.2f}: STRONG bearish trend, momentum declining")
            else:
                lines.append(f"  • MACD {macd:.2f} < Signal {macd_signal:.2f}: Bearish, but momentum stabilizing")

        if macd > 0:
            lines.append(f"  • MACD above zero: Uptrend bias")
        else:
            lines.append(f"  • MACD below zero: Downtrend bias")

        # Bollinger Bands explanation
        lines.append("")
        lines.append("🎯 Volatility & Support/Resistance (Bollinger Bands):")
        bb_position = (price - bb_lower) / (bb_upper - bb_lower) * 100
        if bb_position < 20:
            lines.append(f"  • Price at LOWER band ({price:.2f}): Strong support, oversold condition")
        elif bb_position < 50:
            lines.append(f"  • Price in lower half: Near support, potential bounce")
        elif bb_position < 80:
            lines.append(f"  • Price in upper half: Near resistance, potential pullback")
        else:
            lines.append(f"  • Price at UPPER band ({price:.2f}): Strong resistance, overbought condition")

        lines.append(f"  • Band width: {(bb_upper - bb_lower):.2f} ({((bb_upper - bb_lower) / bb_middle * 100):.1f}% of price)")

        # Moving Averages explanation
        lines.append("")
        lines.append("📉 Trend Structure (Moving Averages):")

        above_20 = "✓" if price > ma_20 else "✗"
        above_50 = "✓" if price > ma_50 else "✗"
        above_200 = "✓" if ma_200 and price > ma_200 else "?"

        lines.append(f"  • Price vs 20-day MA: {above_20} ({price:.2f} vs {ma_20:.2f})")
        lines.append(f"  • Price vs 50-day MA: {above_50} ({price:.2f} vs {ma_50:.2f})")
        if ma_200:
            lines.append(f"  • Price vs 200-day MA: {above_200} ({price:.2f} vs {ma_200:.2f})")
        else:
            lines.append(f"  • Price vs 200-day MA: ? (insufficient data)")

        # Trend characterization
        ma_above_count = sum([price > ma_20, price > ma_50, ma_200 and price > ma_200])
        if ma_above_count == 3:
            lines.append(f"  ➜ STRONG UPTREND: Price above all major moving averages")
        elif ma_above_count == 2:
            lines.append(f"  ➜ UPTREND: Price above most moving averages")
        elif ma_above_count == 1:
            lines.append(f"  ➜ MIXED: Some alignment, but weak trend")
        else:
            lines.append(f"  ➜ DOWNTREND: Price below major moving averages")

        # Action recommendation
        lines.append("")
        lines.append("💡 Action:")

        if signal == "BUY":
            if confidence >= 75:
                lines.append(f"  STRONG BUY — Enter position now or buy dips")
                lines.append(f"  Stop-loss: Below recent swing low")
                lines.append(f"  Target: Next resistance or +5-10% move")
            elif confidence >= 50:
                lines.append(f"  MODERATE BUY — Consider entry, watch for confirmation")
                lines.append(f"  Wait for: RSI pullback to 40-50 for better entry")
                lines.append(f"  Risk: Limited upside until more signals align")
            else:
                lines.append(f"  WEAK BUY — Informational signal, not yet actionable")
                lines.append(f"  Wait for: 2-3 more indicators to align (RSI <30, MACD cross)")
                lines.append(f"  Risk: High, only for aggressive traders")

        elif signal == "SELL":
            if confidence >= 75:
                lines.append(f"  STRONG SELL — Exit longs, consider shorts")
                lines.append(f"  Stop-loss: Above recent swing high")
                lines.append(f"  Target: Next support or -5-10% decline")
            elif confidence >= 50:
                lines.append(f"  MODERATE SELL — Trim positions, watch for weakness")
                lines.append(f"  Wait for: RSI peak >70 or MACD bearish cross for exit")
                lines.append(f"  Risk: May be temporary pullback in uptrend")
            else:
                lines.append(f"  WEAK SELL — Informational signal, not yet actionable")
                lines.append(f"  Wait for: 2-3 more indicators to align (RSI >70, MACD cross)")
                lines.append(f"  Risk: May bounce higher before decline")

        else:  # HOLD
            lines.append(f"  HOLD — Conflicting signals, no clear direction")
            lines.append(f"  Wait for: Clearer signal before entering position")
            lines.append(f"  Risk: Position holding, but risk/reward unclear")

        lines.append("")
        lines.append("⚠️ Risk Management:")
        lines.append(f"  • Always use stop-loss to limit downside")
        lines.append(f"  • Position size based on your risk tolerance")
        lines.append(f"  • This is technical analysis only, not financial advice")

        return "\n".join(lines)

    @staticmethod
    def explain_signal_html(ticker, analysis):
        """Generate HTML narrative with interactive 'Learn More' tooltips"""

        signal = analysis['signal_type']
        confidence = analysis['confidence']
        rsi = analysis['rsi']
        macd = analysis['macd']
        macd_signal = analysis['macd_signal']
        price = analysis['current_price']
        bb_upper = analysis['bb_upper']
        bb_middle = analysis['bb_middle']
        bb_lower = analysis['bb_lower']
        ma_20 = analysis['ma_20']
        ma_50 = analysis['ma_50']
        ma_200 = analysis['ma_200']
        signals_aligned = analysis['signals_aligned']

        html = []
        signal_color = '#27ae60' if signal == 'BUY' else '#e74c3c' if signal == 'SELL' else '#f39c12'

        # Signal strength explanation
        if signals_aligned == 1:
            strength_desc = "weak signal (only 1 indicator aligned)"
        elif signals_aligned == 2:
            strength_desc = "moderate signal (2 indicators aligned)"
        elif signals_aligned == 3:
            strength_desc = "strong signal (3 indicators aligned)"
        else:
            strength_desc = "very strong signal (all 4 indicators aligned)"

        # Header with confidence
        html.append(f'<div class="signal-analysis-html">')
        html.append(f'<div style="margin-bottom: 15px;">')
        html.append(f'<div style="color: {signal_color}; font-weight: bold; font-size: 14px;">Signal Strength: {strength_desc}</div>')
        html.append(f'<small style="color: #666;">Based on {signals_aligned} out of 4 technical indicators aligned</small>')
        html.append(f'</div>')

        # RSI explanation with tooltip
        html.append(f'<div style="margin: 15px 0; padding: 12px; background: #f8f9fa; border-radius: 4px;">')
        html.append(f'<div style="display: flex; justify-content: space-between; align-items: center;">')
        html.append(f'<strong>📈 Momentum (RSI)</strong>')
        html.append(f'<span class="learn-more-btn" onclick="toggleLearnMore(this)">? Learn More</span>')
        html.append(f'</div>')

        if rsi < 30:
            rsi_status = f'<span style="color: #27ae60; font-weight: bold;">OVERSOLD</span> — Strong potential reversal signal'
        elif rsi < 40:
            rsi_status = f'<span style="color: #3498db; font-weight: bold;">Weak momentum</span> — Setup for potential rally'
        elif rsi < 60:
            rsi_status = f'<span style="color: #7f8c8d;">Neutral</span> — No directional bias'
        elif rsi < 70:
            rsi_status = f'<span style="color: #3498db; font-weight: bold;">Rising momentum</span> — Strength building'
        else:
            rsi_status = f'<span style="color: #e74c3c; font-weight: bold;">OVERBOUGHT</span> — Watch for pullback or reversal'

        html.append(f'<div style="margin: 10px 0;">RSI {rsi:.1f}: {rsi_status}</div>')
        html.append(f'<div class="learn-more-content" style="display: none; margin-top: 10px; padding: 10px; background: white; border-left: 3px solid #3498db; border-radius: 3px;">')
        html.append(f'<strong>What is RSI?</strong> Relative Strength Index measures momentum 0-100.<br>')
        html.append(f'<strong>Good ranges:</strong> 30-70 is neutral. <30 means oversold (potential bounce), >70 means overbought (potential pullback).<br>')
        html.append(f'<strong>Current reading:</strong> {rsi:.1f} is {"OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "neutral"}.')
        html.append(f'</div>')
        html.append(f'</div>')

        # MACD explanation with tooltip
        html.append(f'<div style="margin: 15px 0; padding: 12px; background: #f8f9fa; border-radius: 4px;">')
        html.append(f'<div style="display: flex; justify-content: space-between; align-items: center;">')
        html.append(f'<strong>📊 Trend (MACD)</strong>')
        html.append(f'<span class="learn-more-btn" onclick="toggleLearnMore(this)">? Learn More</span>')
        html.append(f'</div>')

        if macd > macd_signal:
            histogram = abs(macd - macd_signal)
            if histogram > 2:
                macd_status = f'<span style="color: #27ae60; font-weight: bold;">STRONG bullish trend</span>, momentum expanding'
            else:
                macd_status = f'<span style="color: #27ae60;">Bullish</span>, momentum flattening'
            trend_bias = "Uptrend bias" if macd > 0 else "Mixed signals"
        else:
            histogram = abs(macd - macd_signal)
            if histogram > 2:
                macd_status = f'<span style="color: #e74c3c; font-weight: bold;">STRONG bearish trend</span>, momentum declining'
            else:
                macd_status = f'<span style="color: #e74c3c;">Bearish</span>, momentum stabilizing'
            trend_bias = "Downtrend bias" if macd < 0 else "Mixed signals"

        html.append(f'<div style="margin: 10px 0;">MACD {macd:.2f} vs Signal {macd_signal:.2f}: {macd_status}<br>')
        html.append(f'<small>→ {trend_bias}</small></div>')
        html.append(f'<div class="learn-more-content" style="display: none; margin-top: 10px; padding: 10px; background: white; border-left: 3px solid #3498db; border-radius: 3px;">')
        html.append(f'<strong>What is MACD?</strong> Moving Average Convergence Divergence tracks momentum by comparing averages.<br>')
        html.append(f'<strong>Good values:</strong> When MACD is above its signal line = bullish. When below = bearish.<br>')
        html.append(f'<strong>Current reading:</strong> MACD is {"above" if macd > macd_signal else "below"} signal line, indicating {"bullish" if macd > macd_signal else "bearish"} momentum.')
        html.append(f'</div>')
        html.append(f'</div>')

        # Bollinger Bands explanation with tooltip
        html.append(f'<div style="margin: 15px 0; padding: 12px; background: #f8f9fa; border-radius: 4px;">')
        html.append(f'<div style="display: flex; justify-content: space-between; align-items: center;">')
        html.append(f'<strong>🎯 Volatility & Support/Resistance (Bollinger Bands)</strong>')
        html.append(f'<span class="learn-more-btn" onclick="toggleLearnMore(this)">? Learn More</span>')
        html.append(f'</div>')

        bb_position = (price - bb_lower) / (bb_upper - bb_lower) * 100
        bb_width_pct = (bb_upper - bb_lower) / bb_middle * 100

        if bb_position < 20:
            bb_status = f'<span style="color: #27ae60; font-weight: bold;">Strong support</span> at lower band, oversold condition'
        elif bb_position < 50:
            bb_status = f'<span style="color: #3498db;">Near support</span>, potential bounce'
        elif bb_position < 80:
            bb_status = f'<span style="color: #e74c3c;">Near resistance</span>, potential pullback'
        else:
            bb_status = f'<span style="color: #e74c3c; font-weight: bold;">Strong resistance</span> at upper band, overbought condition'

        volatility_level = "Low" if bb_width_pct < 15 else "Normal" if bb_width_pct < 25 else "High"

        html.append(f'<div style="margin: 10px 0;">Price position: {bb_status}<br>')
        html.append(f'<small>Band width: {(bb_upper - bb_lower):.2f} ({bb_width_pct:.1f}% of price) = {volatility_level} volatility</small></div>')
        html.append(f'<div class="learn-more-content" style="display: none; margin-top: 10px; padding: 10px; background: white; border-left: 3px solid #3498db; border-radius: 3px;">')
        html.append(f'<strong>What are Bollinger Bands?</strong> Shows price volatility and support/resistance levels.<br>')
        html.append(f'<strong>Band width meaning:</strong> <15% = low volatility, 15-25% = normal, >30% = high volatility (potential breakout).<br>')
        html.append(f'<strong>Current reading:</strong> {bb_width_pct:.1f}% width = {volatility_level} volatility. Price is {"at support" if bb_position < 30 else "near resistance" if bb_position > 70 else "in the middle"}.')
        html.append(f'</div>')
        html.append(f'</div>')

        # Moving Averages explanation with tooltip
        html.append(f'<div style="margin: 15px 0; padding: 12px; background: #f8f9fa; border-radius: 4px;">')
        html.append(f'<div style="display: flex; justify-content: space-between; align-items: center;">')
        html.append(f'<strong>📉 Trend Structure (Moving Averages)</strong>')
        html.append(f'<span class="learn-more-btn" onclick="toggleLearnMore(this)">? Learn More</span>')
        html.append(f'</div>')

        above_20 = price > ma_20
        above_50 = price > ma_50
        above_200 = ma_200 and price > ma_200
        ma_above_count = sum([above_20, above_50, above_200])

        html.append(f'<div style="margin: 10px 0;">')
        html.append(f'<small>{"✓" if above_20 else "✗"} 20-day: {price:.2f} vs {ma_20:.2f}<br>')
        html.append(f'{"✓" if above_50 else "✗"} 50-day: {price:.2f} vs {ma_50:.2f}<br>')
        if ma_200:
            html.append(f'{"✓" if above_200 else "✗"} 200-day: {price:.2f} vs {ma_200:.2f}<br>')
        else:
            html.append(f'? 200-day: insufficient data<br>')

        if ma_above_count == 3:
            trend = "🟢 STRONG UPTREND: Price above all moving averages"
        elif ma_above_count == 2:
            trend = "📈 UPTREND: Price above most moving averages"
        elif ma_above_count == 1:
            trend = "🟡 MIXED: Some alignment, weak trend"
        else:
            trend = "📉 DOWNTREND: Price below major moving averages"

        html.append(f'<strong>{trend}</strong></div>')
        html.append(f'<div class="learn-more-content" style="display: none; margin-top: 10px; padding: 10px; background: white; border-left: 3px solid #3498db; border-radius: 3px;">')
        html.append(f'<strong>What are Moving Averages?</strong> Smoothed price trends over different time periods (20, 50, 200 days).<br>')
        html.append(f'<strong>Good pattern:</strong> Price above 20-day = short-term uptrend. Above 50-day = medium-term uptrend. Above 200-day = long-term uptrend.<br>')
        html.append(f'<strong>Current reading:</strong> Price is above {ma_above_count} out of {3 if ma_200 else 2} major moving averages, confirming {"strong uptrend" if ma_above_count >= 2 else "weak trend" if ma_above_count == 1 else "downtrend"}.')
        html.append(f'</div>')
        html.append(f'</div>')

        html.append(f'</div>')

        return "\n".join(html)

if __name__ == '__main__':
    # Example usage
    import json

    example = {
        'signal_type': 'BUY',
        'confidence': 75,
        'rsi': 35.5,
        'macd': 2.15,
        'macd_signal': 1.20,
        'current_price': 250.0,
        'bb_upper': 265.0,
        'bb_middle': 250.0,
        'bb_lower': 235.0,
        'ma_20': 248.0,
        'ma_50': 245.0,
        'ma_200': 240.0,
        'signals_aligned': 3
    }

    print(TradingNarrative.explain_signal('AAPL', example))
