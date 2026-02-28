import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.styles import GLOBAL_CSS

# ─── st.navigation MUST be called before set_page_config ──────────────────────
# Files are lowercase: sectors.py and stocks.py — NOT Sectors.py / Stocks.py

sectors_page = st.Page("pages/sectors.py", title="Sectors Overview")
stocks_page  = st.Page("pages/stocks.py",  title="Stocks by Sector")

pg = st.navigation(
    {"NSE F&O": [sectors_page, stocks_page]},
    position="hidden"   # we draw our own sidebar nav
)

st.set_page_config(
    page_title="NSE F&O Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─── Shared Sidebar (shown on every page) ──────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #222;margin-bottom:16px;">
        <div style="font-size:1.2rem;font-weight:700;letter-spacing:-0.5px;">⚡ NSE F&O</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#444;
                    margin-top:3px;text-transform:uppercase;letter-spacing:1.5px;">Dashboard</div>
    </div>""", unsafe_allow_html=True)

    st.page_link(sectors_page, label="📊  Sectors Overview")
    st.page_link(stocks_page,  label="🔍  Stocks by Sector")

pg.run()