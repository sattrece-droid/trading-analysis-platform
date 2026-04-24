#!/usr/bin/env python3
"""
Backtest trading signals against historical price movements
Validates signal accuracy and confidence thresholds
"""

import psycopg2
import yfinance as yf
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd

load_dotenv('.env.trading')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')

class SignalBacktester:
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

    def test_signal(self, ticker, signal_date, signal_type, price_at_signal):
        """Test if signal was profitable (1-day, 5-day, 30-day outlook)"""

        # Fetch price history around signal date
        hist = yf.download(ticker, start=signal_date, end=signal_date + timedelta(days=35), progress=False)

        if hist.empty or len(hist) < 2:
            return None

        # Handle multi-index columns
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.get_level_values(0)

        prices = hist['Close'].values

        if len(prices) < 2:
            return None

        # Get prices at different horizons
        price_1day = prices[1] if len(prices) > 1 else None
        price_5day = prices[min(5, len(prices)-1)]
        price_30day = prices[min(30, len(prices)-1)]

        # Calculate returns
        return_1day = ((price_1day - price_at_signal) / price_at_signal * 100) if price_1day else 0
        return_5day = ((price_5day - price_at_signal) / price_at_signal * 100)
        return_30day = ((price_30day - price_at_signal) / price_at_signal * 100)

        # Check if signal was correct
        correct_1day = (return_1day > 0 and signal_type == "BUY") or (return_1day < 0 and signal_type == "SELL")
        correct_5day = (return_5day > 0 and signal_type == "BUY") or (return_5day < 0 and signal_type == "SELL")
        correct_30day = (return_30day > 0 and signal_type == "BUY") or (return_30day < 0 and signal_type == "SELL")

        return {
            'return_1day': round(return_1day, 2),
            'return_5day': round(return_5day, 2),
            'return_30day': round(return_30day, 2),
            'correct_1day': correct_1day,
            'correct_5day': correct_5day,
            'correct_30day': correct_30day,
        }

    def backtest_all(self):
        """Test all historical signals"""
        self.cur.execute("""
            SELECT ticker, date, signal_type, confidence
            FROM trading_signals
            WHERE date < NOW() - INTERVAL '1 day'  -- Only test signals from past
            ORDER BY date DESC
            LIMIT 50  -- Test last 50 signals
        """)

        results = []
        total_signals = 0
        correct_1day = 0
        correct_5day = 0
        correct_30day = 0

        for ticker, signal_date, signal_type, confidence in self.cur.fetchall():
            # Get the price at the time of signal (close price on that day)
            hist = yf.download(ticker, start=signal_date, end=signal_date + timedelta(days=1), progress=False)

            if hist.empty:
                continue

            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)

            price_at_signal = float(hist['Close'].iloc[0])

            # Test the signal
            test_result = self.test_signal(ticker, signal_date, signal_type, price_at_signal)

            if test_result:
                total_signals += 1
                if test_result['correct_1day']:
                    correct_1day += 1
                if test_result['correct_5day']:
                    correct_5day += 1
                if test_result['correct_30day']:
                    correct_30day += 1

                results.append({
                    'ticker': ticker,
                    'date': signal_date,
                    'signal': signal_type,
                    'confidence': confidence,
                    'return_1day': test_result['return_1day'],
                    'return_5day': test_result['return_5day'],
                    'return_30day': test_result['return_30day'],
                    'correct_1day': test_result['correct_1day'],
                    'correct_5day': test_result['correct_5day'],
                    'correct_30day': test_result['correct_30day'],
                })

        return {
            'results': results,
            'summary': {
                'total_signals': total_signals,
                'win_rate_1day': f"{(correct_1day/total_signals*100):.1f}%" if total_signals > 0 else "N/A",
                'win_rate_5day': f"{(correct_5day/total_signals*100):.1f}%" if total_signals > 0 else "N/A",
                'win_rate_30day': f"{(correct_30day/total_signals*100):.1f}%" if total_signals > 0 else "N/A",
            }
        }

    def display_backtest(self):
        """Display backtest results"""
        results = self.backtest_all()

        print("\n" + "="*100)
        print("SIGNAL BACKTEST RESULTS")
        print("="*100 + "\n")

        print(f"Total Signals Tested: {results['summary']['total_signals']}")
        print(f"Win Rate (1-day):  {results['summary']['win_rate_1day']}")
        print(f"Win Rate (5-day):  {results['summary']['win_rate_5day']}")
        print(f"Win Rate (30-day): {results['summary']['win_rate_30day']}")

        print("\n" + "-"*100)
        print("Detailed Results:\n")

        for r in results['results'][:20]:  # Show last 20
            status_1d = "✓" if r['correct_1day'] else "✗"
            status_5d = "✓" if r['correct_5day'] else "✗"
            status_30d = "✓" if r['correct_30day'] else "✗"

            print(f"{r['date']} | {r['ticker']} | {r['signal']} ({r['confidence']:.0f}%)")
            print(f"  1-day: {status_1d} {r['return_1day']:+.2f}% | 5-day: {status_5d} {r['return_5day']:+.2f}% | 30-day: {status_30d} {r['return_30day']:+.2f}%")

        print("\n" + "="*100 + "\n")

if __name__ == '__main__':
    tester = SignalBacktester()
    tester.display_backtest()
    tester.close()
