# Trading Intelligence MVP — Integration Guide

This guide explains how to integrate the Technical Analysis + Sentiment Analysis skills with OpenClaw and n8n.

## Architecture Overview

```
User (WhatsApp/Telegram)
  ↓
OpenClaw Agent
  ↓ (calls technical-analysis skill)
n8n Webhook → Trading Webhook Server (Flask)
  ↓
trading_analysis.py (calculations)
  ↓
PostgreSQL (storage)
```

---

## Step 1: Start the Trading Webhook Server

The Flask server exposes the analysis engine as HTTP endpoints for n8n to call.

```bash
# From Documents/Projects-Ideas directory
cd /Users/isaacacosta/Documents/Projects-Ideas

# Activate venv (if not already active)
source trading_env/bin/activate

# Install Flask
pip install flask

# Start the webhook server
python3 trading_webhook_server.py
```

Server will run on `http://localhost:5555` with these endpoints:
- `GET /health` — Health check
- `GET /analyze/<ticker>` — Analyze single ticker (e.g., `/analyze/AAPL`)
- `POST /analyze/watchlist` — Analyze all watchlist tickers
- `GET /signals/latest` — Get latest signals from DB

Test it:
```bash
curl http://localhost:5555/health
curl http://localhost:5555/analyze/AAPL
```

---

## Step 2: Create n8n Workflow (Daily Market Scan)

### Create New Workflow in n8n (http://localhost:5678)

**Step 1: Add Schedule Trigger**
- Node type: **Core Nodes → Schedule**
- Trigger: **Daily**
- Time: **6:30 AM**
- Timezone: Your local timezone

**Step 2: Add HTTP Request Node**
- Node type: **Action Nodes → HTTP Request**
- Method: `POST`
- URL: `http://localhost:5555/analyze/watchlist`
- Authentication: None
- Name it: "Fetch Analysis"

**Step 3: Add Data Storage Node**
- Node type: **Action Nodes → PostgreSQL**
- Connection: Create connection to `trading_intelligence` DB
- Query: Already being saved by Flask server
- Or skip if you want to rely on the Flask server's DB storage

**Step 4: Add Notification Node** (optional, send to Slack/Email)
- Node type: **Action Nodes → Slack** (or Email, Discord, etc.)
- Message: Format the analysis results nicely
- Send to: Your notification channel

**Step 5: Connect Nodes**
- Schedule → HTTP Request → Slack (optional) → Done

### Workflow JSON (Import this instead)

If you prefer, save this as a JSON file and import it into n8n:

```json
{
  "nodes": [
    {
      "parameters": {
        "triggerType": "daily",
        "triggerAtTime": "06:30",
        "timezone": "America/Costa_Rica"
      },
      "name": "Daily 6:30 AM",
      "type": "n8n-nodes-base.schedule",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5555/analyze/watchlist",
        "authentication": "none",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": []
        },
        "bodyParametersJson": "{}"
      },
      "name": "Fetch Market Analysis",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.3,
      "position": [500, 300]
    }
  ],
  "connections": {
    "Daily 6:30 AM": {
      "main": [
        [
          {
            "node": "Fetch Market Analysis",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Step 3: Configure OpenClaw Skills

The SKILL.md files are already created in:
- `~/.openclaw/workspace/skills/technical-analysis/SKILL.md`
- `~/.openclaw/workspace/skills/sentiment-analysis/SKILL.md`

### Verify Skills are Loaded

```bash
# Check OpenClaw knows about the skills
openclaw doctor

# Test the agent with a skill
openclaw agent --message "What's the technical analysis for AAPL?" --thinking high
```

### How Skills Integrate with n8n

When a user asks the OpenClaw agent about a ticker:

1. **User**: "What do you think of Apple stock?"
2. **OpenClaw Agent**: Recognizes the query, loads Technical Analysis skill
3. **Skill**: Contains prompts and tool references
4. **Agent**: Determines it needs real-time data, calls webhook:
   ```
   POST http://localhost:5555/analyze/AAPL
   ```
5. **Webhook**: Returns analysis JSON with all indicators
6. **Skill**: Agent uses returned data to synthesize response
7. **Response**: "Apple is showing a [signal type] signal with [confidence]% confidence because..."

---

## Step 4: Test End-to-End Flow

### Test 1: Direct Webhook Call

```bash
curl http://localhost:5555/analyze/AAPL | jq .
```

Expected response:
```json
{
  "ticker": "AAPL",
  "current_price": 273.43,
  "signal_type": "BUY",
  "confidence": 75.0,
  "rsi": 35.2,
  "macd": 1.234,
  ...
}
```

### Test 2: OpenClaw Agent Query

```bash
openclaw agent --message "Should I buy MSFT? Give me a technical analysis." --thinking high
```

Expected: Agent fetches latest MSFT data and provides detailed analysis with price levels, confidence %, signal type.

### Test 3: n8n Workflow

In n8n UI:
1. Go to your Daily Market Scan workflow
2. Click **Execute Workflow** (run button)
3. Should return analysis for all 5 tickers (AAPL, MSFT, TSLA, NVDA, UBER)

---

## Step 5: Refine the Skills (Optional)

The SKILL.md files define HOW the agent responds. You can customize:

**In `technical-analysis/SKILL.md`:**
- Adjust RSI thresholds (currently 30/70)
- Change MACD interpretation
- Modify confidence scoring logic

**In `sentiment-analysis/SKILL.md`:**
- Add/remove news sources to monitor
- Adjust sentiment score weights
- Add social media tracking

After editing SKILL.md files, reload OpenClaw:
```bash
openclaw doctor  # Verify skills are valid
openclaw gateway --restart
```

---

## Step 6: Schedule Daily Scans (Cron Alternative)

If you prefer cron instead of n8n:

```bash
# Edit crontab
crontab -e

# Add this line (6:30 AM daily):
30 6 * * * cd /Users/isaacacosta/Documents/Projects-Ideas && source trading_env/bin/activate && python3 trading_analysis.py >> /tmp/trading_scan.log 2>&1
```

---

## Monitoring & Debugging

### Check Analysis Results in Database

```bash
# Latest signals for all tickers
psql -d trading_intelligence << 'EOF'
SELECT ticker, signal_type, confidence, date
FROM trading_signals
ORDER BY date DESC, ticker
LIMIT 5;
EOF
```

### View Logs

```bash
# Flask webhook server errors
tail -f /tmp/trading_webhook.log

# OpenClaw logs
openclaw doctor --verbose

# PostgreSQL query log
psql -d trading_intelligence -c "SELECT * FROM trading_signals LIMIT 5;"
```

### Performance Check

If analysis is slow:
- Alpha Vantage API rate-limited (5 calls/min free) — wait between calls
- PostgreSQL queries taking time — add indexes (already done)
- Use `compact` output size (100 days) instead of `full` (premium feature)

---

## Next Steps (Refinement Phase)

Once MVP is stable:

1. **Add Fundamental Analysis Skill** — earnings, PE ratio, growth
2. **Add Market Share Skill** — competitive positioning
3. **Enhance Sentiment** — Reddit/Twitter scraping, insider tracking
4. **Backtesting** — validate signal accuracy on historical data
5. **White-label** — wrap for distribution as OpenClaw skill pack

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to n8n" | Verify `http://localhost:5678` is accessible, n8n is running |
| "Webhook returns 400 error" | Check API keys in `.env.trading` are valid |
| "Skills not loading in OpenClaw" | Run `openclaw doctor`, verify SKILL.md syntax |
| "Empty analysis results" | Check PostgreSQL watchlist has tickers, API responses aren't capped |
| "Rate limit errors from Alpha Vantage" | Free tier is 5/min; wait between calls (script has 1-sec delay) |

---

## Files Summary

| File | Purpose |
|------|---------|
| `trading_analysis.py` | Core analysis engine (RSI, MACD, BB, MAs) |
| `trading_webhook_server.py` | Flask server exposing webhooks for n8n |
| `technical-analysis/SKILL.md` | OpenClaw skill for technical analysis prompts |
| `sentiment-analysis/SKILL.md` | OpenClaw skill for sentiment analysis prompts |
| `.env.trading` | API keys and database config |
| `trading_intelligence` (DB) | PostgreSQL database with results |

---

## Testing Checklist

- [ ] Flask webhook server starts without errors: `python3 trading_webhook_server.py`
- [ ] Can curl the webhook: `curl http://localhost:5555/analyze/AAPL`
- [ ] OpenClaw agent can be queried: `openclaw agent --message "AAPL analysis"`
- [ ] n8n workflow runs and calls webhook
- [ ] Results are stored in PostgreSQL
- [ ] Skills are loaded (no "SKILL.md not found" errors)
- [ ] Analysis takes <10 seconds per ticker
- [ ] Daily scan can be scheduled and runs at 6:30 AM

Once all checks pass, you're ready for **Task #6: Test MVP with Real Data**.
