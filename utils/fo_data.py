"""
Shared utility: compute Relative Volume, Relative Turnover, Signal
for any list of stocks given live data + 20d averages.

Used by both pages/fo_stocks.py and pages/stocks.py.
"""


def compute_fo_metrics(live_rows: list, averages: dict) -> list:
    """
    Merge live data with 20d averages and compute derived metrics.

    live_rows : list of dicts from get_stocks_data()
                each has: symbol, price, pct, volume, tv_url
    averages  : dict from get_20d_averages()
                each key: symbol -> { avg_vol, avg_price }

    Returns list of dicts with extra keys:
        volume, turnover, avg_vol, avg_price, avg_turnover,
        rel_vol, rel_turnover, signal
    """
    enriched = []
    for r in live_rows:
        sym    = r["symbol"]
        price  = r.get("price")
        volume = r.get("volume")
        pct    = r.get("pct")
        tv_url = r.get("tv_url", f"https://www.tradingview.com/chart/?symbol=NSE:{sym}")

        avg    = averages.get(sym, {})
        avg_vol   = avg.get("avg_vol")
        avg_price = avg.get("avg_price")

        # today's turnover
        turnover = (price * volume) if (price is not None and volume is not None) else None

        # 20d avg turnover
        avg_turnover = (avg_vol * avg_price) if (avg_vol is not None and avg_price is not None) else None

        # relative metrics
        rel_vol = round(volume / avg_vol, 2) if (volume is not None and avg_vol and avg_vol > 0) else None
        rel_turnover = round(turnover / avg_turnover, 2) if (turnover is not None and avg_turnover and avg_turnover > 0) else None

        # signal
        if rel_vol is not None and rel_turnover is not None and rel_vol > 2 and rel_turnover > 2:
            signal = "Momentum 🚀"
        else:
            signal = "No Signal"

        enriched.append({
            "symbol":       sym,
            "price":        price,
            "pct":          pct,
            "volume":       volume,
            "turnover":     turnover,
            "avg_vol":      avg_vol,
            "avg_price":    avg_price,
            "avg_turnover": avg_turnover,
            "rel_vol":      rel_vol,
            "rel_turnover": rel_turnover,
            "signal":       signal,
            "tv_url":       tv_url,
        })
    return enriched