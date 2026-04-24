#!/usr/bin/env python3
"""
Flask server to serve dynamic trading dashboard with custom ticker search
"""

from flask import Flask, render_template_string, request, jsonify
from trading_analysis import TradingAnalyzer
from narrative_analysis import TradingNarrative
from market_performance import MarketPerformance
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.trading'))

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Intelligence Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            background: #f0f2f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #1f77b4;
            text-align: center;
            margin-bottom: 10px;
        }
        .timestamp {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 12px;
        }

        /* Search Form Styles */
        .search-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .search-form {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }
        .search-form input {
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            font-size: 14px;
            flex: 1;
            min-width: 150px;
        }
        .search-form input:focus {
            outline: none;
            border-color: #1f77b4;
            box-shadow: 0 0 5px rgba(31, 119, 180, 0.3);
        }
        .search-form button {
            padding: 10px 20px;
            background: #1f77b4;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        .search-form button:hover {
            background: #1660a0;
        }
        .search-tips {
            font-size: 12px;
            color: #666;
            margin-top: 10px;
        }

        .signal-card {
            background: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #ddd;
        }
        .signal-card.buy { border-left-color: #27ae60; }
        .signal-card.sell { border-left-color: #e74c3c; }
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .ticker {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }
        .signal-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }
        .signal-badge.buy {
            background: #d5f4e6;
            color: #27ae60;
        }
        .signal-badge.sell {
            background: #fadbd8;
            color: #e74c3c;
        }
        .confidence-bar {
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            background: #3498db;
        }
        .performance-section {
            background: #f0f7ff;
            padding: 12px;
            border-left: 4px solid #3498db;
            margin: 10px 0;
            border-radius: 4px;
        }
        .performance-stat {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 13px;
        }
        .stat-label { color: #666; }
        .stat-value { font-weight: bold; color: #333; }
        .stat-positive { color: #27ae60; }
        .stat-negative { color: #e74c3c; }
        .narrative {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            color: #2c3e50;
        }
        .signal-analysis-html {
            background: white;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }
        .learn-more-btn {
            background: #3498db;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
            font-weight: bold;
            display: inline-block;
        }
        .learn-more-btn:hover {
            background: #2980b9;
            transform: scale(1.05);
        }
        .learn-more-content {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            line-height: 1.6;
            color: #1a1a1a;
            background: #ffffff !important;
        }
        .summary {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .summary h2 {
            color: #1f77b4;
            margin-top: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background: #ecf0f1;
            font-weight: bold;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .error-message {
            background: #fadbd8;
            color: #c0392b;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
            border-left: 4px solid #e74c3c;
        }
        .success-message {
            background: #d5f4e6;
            color: #27ae60;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
            border-left: 4px solid #27ae60;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Trading Intelligence Dashboard</h1>
        <div class="timestamp">Last updated: {{ timestamp }}</div>

        <!-- Search Form -->
        <div class="search-section">
            <h3>🔍 Search for Analysis</h3>
            <form method="POST" class="search-form">
                <input
                    type="text"
                    name="ticker"
                    placeholder="Enter ticker symbol (e.g., AAPL, MSFT, GOOGL)"
                    maxlength="5"
                    required
                >
                <button type="submit">Analyze</button>
            </form>
            <div class="search-tips">
                💡 Tip: Enter any stock ticker symbol to get technical analysis, market performance, and trading signals
            </div>
        </div>

        <!-- Custom Analysis Result -->
        {% if custom_ticker %}
            {% if custom_analysis %}
                <div class="success-message">
                    ✅ Analysis for {{ custom_ticker.upper() }}
                </div>
                <div class="signal-card {{ custom_analysis.signal_type.lower() }}">
                    <div class="signal-header">
                        <span class="ticker">{{ custom_ticker.upper() }}</span>
                        <span class="signal-badge {{ custom_analysis.signal_type.lower() }}">
                            {{ custom_analysis.signal_type }} • {{ "%.0f"|format(custom_analysis.confidence) }}%
                        </span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {{ custom_analysis.confidence }}%;"></div>
                    </div>

                    {% if custom_performance %}
                    <div class="performance-section">
                        <strong>📊 5-Day Market Performance:</strong>
                        <div class="performance-stat">
                            <span class="stat-label">Price 5 days ago:</span>
                            <span class="stat-value">${{ "%.2f"|format(custom_performance.price_5d_ago) }}</span>
                        </div>
                        <div class="performance-stat">
                            <span class="stat-label">Current price:</span>
                            <span class="stat-value">${{ "%.2f"|format(custom_performance.current_price) }}</span>
                        </div>
                        <div class="performance-stat">
                            <span class="stat-label">5-day change:</span>
                            <span class="stat-value {% if custom_performance.change_5d_pct|float > 0 %}stat-positive{% else %}stat-negative{% endif %}">
                                {{ "%.2f"|format(custom_performance.change_5d) }} ({{ "%.2f"|format(custom_performance.change_5d_pct) }}%)
                            </span>
                        </div>
                        <div class="performance-stat">
                            <span class="stat-label">Trend:</span>
                            <span class="stat-value">{{ custom_performance.trend_5d }}</span>
                        </div>
                        <div class="performance-stat">
                            <span class="stat-label">Avg daily change:</span>
                            <span class="stat-value {% if custom_performance.avg_daily_change|float > 0 %}stat-positive{% else %}stat-negative{% endif %}">
                                {{ "%.2f"|format(custom_performance.avg_daily_change) }}% per day
                            </span>
                        </div>
                        <hr style="margin: 8px 0; border: none; border-top: 1px solid #ccc;">
                        <div class="performance-stat">
                            <span class="stat-label">30-day change:</span>
                            <span class="stat-value" style="color: {% if custom_performance.change_30d_pct|float > 0 %}#27ae60{% else %}#e74c3c{% endif %};">
                                {{ "%.2f"|format(custom_performance.change_30d_pct) }}%
                            </span>
                        </div>
                        <div class="performance-stat">
                            <span class="stat-label">90-day change:</span>
                            <span class="stat-value" style="color: {% if custom_performance.change_90d_pct|float > 0 %}#27ae60{% else %}#e74c3c{% endif %};">
                                {{ "%.2f"|format(custom_performance.change_90d_pct) }}%
                            </span>
                        </div>
                    </div>
                    {% endif %}

                    {% if custom_narrative_html %}
                        {{ custom_narrative_html | safe }}
                    {% else %}
                        <div class="narrative">{{ custom_narrative }}</div>
                    {% endif %}
                </div>
                <hr style="margin: 40px 0; border: none; border-top: 2px solid #ddd;">
            {% else %}
                <div class="error-message">
                    ❌ Unable to analyze {{ custom_ticker.upper() }}. Please check the ticker symbol and try again.
                </div>
            {% endif %}
        {% endif %}

        <!-- Default Watchlist -->
        <div class="summary">
            <h2>📋 Default Watchlist Overview</h2>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>Signal</th>
                    <th>Confidence</th>
                    <th>Price</th>
                    <th>RSI</th>
                    <th>5-Day Change</th>
                </tr>
                {% for signal in default_signals %}
                <tr>
                    <td><strong>{{ signal.ticker }}</strong></td>
                    <td>{{ signal.signal }}</td>
                    <td>{{ signal.confidence }}</td>
                    <td>{{ signal.price }}</td>
                    <td>{{ signal.rsi }}</td>
                    <td style="color: #999;">
                        {{ signal.change_5d_pct }}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- Detailed Analysis for Default Watchlist -->
        {% for card in cards %}
        <div class="signal-card {{ card.signal_type.lower() }}">
            <div class="signal-header">
                <span class="ticker">{{ card.ticker }}</span>
                <span class="signal-badge {{ card.signal_type.lower() }}">
                    {{ card.signal_type }} • {{ "%.0f"|format(card.confidence) }}%
                </span>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {{ card.confidence }}%;"></div>
            </div>

            {% if card.performance %}
            <div class="performance-section">
                <strong>📊 5-Day Market Performance:</strong>
                <div class="performance-stat">
                    <span class="stat-label">Price 5 days ago:</span>
                    <span class="stat-value">${{ "%.2f"|format(card.performance.price_5d_ago) }}</span>
                </div>
                <div class="performance-stat">
                    <span class="stat-label">Current price:</span>
                    <span class="stat-value">${{ "%.2f"|format(card.performance.current_price) }}</span>
                </div>
                <div class="performance-stat">
                    <span class="stat-label">5-day change:</span>
                    <span class="stat-value {% if card.performance.change_5d_pct|float > 0 %}stat-positive{% else %}stat-negative{% endif %}">
                        {{ "%.2f"|format(card.performance.change_5d) }} ({{ "%.2f"|format(card.performance.change_5d_pct) }}%)
                    </span>
                </div>
                <div class="performance-stat">
                    <span class="stat-label">Trend:</span>
                    <span class="stat-value">{{ card.performance.trend_5d }}</span>
                </div>
                <div class="performance-stat">
                    <span class="stat-label">Avg daily change:</span>
                    <span class="stat-value {% if card.performance.avg_daily_change|float > 0 %}stat-positive{% else %}stat-negative{% endif %}">
                        {{ "%.2f"|format(card.performance.avg_daily_change) }}% per day
                    </span>
                </div>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #ccc;">
                <div class="performance-stat">
                    <span class="stat-label">30-day change:</span>
                    <span class="stat-value" style="color: {% if card.performance.change_30d_pct|float > 0 %}#27ae60{% else %}#e74c3c{% endif %};">
                        {{ "%.2f"|format(card.performance.change_30d_pct) }}%
                    </span>
                </div>
                <div class="performance-stat">
                    <span class="stat-label">90-day change:</span>
                    <span class="stat-value" style="color: {% if card.performance.change_90d_pct|float > 0 %}#27ae60{% else %}#e74c3c{% endif %};">
                        {{ "%.2f"|format(card.performance.change_90d_pct) }}%
                    </span>
                </div>
            </div>
            {% endif %}

            {% if card.narrative_html %}
                {{ card.narrative_html | safe }}
            {% else %}
                <div class="narrative">{{ card.narrative }}</div>
            {% endif %}
        </div>
        {% endfor %}

    </div>

    <script>
        function toggleLearnMore(btn) {
            const content = btn.parentElement.parentElement.nextElementSibling.querySelector('.learn-more-content');
            if (!content) {
                // Try to find in siblings
                let current = btn.parentElement.parentElement;
                while (current) {
                    const found = current.querySelector('.learn-more-content');
                    if (found) {
                        content = found;
                        break;
                    }
                    current = current.nextElementSibling;
                }
            }

            if (content) {
                const isHidden = content.style.display === 'none';
                content.style.display = isHidden ? 'block' : 'none';
                btn.textContent = isHidden ? '✕ Hide' : '? Learn More';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    """Main dashboard with watchlist and custom search"""
    analyzer = TradingAnalyzer()

    # Default watchlist
    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'UBER']
    cards = []
    default_signals = []

    # Load default watchlist
    for ticker in tickers:
        analysis = analyzer.analyze_ticker(ticker)
        if analysis:
            perf = MarketPerformance.get_price_changes(ticker)
            narrative = TradingNarrative.explain_signal(ticker, analysis)
            narrative_html = TradingNarrative.explain_signal_html(ticker, analysis)

            cards.append({
                'ticker': ticker,
                'signal_type': analysis['signal_type'],
                'confidence': analysis['confidence'],
                'narrative': narrative,
                'narrative_html': narrative_html,
                'performance': perf
            })

            # For summary table
            default_signals.append({
                'ticker': ticker,
                'signal': analysis['signal_type'],
                'confidence': f"{analysis['confidence']:.0f}%",
                'price': f"${analysis['current_price']:.2f}",
                'rsi': f"{analysis['rsi']:.1f}",
                'change_5d_pct': f"{(perf['change_5d_pct']):+.2f}%" if perf else "N/A"
            })

    # Handle custom ticker search
    custom_ticker = None
    custom_analysis = None
    custom_performance = None
    custom_narrative = None
    custom_narrative_html = None

    if request.method == 'POST':
        custom_ticker = request.form.get('ticker', '').strip().upper()

        if custom_ticker:
            custom_analysis = analyzer.analyze_ticker(custom_ticker)
            if custom_analysis:
                custom_performance = MarketPerformance.get_price_changes(custom_ticker)
                custom_narrative = TradingNarrative.explain_signal(custom_ticker, custom_analysis)
                custom_narrative_html = TradingNarrative.explain_signal_html(custom_ticker, custom_analysis)

    analyzer.close()

    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        cards=cards,
        default_signals=default_signals,
        custom_ticker=custom_ticker,
        custom_analysis=custom_analysis,
        custom_performance=custom_performance,
        custom_narrative=custom_narrative,
        custom_narrative_html=custom_narrative_html
    )

if __name__ == '__main__':
    print("Starting Trading Intelligence Dashboard Server...")
    print("📊 Dashboard available at: http://localhost:5001")
    print("Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5001, debug=False)
