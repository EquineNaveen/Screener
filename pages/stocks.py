import streamlit as st
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import get_sectors
from utils.market_data import get_stocks_data, is_market_open

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
    <h1 style="font-size:2rem;font-weight:700;letter-spacing:-1px;margin:14px 0 4px 0;">Stocks by Sector</h1>
    <p style="color:#444;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;margin:0;letter-spacing:0.5px;">
        Select a sector · Click symbol to open TradingView chart
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Controls ──────────────────────────────────────────────────────────────────
sectors_map  = get_sectors()
sector_names = list(sectors_map.keys())

c1, c2, c3 = st.columns([3, 2, 2])
with c1:
    selected   = st.selectbox("Sector", sector_names)
with c2:
    sort_opt   = st.selectbox("Sort by", ["% Change ↓", "% Change ↑", "Symbol A-Z", "Price ↓"])
with c3:
    filter_opt = st.selectbox("Filter", ["All", "Gainers", "Losers"])

stocks = sectors_map.get(selected, [])

st.markdown(f"""
<div style="background:#161616;border:1px solid #222;border-left:2px solid #f5a623;
            border-radius:8px;padding:12px 16px;margin:14px 0 6px 0;">
    <span style="font-size:0.9rem;font-weight:600;">{selected}</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#444;margin-left:10px;">
        {len(stocks)} F&O stocks
    </span>
</div>
""", unsafe_allow_html=True)

if not stocks:
    st.warning("No F&O stocks found for this sector.")
    st.stop()

# ─── Fetch ─────────────────────────────────────────────────────────────────────
with st.spinner(f"Fetching data for {len(stocks)} stocks..."):
    rows = get_stocks_data(tuple(stocks))

# ─── Filter ────────────────────────────────────────────────────────────────────
if filter_opt == "Gainers":
    rows = [r for r in rows if r["pct"] is not None and r["pct"] > 0]
elif filter_opt == "Losers":
    rows = [r for r in rows if r["pct"] is not None and r["pct"] < 0]

# ─── Sort ──────────────────────────────────────────────────────────────────────
if sort_opt == "% Change ↓":
    rows = sorted(rows, key=lambda r: r["pct"] if r["pct"] is not None else -999, reverse=True)
elif sort_opt == "% Change ↑":
    rows = sorted(rows, key=lambda r: r["pct"] if r["pct"] is not None else 999)
elif sort_opt == "Symbol A-Z":
    rows = sorted(rows, key=lambda r: r["symbol"])
elif sort_opt == "Price ↓":
    rows = sorted(rows, key=lambda r: r["price"] if r["price"] is not None else -1, reverse=True)

# ─── Summary ───────────────────────────────────────────────────────────────────
g = sum(1 for r in rows if r["pct"] is not None and r["pct"] > 0)
l = sum(1 for r in rows if r["pct"] is not None and r["pct"] < 0)
n = len(rows) - g - l
now_str = __import__('datetime').datetime.now().strftime('%H:%M:%S')

st.markdown(f"""
<div style="display:flex;gap:10px;align-items:center;margin:14px 0 16px;flex-wrap:wrap;">
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#22c55e;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▲ {g} Gainers</span>
    <span style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:#ef4444;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▼ {l} Losers</span>
    <span style="background:#1a1a1a;border:1px solid #2a2a2a;color:#444;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">— {n} N/A</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#2a2a2a;">{now_str}</span>
</div>
""", unsafe_allow_html=True)

# ─── Build full table as single HTML string ────────────────────────────────────
tbody = ""
for i, r in enumerate(rows, 1):
    sym    = r["symbol"]
    price  = r["price"]
    pct    = r["pct"]
    tv_url = r["tv_url"]

    price_str = f"&#8377;{price:,.2f}" if price is not None else "&#8212;"

    if pct is None:
        pct_cell = '<span style="color:#333;font-family:IBM Plex Mono,monospace;font-size:0.82rem;">&#8212;</span>'
    elif pct >= 0:
        pct_cell = f'<span style="color:#22c55e;font-weight:600;font-family:IBM Plex Mono,monospace;font-size:0.82rem;">&#9650; +{pct:.2f}%</span>'
    else:
        pct_cell = f'<span style="color:#ef4444;font-weight:600;font-family:IBM Plex Mono,monospace;font-size:0.82rem;">&#9660; {pct:.2f}%</span>'

    row_bg = "#171717" if i % 2 == 0 else "#161616"

    tbody += f"""<tr style="background:{row_bg};border-bottom:1px solid #1e1e1e;">
        <td style="padding:11px 14px;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#2a2a2a;width:40px;">{i}</td>
        <td style="padding:11px 14px;">
            <a href="{tv_url}" target="_blank"
               style="font-family:'IBM Plex Mono',monospace;font-size:0.88rem;font-weight:600;
                      color:#f5a623;text-decoration:none;letter-spacing:0.3px;">
                {sym}
            </a>
        </td>
        <td style="padding:11px 14px;font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#c0c0c0;">{price_str}</td>
        <td style="padding:11px 14px;">{pct_cell}</td>
    </tr>"""

th_style = "padding:10px 14px;text-align:left;font-family:'IBM Plex Mono',monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:1.5px;color:#333;font-weight:500;background:#111;"

table_html = f"""
<div style="border:1px solid #1e1e1e;border-radius:10px;overflow:hidden;">
    <table style="width:100%;border-collapse:collapse;">
        <thead>
            <tr style="border-bottom:1px solid #222;">
                <th style="{th_style}width:40px;">#</th>
                <th style="{th_style}">Symbol</th>
                <th style="{th_style}">Price</th>
                <th style="{th_style}">Change</th>
            </tr>
        </thead>
        <tbody>{tbody}</tbody>
    </table>
</div>"""

st.markdown(table_html, unsafe_allow_html=True)

# ─── Auto-refresh (only when market is open) ───────────────────────────────────
interval_map = {"30s": 30, "60s": 60, "2min": 120, "5min": 300}
if refresh_interval != "Off":
    if market_open:
        secs = interval_map[refresh_interval]
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#1e1e1e;text-align:center;margin-top:24px;">auto-refresh every {refresh_interval}</div>', unsafe_allow_html=True)
        time.sleep(secs)
        st.cache_data.clear()
        st.rerun()
    else:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#2a2a2a;text-align:center;margin-top:24px;">auto-refresh paused — market closed</div>', unsafe_allow_html=True)