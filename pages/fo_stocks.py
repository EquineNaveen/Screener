import streamlit as st
import streamlit.components.v1 as components
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import get_all_fo_stocks, get_sectors
from utils.market_data import get_stocks_data, get_20d_averages, is_market_open
from utils.fo_data import compute_fo_metrics
from utils.auth import require_login
require_login()
# ─── Sector Lookup ─────────────────────────────────────────────────────────────
sector_lookup = {}
for sector_name, stock_list in get_sectors().items():
    for sym in stock_list:
        sector_lookup.setdefault(sym, []).append(sector_name)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="height:1px;background:#1a1a1a;margin:4px 0 16px 0;"></div>', unsafe_allow_html=True)
    refresh_interval = st.selectbox("Auto-refresh", ["Off", "30s", "60s", "2min", "5min"], index=2)
    if st.button("↺  Refresh Now"):
        st.cache_data.clear()
        st.rerun()

# ─── Header ────────────────────────────────────────────────────────────────────
market_open = is_market_open()
bc = "#22c55e" if market_open else "#ef4444"
bl = "LIVE"    if market_open else "CLOSED"
bb = "rgba(34,197,94,0.08)"  if market_open else "rgba(239,68,68,0.08)"
bd = "rgba(34,197,94,0.25)"  if market_open else "rgba(239,68,68,0.25)"

st.markdown(f"""
<div style="padding:32px 0 20px 0;">
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:{bc};
                 background:{bb};border:1px solid {bd};padding:3px 10px;border-radius:4px;letter-spacing:2px;">
        ● NSE {bl}
    </span>
    <h1 style="font-size:2rem;font-weight:700;letter-spacing:-1px;margin:14px 0 4px 0;">All F&amp;O Stocks</h1>
    <p style="color:#444;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;margin:0;letter-spacing:0.5px;">
        LTP · % Change · Relative Volume · Relative Turnover
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Controls ──────────────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 2])
with c1:
    sort_opt = st.selectbox("Sort by", [
        "% Change ↓", "% Change ↑",
        "Rel Volume ↓", "Rel Turnover ↓",
        "Symbol A-Z", "Price ↓"
    ])
with c2:
    filter_opt = st.selectbox("Filter", ["All", "Gainers", "Losers"])

# ─── Fetch ─────────────────────────────────────────────────────────────────────
all_stocks = get_all_fo_stocks()
symbols    = tuple(all_stocks)

with st.spinner(f"Fetching live data for {len(symbols)} F&O stocks..."):
    live_rows = get_stocks_data(symbols)

with st.spinner("Fetching 20-day averages (cached daily)..."):
    averages = get_20d_averages(symbols)

rows = compute_fo_metrics(live_rows, averages)

# ─── Filter ────────────────────────────────────────────────────────────────────
if filter_opt == "Gainers":
    rows = [r for r in rows if r["pct"] is not None and r["pct"] > 0]
elif filter_opt == "Losers":
    rows = [r for r in rows if r["pct"] is not None and r["pct"] < 0]

# ─── Sort ──────────────────────────────────────────────────────────────────────
if sort_opt == "% Change ↓":
    rows = sorted(rows, key=lambda r: (r["pct"] is None, -(r["pct"] if r["pct"] is not None else 0)))
elif sort_opt == "% Change ↑":
    rows = sorted(rows, key=lambda r: (r["pct"] is None,  (r["pct"] if r["pct"] is not None else 0)))
elif sort_opt == "Rel Volume ↓":
    rows = sorted(rows, key=lambda r: (r["rel_vol"] is None, -(r["rel_vol"] if r["rel_vol"] is not None else 0)))
elif sort_opt == "Rel Turnover ↓":
    rows = sorted(rows, key=lambda r: (r["rel_turnover"] is None, -(r["rel_turnover"] if r["rel_turnover"] is not None else 0)))
elif sort_opt == "Symbol A-Z":
    rows = sorted(rows, key=lambda r: r["symbol"])
elif sort_opt == "Price ↓":
    rows = sorted(rows, key=lambda r: (r["price"] is None, -(r["price"] if r["price"] is not None else 0)))

# ─── Summary bar ───────────────────────────────────────────────────────────────
g       = sum(1 for r in rows if r["pct"] is not None and r["pct"] > 0)
l       = sum(1 for r in rows if r["pct"] is not None and r["pct"] < 0)
n       = len(rows) - g - l
now_str = __import__('datetime').datetime.now().strftime('%H:%M:%S')

st.markdown(f"""
<div style="display:flex;gap:10px;align-items:center;margin:14px 0 16px;flex-wrap:wrap;">
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#22c55e;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▲ {g} Gainers</span>
    <span style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:#ef4444;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▼ {l} Losers</span>
    <span style="background:#1a1a1a;border:1px solid #2a2a2a;color:#444;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">— {n} N/A</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#2a2a2a;">{now_str} · {len(rows)} stocks</span>
</div>
""", unsafe_allow_html=True)

# ─── Table ─────────────────────────────────────────────────────────────────────
tbody = ""
for i, r in enumerate(rows, 1):
    sym          = r["symbol"]
    price        = r["price"]
    pct          = r["pct"]
    tv_url       = r["tv_url"]
    volume       = r.get("volume")
    rel_vol      = r.get("rel_vol")
    rel_turnover = r.get("rel_turnover")

    sectors     = sector_lookup.get(sym, [])
    sector_str  = ", ".join(sectors) if sectors else "—"

    price_str  = f"&#8377;{price:,.2f}" if price is not None else "&#8212;"
    volume_str = f"{volume:,}" if volume is not None else "&#8212;"

    if pct is None:
        pct_cell = '<span style="color:#888;font-family:IBM Plex Mono,monospace;font-size:0.82rem;">&#8212;</span>'
    elif pct >= 0:
        pct_cell = f'<span style="color:#22c55e;font-weight:600;font-family:IBM Plex Mono,monospace;font-size:0.82rem;">&#9650; +{pct:.2f}%</span>'
    else:
        pct_cell = f'<span style="color:#ef4444;font-weight:600;font-family:IBM Plex Mono,monospace;font-size:0.82rem;">&#9660; {pct:.2f}%</span>'

    rv_str = f"{rel_vol:.2f}"      if rel_vol      is not None else "&#8212;"
    rt_str = f"{rel_turnover:.2f}" if rel_turnover is not None else "&#8212;"

    row_bg = "#171717" if i % 2 == 0 else "#161616"

    tbody += f"""<tr style="background:{row_bg};border-bottom:1px solid #1e1e1e;">
        <td style="padding:10px 14px;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#2a2a2a;width:36px;">{i}</td>
        <td style="padding:10px 14px;">
            <a href="{tv_url}" target="_blank"
               style="font-family:'IBM Plex Mono',monospace;font-size:0.88rem;font-weight:600;
                      color:#f5a623;text-decoration:none;letter-spacing:0.3px;">{sym}</a>
        </td>
        <td style="padding:10px 14px;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#666;max-width:220px;">{sector_str}</td>
        <td style="padding:10px 14px;font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#c0c0c0;">{price_str}</td>
        <td style="padding:10px 14px;">{pct_cell}</td>
        <td style="padding:10px 14px;font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#c0c0c0;">{volume_str}</td>
        <td style="padding:10px 14px;font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#c0c0c0;">{rv_str}</td>
        <td style="padding:10px 14px;font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#c0c0c0;">{rt_str}</td>
    </tr>"""

th = "padding:10px 14px;text-align:left;font-family:'IBM Plex Mono',monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:1.5px;color:#888;font-weight:500;background:#111;"

table_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>* {{box-sizing:border-box;margin:0;padding:0;}} body {{background:transparent;}}</style>
</head><body>
<div style="border:1px solid #1e1e1e;border-radius:10px;overflow:hidden;">
    <table style="width:100%;border-collapse:collapse;">
        <thead>
            <tr style="border-bottom:1px solid #222;">
                <th style="{th}width:36px;">#</th>
                <th style="{th}">Symbol</th>
                <th style="{th}">Sector</th>
                <th style="{th}">LTP</th>
                <th style="{th}">Change</th>
                <th style="{th}">Volume</th>
                <th style="{th}">Rel Volume</th>
                <th style="{th}">Rel Turnover</th>
            </tr>
        </thead>
        <tbody>{tbody}</tbody>
    </table>
</div>
</body></html>"""

row_height   = 42
header_h     = 42
total_height = header_h + (len(rows) * row_height) + 20
components.html(table_html, height=total_height, scrolling=False)

# ─── Auto-refresh ──────────────────────────────────────────────────────────────
interval_map = {"30s": 30, "60s": 60, "2min": 120, "5min": 300}
if refresh_interval != "Off":
    if market_open:
        secs = interval_map[refresh_interval]
        st.markdown(
            f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;'
            f'color:#1e1e1e;text-align:center;margin-top:24px;">'
            f'auto-refresh every {refresh_interval}</div>',
            unsafe_allow_html=True)
        time.sleep(secs)
        st.cache_data.clear()
        st.rerun()
    else:
        st.markdown(
            '<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;'
            'color:#2a2a2a;text-align:center;margin-top:24px;">'
            'auto-refresh paused — market closed</div>',
            unsafe_allow_html=True)