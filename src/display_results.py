#!/usr/bin/env python3
"""
Display trading results in multiple formats
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from tabulate import tabulate
from trading_analysis import TradingAnalyzer
from narrative_analysis import TradingNarrative
from market_performance import MarketPerformance

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.trading'))

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')

def get_latest_signals():
    """Fetch latest signals from database"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER
    )
    cur = conn.cursor()

    cur.execute("""
        SELECT ticker, signal_type, confidence, reasoning, date
        FROM trading_signals
        WHERE date = (SELECT MAX(date) FROM trading_signals)
        ORDER BY confidence DESC
    """)

    results = []
    for row in cur.fetchall():
        results.append({
            'ticker': row[0],
            'signal': row[1],
            'confidence': f"{row[2]:.0f}%",
            'reasoning': row[3],
            'date': row[4]
        })

    cur.close()
    conn.close()
    return results

def display_table():
    """Display as formatted table"""
    signals = get_latest_signals()

    print("\n" + "="*80)
    print("TRADING INTELLIGENCE — MARKET SIGNALS")
    print("="*80 + "\n")

    table_data = [
        [s['ticker'], s['signal'], s['confidence'], s['reasoning'][:40] + "..."]
        for s in signals
    ]

    headers = ['TICKER', 'SIGNAL', 'CONFIDENCE', 'REASONING']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print(f"\nGenerated: {signals[0]['date'] if signals else 'N/A'}\n")

def display_detailed():
    """Display detailed analysis"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER
    )
    cur = conn.cursor()

    # Get the latest date
    cur.execute("SELECT MAX(date) FROM trading_signals")
    latest_date = cur.fetchone()[0]

    print("\n" + "="*80)
    print(f"TRADING INTELLIGENCE — DETAILED ANALYSIS ({latest_date})")
    print("="*80 + "\n")

    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'UBER']

    for ticker in tickers:
        cur.execute("""
            SELECT signal_type, confidence, reasoning
            FROM trading_signals
            WHERE ticker = %s AND date = %s
        """, (ticker, latest_date))

        row = cur.fetchone()
        if row:
            signal, confidence, reasoning = row
            emoji = "📈" if signal == "BUY" else "📉" if signal == "SELL" else "⏸️"

            print(f"{emoji} {ticker}")
            print(f"   Signal: {signal} | Confidence: {confidence:.0f}%")
            print(f"   {reasoning}")
            print()

    cur.close()
    conn.close()

def display_text_report():
    """Display as text report for messaging"""
    signals = get_latest_signals()

    if not signals:
        return "No signals available."

    report = "📊 TRADING SIGNALS REPORT\n\n"

    for s in signals:
        emoji = "🟢" if s['signal'] == "BUY" else "🔴" if s['signal'] == "SELL" else "⚪"
        report += f"{emoji} *{s['ticker']}*\n"
        report += f"Signal: {s['signal']} ({s['confidence']} confidence)\n"
        report += f"Analysis: {s['reasoning']}\n\n"

    return report

def display_html():
    """Generate HTML for web display with detailed narratives"""
    analyzer = TradingAnalyzer()

    # Get full analysis for each ticker
    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'UBER']
    analyses = {}
    for ticker in tickers:
        analysis = analyzer.analyze_ticker(ticker)
        if analysis:
            analyses[ticker] = analysis

    analyzer.close()

    html = """
    <html>
    <head>
        <title>Trading Intelligence Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f0f2f5; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #1f77b4; text-align: center; margin-bottom: 10px; }
            .timestamp { text-align: center; color: #666; margin-bottom: 30px; font-size: 12px; }
            .signal-card { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; border-left: 5px solid #ddd; }
            .signal-card.buy { border-left-color: #27ae60; }
            .signal-card.sell { border-left-color: #e74c3c; }
            .signal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .ticker { font-size: 28px; font-weight: bold; color: #333; }
            .signal-badge {
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            .signal-badge.buy { background: #d5f4e6; color: #27ae60; }
            .signal-badge.sell { background: #fadbd8; color: #e74c3c; }
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
            .summary {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }
            .summary h2 { color: #1f77b4; margin-top: 0; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; }
            th { background: #ecf0f1; font-weight: bold; }
            tr:hover { background: #f8f9fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Trading Intelligence Dashboard</h1>
            <div class="timestamp">Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</div>

            <div class="summary">
                <h2>Market Overview</h2>
                <table>
                    <tr>
                        <th>Ticker</th>
                        <th>Signal</th>
                        <th>Confidence</th>
                        <th>Price</th>
                        <th>RSI</th>
                    </tr>
    """

    signals = get_latest_signals()
    for s in signals:
        if s['ticker'] in analyses:
            a = analyses[s['ticker']]
            html += f"""
                    <tr>
                        <td><strong>{s['ticker']}</strong></td>
                        <td>{s['signal']}</td>
                        <td>{s['confidence']}</td>
                        <td>${a['current_price']:.2f}</td>
                        <td>{a['rsi']:.1f}</td>
                    </tr>
            """

    html += """
                </table>
            </div>
    """

    # Detailed analysis for each ticker
    for ticker in ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'UBER']:
        if ticker not in analyses:
            continue

        a = analyses[ticker]
        signal_type = a['signal_type'].lower()
        narrative = TradingNarrative.explain_signal(ticker, a)

        # Get market performance
        perf = MarketPerformance.get_price_changes(ticker)

        # Format performance section
        perf_html = ""
        if perf:
            change_color = "stat-positive" if perf['change_5d_pct'] > 0 else "stat-negative"
            perf_html = f"""
                <div class="performance-section">
                    <strong>📊 5-Day Market Performance:</strong>
                    <div class="performance-stat">
                        <span class="stat-label">Price 5 days ago:</span>
                        <span class="stat-value">${perf['price_5d_ago']:.2f}</span>
                    </div>
                    <div class="performance-stat">
                        <span class="stat-label">Current price:</span>
                        <span class="stat-value">${perf['current_price']:.2f}</span>
                    </div>
                    <div class="performance-stat">
                        <span class="stat-label">5-day change:</span>
                        <span class="stat-value {change_color}">{perf['change_5d']:+.2f} ({perf['change_5d_pct']:+.2f}%)</span>
                    </div>
                    <div class="performance-stat">
                        <span class="stat-label">Trend:</span>
                        <span class="stat-value">{perf['trend_5d']}</span>
                    </div>
                    <div class="performance-stat">
                        <span class="stat-label">Avg daily change:</span>
                        <span class="stat-value {change_color}">{perf['avg_daily_change']:+.2f}% per day</span>
                    </div>
                    <hr style="margin: 8px 0; border: none; border-top: 1px solid #ccc;">
                    <div class="performance-stat">
                        <span class="stat-label">30-day change:</span>
                        <span class="stat-value" style="color: {'#27ae60' if perf['change_30d_pct'] > 0 else '#e74c3c'};">{perf['change_30d_pct']:+.2f}%</span>
                    </div>
                    <div class="performance-stat">
                        <span class="stat-label">90-day change:</span>
                        <span class="stat-value" style="color: {'#27ae60' if perf['change_90d_pct'] > 0 else '#e74c3c'};">{perf['change_90d_pct']:+.2f}%</span>
                    </div>
                </div>
            """

        html += f"""
            <div class="signal-card {signal_type}">
                <div class="signal-header">
                    <span class="ticker">{ticker}</span>
                    <span class="signal-badge {signal_type}">{a['signal_type']} • {a['confidence']:.0f}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {a['confidence']}%;"></div>
                </div>
                {perf_html}
                <div class="narrative">{narrative}</div>
            </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    return html

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = 'table'

    if mode == 'table':
        display_table()
    elif mode == 'detailed':
        display_detailed()
    elif mode == 'text':
        print(display_text_report())
    elif mode == 'html':
        html = display_html()
        with open('/tmp/trading_signals.html', 'w') as f:
            f.write(html)
        print("✓ HTML report saved to /tmp/trading_signals.html")
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python3 display_results.py [table|detailed|text|html]")
