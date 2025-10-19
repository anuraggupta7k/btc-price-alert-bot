# BTC Price Alert Telegram Bot

Continuously monitors Binance spot ticker for `BTCUSDT` and sends a Telegram alert when price moves ±$500 from the last alert baseline. Each alert includes:
- Current BTC price
- Price change amount and direction
- Recent price chart (last 60 minutes)
- Alert timestamp (UTC)

Baseline resets to the current price after each alert to avoid duplicates.

## Requirements
- Python 3.9+
- A Telegram Bot token (via @BotFather)
- Your Telegram chat ID (use @userinfobot or other methods)

## Setup

1. Create a virtual environment and install dependencies:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Export environment variables:
```
export TELEGRAM_BOT_TOKEN="<your-telegram-bot-token>"
export TELEGRAM_CHAT_ID="<your-chat-id>"
# Optional overrides
export PRICE_DELTA_USD=500
export INTERVAL_SECONDS=3
export KLINE_INTERVAL="1m"
export KLINE_LIMIT=60
export SYMBOL="BTCUSDT"
# Dry-run mode prints alerts to console and does not send Telegram messages
export DRY_RUN=0  # set to 1 to avoid sending
```

3. Run the bot:
```
python main.py
```

## How It Works
- Polls Binance `ticker/price` endpoint every `INTERVAL_SECONDS`.
- Compares current price with stored baseline (from `state.json`).
- When price change ≥ `PRICE_DELTA_USD` (up or down), it:
  - Fetches last `KLINE_LIMIT` 1m klines for chart
  - Generates PNG chart with baseline and current price lines
  - Sends Telegram photo with a caption containing price, change, direction, and timestamp
  - Resets baseline to current price and saves to `state.json`

## Persistence
- `state.json` stores `last_alert_price` and a history of alerts.
- If `state.json` is missing, initial baseline is set from the current market price.

## Rate Limiting & Error Handling
- Uses `requests` with retries and exponential backoff for 429/5xx errors.
- On transient errors during polling, backs off up to 60s and resumes.

## Notes
- Uses `BTCUSDT` (USDT-pegged to USD) as proxy for BTC/USD.
- Ensure your bot can message your target chat (start chat with the bot or add it to a group).
- For testing without sending Telegram messages, set `DRY_RUN=1`.