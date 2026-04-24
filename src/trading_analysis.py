#!/usr/bin/env python3
"""
Trading Intelligence Analysis Engine
Calculates technical indicators and sentiment scores for stocks
"""

import os
import json
import psycopg2
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import numpy as np
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except:
    YFINANCE_AVAILABLE = False

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.trading'))

# API Keys
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
FINNHUB_KEY = os.getenv('FINNHUB_KEY')

# DB Config
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')

class TradingAnalyzer:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER
        )
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def fetch_ohlcv(self, ticker):
        """Fetch OHLCV data from yfinance (unlimited free tier)"""
        if not YFINANCE_AVAILABLE:
            print(f"  Error: yfinance not installed")
            return None

        try:
            data = yf.download(ticker, period='6mo', progress=False)
            if data.empty:
                print(f"  Error fetching {ticker}: No data")
                return None

            # Handle multi-index columns from yfinance
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            prices = []
            for idx in range(len(data)):
                row = data.iloc[idx]
                prices.append({
                    'date': str(data.index[idx].date()),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })

            return prices if prices else None
        except Exception as e:
            print(f"  Error fetching {ticker}: {str(e)}")
            return None

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        closes = [p['close'] for p in prices]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]

        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    def calculate_macd(self, prices):
        """Calculate MACD indicator"""
        closes = [p['close'] for p in prices]
        df = pd.DataFrame({'close': closes})

        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()

        return round(macd.iloc[-1], 4), round(signal.iloc[-1], 4)

    def calculate_bollinger_bands(self, prices, period=20):
        """Calculate Bollinger Bands"""
        closes = [p['close'] for p in prices]
        df = pd.DataFrame({'close': closes})

        sma = df['close'].rolling(period).mean()
        std = df['close'].rolling(period).std()

        bb_upper = sma + (std * 2)
        bb_lower = sma - (std * 2)

        return (
            round(bb_upper.iloc[-1], 2),
            round(sma.iloc[-1], 2),
            round(bb_lower.iloc[-1], 2)
        )

    def calculate_moving_averages(self, prices):
        """Calculate 20, 50, 200-day MAs"""
        closes = [p['close'] for p in prices]
        df = pd.DataFrame({'close': closes})

        ma_20 = df['close'].rolling(20).mean().iloc[-1]
        ma_50 = df['close'].rolling(50).mean().iloc[-1]
        ma_200 = df['close'].rolling(200).mean().iloc[-1]

        return round(ma_20, 2), round(ma_50, 2), round(ma_200, 2)

    def fetch_sentiment(self, ticker):
        """Fetch sentiment data from Finnhub"""
        url = f"https://finnhub.io/api/v1/quote"
        params = {
            'symbol': ticker,
            'token': FINNHUB_KEY
        }

        try:
            resp = requests.get(url, params=params)
            data = resp.json()
            return {
                'price': data.get('c', 0),
                'change': data.get('d', 0),
                'change_percent': data.get('dp', 0)
            }
        except:
            return None

    def calculate_confidence_score(self, prices):
        """Calculate buy/sell signal confidence (0-100)"""
        rsi = self.calculate_rsi(prices)
        macd, macd_signal = self.calculate_macd(prices)
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(prices)
        ma_20, ma_50, ma_200 = self.calculate_moving_averages(prices)

        current_price = prices[-1]['close']
        signals = 0
        signal_type = 'HOLD'

        # RSI signal
        if rsi < 30:
            signals += 1
            signal_type = 'BUY'
        elif rsi > 70:
            signals += 1
            signal_type = 'SELL'

        # MACD signal
        if macd > macd_signal:
            signals += 1
            if signal_type == 'HOLD':
                signal_type = 'BUY'
        elif macd < macd_signal:
            signals += 1
            if signal_type == 'HOLD':
                signal_type = 'SELL'

        # Bollinger Bands signal
        if current_price < bb_lower:
            signals += 1
            signal_type = 'BUY'
        elif current_price > bb_upper:
            signals += 1
            signal_type = 'SELL'

        # Moving Average signal
        if current_price > ma_50 and current_price > ma_200:
            signals += 1
            if signal_type == 'HOLD':
                signal_type = 'BUY'
        elif current_price < ma_50 and current_price < ma_200:
            signals += 1
            if signal_type == 'HOLD':
                signal_type = 'SELL'

        confidence = (signals / 4) * 100

        return {
            'signal_type': signal_type,
            'confidence': round(confidence, 2),
            'signals_aligned': signals,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'ma_200': ma_200
        }

    def analyze_ticker(self, ticker):
        """Full analysis for a ticker"""
        prices = self.fetch_ohlcv(ticker)
        if not prices or len(prices) < 20:  # Relaxed to 20 for MVP (100 days available)
            return None

        sentiment = self.fetch_sentiment(ticker)
        analysis = self.calculate_confidence_score(prices)

        return {
            'ticker': ticker,
            'current_price': prices[-1]['close'],
            'date': prices[-1]['date'],
            'sentiment': sentiment,
            **analysis
        }

def analyze_watchlist():
    """Analyze all tickers in watchlist"""
    analyzer = TradingAnalyzer()

    try:
        analyzer.cur.execute("SELECT ticker FROM watchlist ORDER BY ticker")
        tickers = [row[0] for row in analyzer.cur.fetchall()]

        results = []
        for i, ticker in enumerate(tickers):
            print(f"  Analyzing {ticker}...", end='', flush=True)
            analysis = analyzer.analyze_ticker(ticker)

            if i < len(tickers) - 1:
                time.sleep(1)  # Rate limit: 1 sec between calls

            if analysis:
                results.append(analysis)
                print(" ✓")

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
                    ticker,
                    analysis['date'],
                    analysis['signal_type'],
                    analysis['confidence'],
                    analysis['confidence'],
                    f"RSI: {analysis['rsi']}, MACD: {analysis['macd']}"
                ))
            else:
                print(" (failed)")

        analyzer.conn.commit()
        return results

    finally:
        analyzer.close()

if __name__ == '__main__':
    results = analyze_watchlist()
    print(json.dumps(results, indent=2))
