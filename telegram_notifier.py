import requests


def send_photo(token: str, chat_id: str, image_bytes: bytes, caption: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {"photo": ("chart.png", image_bytes, "image/png")}
    data = {"chat_id": chat_id, "caption": caption}
    resp = requests.post(url, files=files, data=data, timeout=20)
    if resp.status_code != 200:
        raise Exception(f"Telegram sendPhoto failed: {resp.status_code} {resp.text}")
    return True