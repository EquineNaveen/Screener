import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor

IST = ZoneInfo("Asia/Kolkata")

# -----------------------------------------------
# Sector Index Ticker Mapping
# -----------------------------------------------
SECTOR_TICKER_MAP = {
    "NIFTY REALTY":             "^CNXREALTY",
    "NIFTY AUTO":               "^CNXAUTO",
    "NIFTY FMCG":               "^CNXFMCG",
    "NIFTY METAL":              "^CNXMETAL",
    "NIFTY FINANCIAL SERVICES": "^CNXFINANCE",
    "NIFTY PHARMA":             "^CNXPHARMA",
    "NIFTY INDIA CONSUMPTION":  "^CNXCONSUMPTION",
    "NIFTY HEALTHCARE INDEX":   "^CNXHEALTHCARE",
    "NIFTY PRIVATE BANK":       "^NIFTYPVTBANK",
    "NIFTY CHEMICALS":          "^CNXCHEMICALS",
    "NIFTY MID SELECT":         "^NIFTYMIDSELECT",
    "NIFTY INFRASTRUCTURE":     "^CNXINFRA",
    "NIFTY COMMODITIES":        "^CNXCOMMODITIES",
    "NIFTY INDIA DEFENCE":      "^NIFTYINDIADEFENCE",
    "NIFTY PSU BANK":           "^CNXPSUBANK",
    "NIFTY ENERGY":             "^CNXENERGY",
    "NIFTY OIL & GAS":          "^CNXOILGAS",
    "NIFTY IT":                 "^CNXIT",
    "NIFTY CONSUMER DURABLES":  "^NIFTYCONSUMERDURAB",
    "NIFTY MEDIA":              "^CNXMEDIA",
}

SECTOR_NSE_API_MAP = {
    "NIFTY REALTY":                  "NIFTY REALTY",
    "NIFTY AUTO":                    "NIFTY AUTO",
    "NIFTY FMCG":                    "NIFTY FMCG",
    "NIFTY METAL":                   "NIFTY METAL",
    "NIFTY FINANCIAL SERVICES":      "NIFTY FINANCIAL SERVICES",
    "NIFTY PHARMA":                  "NIFTY PHARMA",
    "NIFTY INDIA CONSUMPTION":       "NIFTY INDIA CONSUMPTION",
    "NIFTY HEALTHCARE INDEX":        "NIFTY HEALTHCARE INDEX",
    "NIFTY PRIVATE BANK":            "NIFTY PRIVATE BANK",
    "NIFTY CHEMICALS":               "NIFTY CHEMICALS",
    "NIFTY MID SELECT":              "NIFTY MID SELECT",
    "NIFTY INFRASTRUCTURE":          "NIFTY INFRASTRUCTURE",
    "NIFTY COMMODITIES":             "NIFTY COMMODITIES",
    "NIFTY INDIA DEFENCE":           "NIFTY INDIA DEFENCE",
    "NIFTY PSU BANK":                "NIFTY PSU BANK",
    "NIFTY ENERGY":                  "NIFTY ENERGY",
    "NIFTY OIL & GAS":               "NIFTY OIL & GAS",
    "NIFTY IT":                      "NIFTY IT",
    "NIFTY CONSUMER DURABLES":       "NIFTY CONSUMER DURABLES",
    "NIFTY CAPITAL MARKET":          "NIFTY CAPITAL MARKET",
    "NIFTY CPSE":                    "NIFTY CPSE",
    "NIFTY CEMENT":                  "NIFTY CEMENT",
    "NIFTY PSE":                     "NIFTY PSE",
    "NIFTY MIDSMALL IT & TELECOM":   "NIFTY MIDSMALL IT & TELECOM",
}

SECTOR_TV_MAP = {
    "NIFTY REALTY":                  "NSE:CNXREALTY",
    "NIFTY AUTO":                    "NSE:CNXAUTO",
    "NIFTY FMCG":                    "NSE:CNXFMCG",
    "NIFTY METAL":                   "NSE:CNXMETAL",
    "NIFTY FINANCIAL SERVICES":      "NSE:CNXFINANCE",
    "NIFTY PHARMA":                  "NSE:CNXPHARMA",
    "NIFTY INDIA CONSUMPTION":       "NSE:CNXCONSUMPTION",
    "NIFTY HEALTHCARE INDEX":        "NSE:NIFTY_HEALTHCARE",
    "NIFTY PRIVATE BANK":            "NSE:NIFTYPVTBANK",
    "NIFTY CHEMICALS":               "NSE:NIFTY_CHEMICALS",
    "NIFTY MID SELECT":              "NSE:NIFTY_MID_SELECT",
    "NIFTY INFRASTRUCTURE":          "NSE:CNXINFRA",
    "NIFTY COMMODITIES":             "NSE:CNXCOMMODITIES",
    "NIFTY INDIA DEFENCE":           "NSE:NIFTY_IND_DEFENCE",
    "NIFTY PSU BANK":                "NSE:CNXPSUBANK",
    "NIFTY ENERGY":                  "NSE:CNXENERGY",
    "NIFTY OIL & GAS":               "NSE:NIFTY_OIL_AND_GAS",
    "NIFTY IT":                      "NSE:CNXIT",
    "NIFTY CONSUMER DURABLES":       "NSE:NIFTY_CONSR_DURBL",
    "NIFTY CAPITAL MARKET":          "NSE:NIFTY_CAPITAL_MKT",
    "NIFTY CPSE":                    "NSE:CPSE",
    "NIFTY CEMENT":                  "NSE:NIFTY_CEMENT",
    "NIFTY PSE":                     "NSE:NIFTY_PSE",
    "NIFTY MIDSMALL IT & TELECOM":   "NSE:NIFTY_MS_IT_TELCM",
}


# -----------------------------------------------
# IST Helpers
# -----------------------------------------------

def _ist_now() -> datetime:
    """Current IST-aware datetime."""
    return datetime.now(IST)


def _current_trading_date() -> date:
    """
    Returns the 'active trading date' in IST.

    Before 9:15 AM IST  -> return yesterday's date.
      Pre-open window; today's market hasn't started yet.
      Returning yesterday prevents a premature re-fetch on
      an early-morning Streamlit auto-refresh rerun.

    From 9:15 AM onward -> return today's date.
      Market is open or has already opened/closed for the day.

    This means get_20d_averages() fetches exactly once per trading
    day, triggered on the first call at or after 9:15 AM IST.
    """
    now    = _ist_now()
    cutoff = now.replace(hour=9, minute=15, second=0, microsecond=0)
    if now < cutoff:
        return (now - timedelta(days=1)).date()
    return now.date()


# -----------------------------------------------
# Market Status
# -----------------------------------------------

def is_market_open() -> bool:
    now = _ist_now()
    if now.weekday() >= 5:
        return False
    market_open  = now.replace(hour=9,  minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close


# -----------------------------------------------
# Sector Data Fetchers
# -----------------------------------------------

def _fetch_nse_index(index_name: str):
    """Primary: NSE API direct fetch for sector index % change."""
    import requests, urllib.parse, time
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept":     "application/json",
        "Referer":    "https://www.nseindia.com/",
    }
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        time.sleep(0.2)
        encoded = urllib.parse.quote(index_name)
        url     = f"https://www.nseindia.com/api/equity-stockIndices?index={encoded}"
        resp    = session.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            records = resp.json().get("data", [])
            if records:
                idx  = records[0]
                last = idx.get("last") or idx.get("lastPrice") or idx.get("indexValue")
                pct  = idx.get("pChange") or idx.get("percentChange")
                if pct is not None:
                    return round(float(pct), 2), (round(float(last), 2) if last else None)
                prev = idx.get("previousClose") or idx.get("previousDay")
                if last and prev and float(prev) != 0:
                    pct = ((float(last) - float(prev)) / float(prev)) * 100
                    return round(pct, 2), round(float(last), 2)
    except Exception:
        pass
    return None, None


def _fetch_yfinance_index(ticker_sym: str):
    """Fallback: yfinance for sector index."""
    try:
        t    = yf.Ticker(ticker_sym)
        info = t.fast_info
        prev = info.get("previousClose") or info.get("regular_market_previous_close")
        curr = info.get("lastPrice")     or info.get("regular_market_price")
        if prev and curr and float(prev) != 0:
            pct = ((float(curr) - float(prev)) / float(prev)) * 100
            return round(pct, 2), round(float(curr), 2)
    except Exception:
        pass
    return None, None


def _fetch_avg_pct(stocks: list):
    """Last resort: average % change of up to 15 constituent stocks."""
    if not stocks:
        return None, None
    syms = [s + ".NS" for s in stocks[:15]]
    try:
        raw = yf.download(syms, period="2d", progress=False, auto_adjust=True)
        if not raw.empty and "Close" in raw:
            closes = raw["Close"]
            if len(closes) >= 2:
                pct_s = ((closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2]) * 100
                return round(float(pct_s.mean()), 2), None
    except Exception:
        pass
    return None, None


def _fetch_one_sector(args):
    """Fetch a single sector — NSE API -> yfinance index -> avg of stocks."""
    sector, sector_stocks = args
    nse_name   = SECTOR_NSE_API_MAP.get(sector)
    ticker_sym = SECTOR_TICKER_MAP.get(sector)
    tv_sym     = SECTOR_TV_MAP.get(sector, "")
    tv_url     = f"https://www.tradingview.com/chart/?symbol={tv_sym}" if tv_sym else "#"
    pct, price = None, None
    source     = "n/a"

    if nse_name:
        pct, price = _fetch_nse_index(nse_name)
        if pct is not None:
            source = "NSE"

    if pct is None and ticker_sym:
        pct, price = _fetch_yfinance_index(ticker_sym)
        if pct is not None:
            source = "YF"

    if pct is None:
        pct, price = _fetch_avg_pct(sector_stocks.get(sector, []))
        if pct is not None:
            source = "avg"

    return sector, {
        "sector":      sector,
        "pct_change":  pct,
        "price":       price,
        "tv_url":      tv_url,
        "stock_count": len(sector_stocks.get(sector, [])),
        "source":      source,
    }


@st.cache_data(ttl=60)
def get_sector_data(sector_names: tuple, sector_stocks_json: str):
    """
    Fetch % change for each sector.
    Priority: NSE API -> yfinance index -> avg of stocks.
    sector_stocks_json: JSON string of sectors dict (hashable for st.cache_data).
    """
    import json
    sector_stocks = json.loads(sector_stocks_json)
    args          = [(sector, sector_stocks) for sector in sector_names]
    results_map   = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        for sector, result in pool.map(_fetch_one_sector, args):
            results_map[sector] = result

    return [results_map[s] for s in sector_names]


# -----------------------------------------------
# Stock Data Fetcher
# -----------------------------------------------

def _fetch_one_stock(args):
    """Fetch a single stock — price, pct, volume via yfinance fast_info."""
    sym, ns_sym        = args
    pct, price, volume = None, None, None
    try:
        tickers = yf.Tickers(ns_sym)
        t       = tickers.tickers.get(ns_sym)
        if t:
            info = t.fast_info
            prev = info.get("previousClose") or info.get("regularMarketPreviousClose")
            curr = info.get("lastPrice")
            vol  = info.get("lastVolume")
            if prev and curr and float(prev) != 0:
                pct   = round(((float(curr) - float(prev)) / float(prev)) * 100, 2)
                price = round(float(curr), 2)
            if vol is not None:
                volume = int(vol)
    except Exception:
        pass

    return {
        "symbol": sym,
        "price":  price,
        "pct":    pct,
        "volume": volume,
        "tv_url": f"https://www.tradingview.com/chart/?symbol=NSE:{sym}",
    }


@st.cache_data(ttl=60)
def get_stocks_data(symbols: tuple):
    """
    Fetch price, pct, volume for NSE stocks via yfinance fast_info.
    Returns list of dicts. Cached for 60 seconds.
    """
    ns_syms = [s + ".NS" for s in symbols]
    args    = list(zip(symbols, ns_syms))

    results_map = {}
    with ThreadPoolExecutor(max_workers=30) as pool:
        for result in pool.map(_fetch_one_stock, args):
            results_map[result["symbol"]] = result

    return [results_map[s] for s in symbols]


# -----------------------------------------------
# 20-Day Averages  (session_state cache — no cron, no disk)
# -----------------------------------------------

def get_20d_averages(symbols: tuple) -> dict:
    """
    Returns 20-day average volume and average close price per symbol.

    Cache strategy (Streamlit Cloud compatible — no cron, no disk):
    ─────────────────────────────────────────────────────────────────
    Data is stored in st.session_state["20d_avg_cache"] as:
        {
            "trading_date": date,        # IST date object — cache key
            "fetched_at":   str,         # human-readable IST timestamp
            "data":         dict,        # {symbol: {avg_vol, avg_price}}
        }

    How the date key works:
      - _current_trading_date() returns yesterday before 9:15 AM IST
        (pre-open window — no premature re-fetch on early reruns).
      - From 9:15 AM onward it returns today's date.
      - When the stored trading_date no longer matches the current one,
        the cache is discarded and a fresh yfinance download runs.

    Result: exactly ONE yfinance fetch per trading day, triggered on
    the first Streamlit run at or after 9:15 AM IST. All subsequent
    reruns (auto-refresh, manual refresh, page navigation) within the
    same session hit the in-memory cache instantly.

    On Streamlit Cloud, the server typically restarts overnight which
    clears session_state automatically — so the next morning's first
    load always gets a clean fetch.
    """
    trading_date = _current_trading_date()
    state_key    = "20d_avg_cache"

    # ── Hit: same trading day already fetched ─────────────────────────────────
    cached = st.session_state.get(state_key)
    if cached and cached.get("trading_date") == trading_date:
        return cached["data"]

    # ── Miss: new trading day or first ever load — fetch from yfinance ────────
    result  = {s: {"avg_vol": None, "avg_price": None} for s in symbols}
    ns_syms = [s + ".NS" for s in symbols]

    try:
        raw = yf.download(ns_syms, period="20d", progress=False, auto_adjust=True)
        if not raw.empty:
            close_df  = raw["Close"]  if "Close"  in raw.columns.get_level_values(0) else None
            volume_df = raw["Volume"] if "Volume" in raw.columns.get_level_values(0) else None

            for sym, ns in zip(symbols, ns_syms):
                avg_vol, avg_price = None, None
                try:
                    col = volume_df[ns] if (volume_df is not None and ns in volume_df.columns) else None
                    if col is not None:
                        avg_vol = float(col.dropna().mean())
                except Exception:
                    pass
                try:
                    col = close_df[ns] if (close_df is not None and ns in close_df.columns) else None
                    if col is not None:
                        avg_price = float(col.dropna().mean())
                except Exception:
                    pass
                result[sym] = {"avg_vol": avg_vol, "avg_price": avg_price}

    except Exception as e:
        st.warning(f"[20d averages] yfinance fetch failed: {e}")

    # ── Store in session_state — keyed by IST trading date ───────────────────
    st.session_state[state_key] = {
        "trading_date": trading_date,
        "fetched_at":   _ist_now().strftime("%d %b %Y  %H:%M:%S IST"),
        "data":         result,
    }

    return result