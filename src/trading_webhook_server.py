#!/usr/bin/env python3
"""
Flask webhook server for trading analysis
Exposes endpoints that n8n can call to trigger analysis
"""

from flask import Flask, request, jsonify
import json
import sys
import os
import time

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

from trading_analysis import TradingAnalyzer

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@app.route('/analyze/<ticker>', methods=['GET'])
def analyze_ticker(ticker):
    """Analyze a single ticker"""
    try:
        analyzer = TradingAnalyzer()
        analysis = analyzer.analyze_ticker(ticker.upper())
        analyzer.close()

        if not analysis:
            return jsonify({'error': f'Could not analyze {ticker}'}), 400

        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze/watchlist', methods=['POST'])
def analyze_watchlist():
    """Analyze all tickers in watchlist"""
    analyzer = TradingAnalyzer()
    try:
        analyzer.cur.execute("SELECT ticker FROM watchlist ORDER BY ticker")
        tickers = [row[0] for row in analyzer.cur.fetchall()]

        results = []
        for i, ticker in enumerate(tickers):
            try:
                analysis = analyzer.analyze_ticker(ticker)
                if analysis:
                    results.append(analysis)
                    # Store in DB
                    analyzer.cur.execute("""
                        INSERT INTO trading_signals
                        (ticker, date, signal_type, confidence, technical_score, reasoning)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (ticker, date) DO UPDATE SET
                            signal_type = EXCLUDED.signal_type,
                            confidence = EXCLUDED.confidence,
                            technical_score = EXCLUDED.technical_score
                    """, (
                        analysis['ticker'],
                        analysis['date'],
                        analysis['signal_type'],
                        analysis['confidence'],
                        analysis['confidence'],
                        f"RSI: {analysis['rsi']}, MACD: {analysis['macd']}"
                    ))
                    analyzer.conn.commit()
            except Exception as e:
                print(f"Error analyzing {ticker}: {str(e)}", flush=True)
                continue

            # Rate limit: 1 sec between API calls (Alpha Vantage free tier: 5/min)
            if i < len(tickers) - 1:
                time.sleep(1)

        analyzer.close()

        return jsonify({
            'timestamp': str(datetime.now()),
            'tickers_analyzed': len(results),
            'results': results
        })
    except Exception as e:
        analyzer.close()
        return jsonify({'error': str(e)}), 500

@app.route('/signals/latest', methods=['GET'])
def get_latest_signals():
    """Get latest signals for all tickers"""
    try:
        analyzer = TradingAnalyzer()
        analyzer.cur.execute("""
            SELECT ticker, signal_type, confidence, reasoning, date
            FROM trading_signals
            WHERE date = (SELECT MAX(date) FROM trading_signals)
            ORDER BY confidence DESC
        """)

        signals = []
        for row in analyzer.cur.fetchall():
            signals.append({
                'ticker': row[0],
                'signal': row[1],
                'confidence': float(row[2]),
                'reasoning': row[3],
                'date': str(row[4])
            })

        analyzer.close()
        return jsonify(signals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from datetime import datetime
    app.run(host='0.0.0.0', port=5555, debug=False)
