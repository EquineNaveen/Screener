"""
Run: python debug3.py
Check exactly what yfinance fast_info returns for volume fields
"""
import yfinance as yf

test_syms = ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS"]

for ns in test_syms:
    print(f"\n=== {ns} ===")
    t = yf.Ticker(ns)
    fi = t.fast_info
    print(f"  All fast_info keys: {list(fi)}")
    print(f"  three_month_average_volume : {fi.get('three_month_average_volume')}")
    print(f"  regular_market_volume      : {fi.get('regular_market_volume')}")
    print(f"  shares_outstanding         : {fi.get('shares_outstanding')}")

    # Also check history for today's volume
    hist = t.history(period="2d")
    print(f"  history tail:\n{hist[['Volume','Close']].tail(2)}")