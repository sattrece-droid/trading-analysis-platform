# Trading Intelligence Platform

A comprehensive real-time stock market analysis system that provides technical indicators, trading signals, market narratives, and performance tracking.

## Features

- **Real-time Technical Analysis**: RSI, MACD, Bollinger Bands, and other indicators
- **Automated Trading Signals**: Buy/Sell/Hold signals with confidence scores
- **Market Narratives**: AI-powered analysis of market trends and catalyst events
- **Dashboard**: Interactive web interface for monitoring trading signals
- **Webhook Server**: REST API for integration with n8n and other automation tools
- **Portfolio Tracking**: Track multiple tickers and watchlists
- **Backtesting**: Historical analysis and strategy validation

## Project Structure

```
trading-intelligence/
├── src/
│   ├── trading_webhook_server.py    # Flask API server (runs continuously)
│   ├── trading_analysis.py          # Core analysis engine
│   ├── narrative_analysis.py        # AI-powered market narratives
│   ├── dashboard_server.py          # Web dashboard
│   ├── display_results.py           # Results formatting
│   ├── market_performance.py        # Performance metrics
│   └── backtest.py                  # Backtesting engine
├── .env.example                     # Configuration template
├── .env.trading                     # Configuration (DO NOT COMMIT)
├── requirements.txt                 # Python dependencies
├── MVP_SUMMARY.md                   # MVP feature overview
└── INTEGRATION_GUIDE.md             # Integration with n8n
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (for signal storage)
- n8n (optional, for automation)
- OpenClaw (optional, for AI services)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/trading-intelligence.git
   cd trading-intelligence
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env.trading
   # Edit .env.trading with your API keys and database credentials
   ```

5. **Initialize database** (if needed)
   ```bash
   psql -U isaacacosta -d trading_intelligence -f setup_db.sql
   ```

## Running the Services

### Webhook Server (Continuous Operation)

The webhook server runs as a Flask app on port 5555 and processes trading analysis requests from n8n.

```bash
cd src
python3 trading_webhook_server.py
```

**For Production (Continuous Running)**:

Using `nohup`:
```bash
cd src
nohup python3 trading_webhook_server.py > webhook_server.log 2>&1 &
```

Using `screen`:
```bash
screen -S trading-webhook
cd src
python3 trading_webhook_server.py
# Press Ctrl+A then D to detach
```

Using `systemd` (systemd service file):
Create `/etc/systemd/system/trading-webhook.service`:
```ini
[Unit]
Description=Trading Intelligence Webhook Server
After=network.target

[Service]
Type=simple
User=isaacacosta
WorkingDirectory=/Users/isaacacosta/Documents/Projects-Ideas/trading-intelligence/src
ExecStart=/usr/bin/python3 /Users/isaacacosta/Documents/Projects-Ideas/trading-intelligence/src/trading_webhook_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable it:
```bash
sudo systemctl enable trading-webhook
sudo systemctl start trading-webhook
```

### Dashboard Server

```bash
cd src
python3 dashboard_server.py
```

Access at `http://localhost:5000`

### Analyze Watchlist

```bash
cd src
python3 trading_webhook_server.py
# In another terminal:
curl -X POST http://localhost:5555/analyze/watchlist
```

### Backtesting

```bash
cd src
python3 backtest.py
```

## API Endpoints

The webhook server provides the following endpoints:

- `GET /health` - Health check
- `GET /analyze/<ticker>` - Analyze a single ticker
- `POST /analyze/watchlist` - Analyze all tickers in watchlist
- `GET /signals/latest` - Get latest trading signals

## Configuration

Edit `.env.trading` to configure:

- **API Keys**: Alpha Vantage, Finnhub
- **Database**: PostgreSQL connection
- **Services**: n8n, OpenClaw URLs

See `.env.example` for all available options.

## Integration with n8n

This system is designed to integrate with n8n workflows. See `INTEGRATION_GUIDE.md` for detailed instructions on:

- Triggering analysis from n8n
- Storing signals in PostgreSQL
- Connecting to WhatsApp/Telegram
- Automating trading notifications

## Performance Notes

- Alpha Vantage free tier: 5 API calls per minute
- Finnhub free tier: 60 API calls per minute
- Server includes 1-second delays between ticker analysis to respect rate limits

## Troubleshooting

**Database connection failed**: 
- Ensure PostgreSQL is running: `psql -U isaacacosta -d trading_intelligence`
- Check `.env.trading` database credentials

**API key errors**:
- Verify API keys in `.env.trading`
- Check rate limits on Alpha Vantage/Finnhub dashboards

**Port already in use**:
- Check for existing process: `lsof -i :5555`
- Kill process: `kill -9 <PID>`

## Documentation

- `MVP_SUMMARY.md` - Feature overview and architecture
- `INTEGRATION_GUIDE.md` - n8n integration instructions

## License

MIT License

## Author

Isaac Acosta
