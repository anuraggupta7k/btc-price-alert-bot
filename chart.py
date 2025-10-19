from io import BytesIO
from datetime import datetime, timezone
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_chart(klines, baseline_price: float, current_price: float, symbol: str, change: float, direction: str, timestamp: datetime) -> bytes:
    times = [datetime.fromtimestamp(k["open_time"] / 1000, tz=timezone.utc) for k in klines]
    closes = [k["close"] for k in klines]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, closes, label=f"{symbol} close (1m)")
    ax.axhline(baseline_price, color="orange", linestyle="--", linewidth=1, label=f"Baseline ${baseline_price:,.2f}")
    ax.axhline(current_price, color=("green" if direction == "up" else "red"), linestyle=":", linewidth=1, label=f"Current ${current_price:,.2f}")

    ax.set_title(f"{symbol} Recent Price Movement — {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Price (USDT)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=8)
    fig.autofmt_xdate()

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    return buf.getvalue()