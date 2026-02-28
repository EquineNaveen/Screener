import streamlit as st
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import get_sectors
from utils.market_data import get_sector_data, is_market_open

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
    <h1 style="font-size:2rem;font-weight:700;letter-spacing:-1px;margin:14px 0 4px 0;">Sectors Overview</h1>
    <p style="color:#444;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;margin:0;letter-spacing:0.5px;">
        NSE sector indices · Click any card to open TradingView
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Controls ──────────────────────────────────────────────────────────────────
sectors_map  = get_sectors()
sector_names = list(sectors_map.keys())

c1, c2 = st.columns([2, 2])
with c1:
    sort_by   = st.selectbox("Sort by", ["% Change ↓", "% Change ↑", "Name A-Z", "Stock Count ↓"])
with c2:
    filter_by = st.selectbox("Filter", ["All", "Gainers", "Losers"])

# ─── Fetch ─────────────────────────────────────────────────────────────────────
with st.spinner("Fetching sector data..."):
    sector_data = get_sector_data(tuple(sector_names), json.dumps(sectors_map))

if filter_by == "Gainers":
    sector_data = [s for s in sector_data if s["pct_change"] is not None and s["pct_change"] > 0]
elif filter_by == "Losers":
    sector_data = [s for s in sector_data if s["pct_change"] is not None and s["pct_change"] < 0]

if sort_by == "% Change ↓":
    sector_data = sorted(sector_data, key=lambda s: s["pct_change"] if s["pct_change"] is not None else -999, reverse=True)
elif sort_by == "% Change ↑":
    sector_data = sorted(sector_data, key=lambda s: s["pct_change"] if s["pct_change"] is not None else 999)
elif sort_by == "Name A-Z":
    sector_data = sorted(sector_data, key=lambda s: s["sector"])
elif sort_by == "Stock Count ↓":
    sector_data = sorted(sector_data, key=lambda s: s["stock_count"], reverse=True)

# ─── Summary ───────────────────────────────────────────────────────────────────
gainers = sum(1 for s in sector_data if s["pct_change"] is not None and s["pct_change"] > 0)
losers  = sum(1 for s in sector_data if s["pct_change"] is not None and s["pct_change"] < 0)
na      = len(sector_data) - gainers - losers
now_str = __import__('datetime').datetime.now().strftime('%H:%M:%S')

st.markdown(f"""
<div style="display:flex;gap:10px;align-items:center;margin:16px 0 24px;flex-wrap:wrap;">
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#22c55e;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▲ {gainers} Gainers</span>
    <span style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:#ef4444;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▼ {losers} Losers</span>
    <span style="background:#1a1a1a;border:1px solid #2a2a2a;color:#444;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">— {na} N/A</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#2a2a2a;">{now_str}</span>
</div>
""", unsafe_allow_html=True)

# ─── Grid ──────────────────────────────────────────────────────────────────────
cols_per_row = 4
for row_start in range(0, len(sector_data), cols_per_row):
    row  = sector_data[row_start: row_start + cols_per_row]
    cols = st.columns(cols_per_row)

    for col, s in zip(cols, row):
        pct    = s["pct_change"]
        price  = s["price"]
        tv_url = s["tv_url"]
        name   = s["sector"]
        sc     = s["stock_count"]
        src    = s["source"]

        if pct is None:
            top_c, pct_c, card_bg = "#2a2a2a", "#444",    "#161616"
            pct_disp, arrow       = "N/A",     ""
        elif pct >= 0:
            top_c, pct_c, card_bg = "#22c55e", "#22c55e", "linear-gradient(160deg,#161616 0%,rgba(34,197,94,0.04) 100%)"
            pct_disp, arrow       = f"+{pct:.2f}%", "▲ "
        else:
            top_c, pct_c, card_bg = "#ef4444", "#ef4444", "linear-gradient(160deg,#161616 0%,rgba(239,68,68,0.04) 100%)"
            pct_disp, arrow       = f"{pct:.2f}%", "▼ "

        price_line = f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#555;margin-top:4px;">&#8377;{price:,.2f}</div>' if price else ""

        card = f"""
        <div style="background:{card_bg};border:1px solid #222;border-top:2px solid {top_c};
                    border-radius:10px;padding:18px 16px;margin-bottom:12px;position:relative;overflow:hidden;">
            <div style="font-size:0.78rem;font-weight:600;color:#888;margin-bottom:10px;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{name}">
                {name}
            </div>
            <div style="font-size:1.65rem;font-weight:700;color:{pct_c};
                        font-family:'IBM Plex Mono',monospace;line-height:1;">{arrow}{pct_disp}</div>
            {price_line}
            <div style="margin-top:12px;">
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#333;">{sc} F&amp;O stocks</span>
            </div>
            <div style="position:absolute;bottom:5px;right:8px;font-family:'IBM Plex Mono',monospace;
                        font-size:0.5rem;color:#222;">{src}</div>
        </div>"""
        with col:
            st.markdown(card, unsafe_allow_html=True)

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