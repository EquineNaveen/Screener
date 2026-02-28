import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import get_sectors, get_metadata, get_all_fo_stocks
meta = get_metadata()
from utils.market_data import is_market_open
from utils.styles import GLOBAL_CSS

st.set_page_config(
    page_title="NSE F&O Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #222;margin-bottom:16px;">
        <div style="font-size:1.2rem;font-weight:700;letter-spacing:-0.5px;">⚡ NSE F&O</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#444;
                    margin-top:3px;text-transform:uppercase;letter-spacing:1.5px;">Dashboard</div>
    </div>""", unsafe_allow_html=True)

    st.page_link("pages/Sectors.py", label="📊  Sectors Overview")
    st.page_link("pages/Stocks.py",  label="🔍  Stocks by Sector")



# ─── Hero ──────────────────────────────────────────────────────────────────────
market_open = is_market_open()
badge_color = "#22c55e" if market_open else "#ef4444"
badge_label = "LIVE"   if market_open else "CLOSED"
badge_bg    = "rgba(34,197,94,0.08)"   if market_open else "rgba(239,68,68,0.08)"
badge_bd    = "rgba(34,197,94,0.25)"   if market_open else "rgba(239,68,68,0.25)"

st.markdown(f"""
<div style="padding:48px 0 36px 0;">
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:{badge_color};
                 background:{badge_bg};border:1px solid {badge_bd};
                 padding:4px 12px;border-radius:4px;letter-spacing:2px;">
        ● NSE {badge_label}
    </span>
    <h1 style="font-size:3rem;font-weight:700;letter-spacing:-1.5px;margin:20px 0 6px 0;line-height:1.05;
               background:linear-gradient(135deg,#f0f0f0 30%,#f5a623 100%);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        F&amp;O Market<br>Dashboard
    </h1>
    <p style="color:#444;font-size:0.78rem;font-family:'IBM Plex Mono',monospace;margin:0;letter-spacing:0.5px;">
        NSE India &nbsp;·&nbsp; Futures &amp; Options &nbsp;·&nbsp; Real-time Data
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Metric cards ──────────────────────────────────────────────────────────────
sectors  = get_sectors()
all_stks = get_all_fo_stocks()

c1, c2, c3, c4 = st.columns(4)
cards = [
    (c1, len(sectors),                          "Sectors"),
    (c2, len(all_stks),                         "F&amp;O Stocks"),
    (c3, meta["total_fo_symbols_tracked"],       "Universe"),
    (c4, sum(len(v) for v in sectors.values()), "Index Members"),
]
for col, val, label in cards:
    with col:
        st.markdown(f"""
        <div style="background:#161616;border:1px solid #222;border-radius:10px;
                    padding:22px 18px;position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;
                        background:linear-gradient(90deg,#f5a623,transparent);"></div>
            <div style="font-size:2.2rem;font-weight:700;color:#f5a623;
                        font-family:'IBM Plex Mono',monospace;line-height:1;">{val}</div>
            <div style="font-size:0.65rem;color:#444;text-transform:uppercase;
                        letter-spacing:1.5px;margin-top:6px;font-family:'IBM Plex Mono',monospace;">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#2a2a2a,transparent);margin-bottom:32px;"></div>', unsafe_allow_html=True)

# ─── Nav ───────────────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:0.62rem;color:#333;text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;font-family:IBM Plex Mono,monospace;">Navigate</div>', unsafe_allow_html=True)

n1, n2 = st.columns(2)
with n1:
    st.markdown("""
    <div style="background:#161616;border:1px solid #222;border-radius:10px;padding:22px 22px 10px 22px;">
        <div style="font-size:1.5rem;margin-bottom:8px;">📊</div>
        <div style="font-size:0.95rem;font-weight:600;color:#f0f0f0;margin-bottom:4px;">Sectors Overview</div>
        <div style="font-size:0.72rem;color:#444;margin-bottom:14px;font-family:'IBM Plex Mono',monospace;">
            Live index % change · Sort · TradingView
        </div>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/Sectors.py", label="→ Go to Sectors")

with n2:
    st.markdown("""
    <div style="background:#161616;border:1px solid #222;border-radius:10px;padding:22px 22px 10px 22px;">
        <div style="font-size:1.5rem;margin-bottom:8px;">🔍</div>
        <div style="font-size:0.95rem;font-weight:600;color:#f0f0f0;margin-bottom:4px;">Stocks by Sector</div>
        <div style="font-size:0.72rem;color:#444;margin-bottom:14px;font-family:'IBM Plex Mono',monospace;">
            Live price · % change · Sort · TradingView
        </div>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/Stocks.py", label="→ Go to Stocks")