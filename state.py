import json
import os
from typing import Dict, Any


def load_state(state_file: str) -> Dict[str, Any]:
    if not os.path.exists(state_file):
        return {"last_alert_price": None, "alerts": []}
    try:
        with open(state_file, "r") as f:
            return json.load(f)
    except Exception:
        return {"last_alert_price": None, "alerts": []}


def save_state(state_file: str, state: Dict[str, Any]) -> None:
    tmp_file = state_file + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(state, f)
    os.replace(tmp_file, state_file)