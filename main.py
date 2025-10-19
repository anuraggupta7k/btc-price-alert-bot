import time
from datetime import datetime, timezone
import logging

from config import Config
from binance_client import BinanceClient
from chart import generate_chart
from telegram_notifier import send_photo
from state import load_state, save_state


def format_usd(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.2f}"


def build_caption(symbol: str, current_price: float, baseline_price: float, delta: float, direction: str, ts: datetime) -> str:
    arrow = "⬆️" if direction == "up" else "⬇️"
    lines = [
        f"{arrow} BTC Price Alert ({symbol})",
        f"Current price: ${current_price:,.2f}",
        f"Change vs baseline: {format_usd(delta)} ({direction})",
        f"Baseline (reset): ${baseline_price:,.2f}",
        f"Timestamp: {ts.strftime('%Y-%m-%d %H:%M:%S %Z')}",
    ]
    return "\n".join(lines)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    cfg = Config()
    client = BinanceClient()
    state = load_state(cfg.state_file)

    # Initialize baseline from stored state or current price
    if state["last_alert_price"] is None:
        logging.info("No baseline found. Fetching initial price for baseline...")
        try:
            price = client.get_price(cfg.symbol)
            state["last_alert_price"] = price
            save_state(cfg.state_file, state)
            logging.info(f"Initial baseline set to ${price:,.2f}")
        except Exception as e:
            logging.error(f"Failed to initialize baseline: {e}")
            return

    baseline = state["last_alert_price"]
    backoff = 1

    while True:
        try:
            current = client.get_price(cfg.symbol)
            delta = current - baseline

            if delta >= cfg.price_delta_usd or delta <= -cfg.price_delta_usd:
                direction = "up" if delta > 0 else "down"
                ts = datetime.now(timezone.utc)
                klines = client.get_klines(cfg.symbol, interval=cfg.kline_interval, limit=cfg.kline_limit)
                image_bytes = generate_chart(
                    klines,
                    baseline_price=baseline,
                    current_price=current,
                    symbol=cfg.symbol,
                    change=delta,
                    direction=direction,
                    timestamp=ts,
                )
                caption = build_caption(cfg.symbol, current, baseline, delta, direction, ts)

                if cfg.dry_run:
                    logging.info("DRY_RUN enabled. Alert not sent.")
                    logging.info("\n" + caption)
                else:
                    # Check Telegram configs
                    if not cfg.telegram_bot_token or not cfg.telegram_chat_id:
                        logging.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID. Enable DRY_RUN or set env vars.")
                    else:
                        send_photo(cfg.telegram_bot_token, cfg.telegram_chat_id, image_bytes, caption)
                        logging.info(f"Alert sent. Price moved {format_usd(delta)} from baseline.")
                # Reset baseline to current
                baseline = current
                state["last_alert_price"] = current
                state["alerts"].append({"timestamp": ts.isoformat(), "baseline": baseline, "delta": delta, "direction": direction})
                save_state(cfg.state_file, state)
                # Reset backoff
                backoff = 1

            time.sleep(cfg.poll_interval_seconds)
        except Exception as e:
            logging.warning(f"Error during polling: {e}. Backing off for {backoff}s.")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)


if __name__ == "__main__":
    main()