import json
import os
import threading

# Watchlists stored at project root: watchlists.json
_WATCHLIST_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "watchlists.json")
_lock = threading.Lock()


def _load_all() -> dict:
    """Load the full watchlists.json file."""
    if not os.path.exists(_WATCHLIST_PATH):
        return {}
    try:
        with open(_WATCHLIST_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_all(data: dict):
    """Save the full watchlists.json file."""
    with open(_WATCHLIST_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_watchlist(username: str) -> list:
    """
    Return watchlist for a user.
    Each item: { "symbol": "RELIANCE", "note": "..." }
    """
    with _lock:
        data = _load_all()
        return data.get(username, [])


def add_to_watchlist(username: str, symbol: str, note: str = ""):
    """Add a stock to user's watchlist. Ignores duplicates."""
    with _lock:
        data = _load_all()
        wl   = data.get(username, [])
        # check duplicate
        if any(item["symbol"] == symbol for item in wl):
            return False  # already exists
        wl.append({"symbol": symbol, "note": note})
        data[username] = wl
        _save_all(data)
        return True


def remove_from_watchlist(username: str, symbol: str):
    """Remove a stock from user's watchlist."""
    with _lock:
        data = _load_all()
        wl   = data.get(username, [])
        data[username] = [item for item in wl if item["symbol"] != symbol]
        _save_all(data)


def update_note(username: str, symbol: str, note: str):
    """Update the note for a stock in user's watchlist."""
    with _lock:
        data = _load_all()
        wl   = data.get(username, [])
        for item in wl:
            if item["symbol"] == symbol:
                item["note"] = note
                break
        data[username] = wl
        _save_all(data)