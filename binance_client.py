import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BinanceClient:
    def __init__(self, base_url: str = "https://api.binance.com", timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_price(self, symbol: str) -> float:
        url = f"{self.base_url}/api/v3/ticker/price"
        params = {"symbol": symbol}
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        price = float(data["price"])
        return price

    def get_klines(self, symbol: str, interval: str = "1m", limit: int = 60):
        url = f"{self.base_url}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        klines = []
        for k in data:
            # [open_time, open, high, low, close, volume, close_time, ...]
            klines.append(
                {
                    "open_time": k[0],
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "close_time": k[6],
                }
            )
        return klines