import os
from dataclasses import dataclass


@dataclass
class Config:
    symbol: str = os.environ.get("SYMBOL", "BTCUSDT")
    price_delta_usd: float = float(os.environ.get("PRICE_DELTA_USD", "500"))
    poll_interval_seconds: int = int(os.environ.get("INTERVAL_SECONDS", "3"))
    kline_interval: str = os.environ.get("KLINE_INTERVAL", "1m")
    kline_limit: int = int(os.environ.get("KLINE_LIMIT", "60"))
    state_file: str = os.environ.get("STATE_FILE", "state.json")
    telegram_bot_token: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.environ.get("TELEGRAM_CHAT_ID", "")
    dry_run: bool = os.environ.get("DRY_RUN", "0") == "1"