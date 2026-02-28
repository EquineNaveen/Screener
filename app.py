import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.styles import GLOBAL_CSS

st.set_page_config(
    page_title="NSE F&O Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─── Sign-out button: fixed top-right via CSS targeting the first button rendered
SIGNOUT_CSS = """
<style>
div[data-testid="stButton"]:has(button[kind="secondary"]#signout) button,
#signout-fixed {
    position: fixed !important;
    top: 12px !important;
    right: 24px !important;
    z-index: 99999 !important;
    background: #1a1a1a !important;
    color: #555 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    padding: 5px 14px !important;
    width: auto !important;
    min-width: unset !important;
}
</style>
"""

def _check_credentials(username: str, password: str) -> bool:
    try:
        stored = st.secrets["passwords"].get(username)
        return stored is not None and stored == password
    except Exception:
        return False


def _login_screen():
    st.markdown("""
    <div style="max-width:380px;margin:80px auto 0 auto;">
        <div style="text-align:center;margin-bottom:32px;">
            <div style="font-size:2rem;font-weight:700;letter-spacing:-1px;">⚡ NSE F&amp;O</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#444;
                        text-transform:uppercase;letter-spacing:2px;margin-top:4px;">Dashboard · Sign in</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.form("login_form"):
            st.markdown('<div style="margin-bottom:4px;font-size:0.75rem;color:#666;font-family:IBM Plex Mono,monospace;text-transform:uppercase;letter-spacing:1px;">Username</div>', unsafe_allow_html=True)
            username = st.text_input("Username", label_visibility="collapsed", placeholder="username")
            st.markdown('<div style="margin:12px 0 4px 0;font-size:0.75rem;color:#666;font-family:IBM Plex Mono,monospace;text-transform:uppercase;letter-spacing:1px;">Password</div>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if _check_credentials(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"]       = username
                st.rerun()
            else:
                st.error("Invalid username or password.")


# ─── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated"):
    _login_screen()
    st.stop()

# ─── Pages ─────────────────────────────────────────────────────────────────────
sectors_page   = st.Page("pages/sectors.py",   title="Sectors Overview")
stocks_page    = st.Page("pages/stocks.py",     title="Stocks by Sector")
watchlist_page = st.Page("pages/watchlist.py",  title="My Watchlist")

pg = st.navigation(
    {"NSE F&O": [sectors_page, stocks_page, watchlist_page]},
    position="hidden",
)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #222;margin-bottom:16px;">
        <div style="font-size:1.2rem;font-weight:700;letter-spacing:-0.5px;">⚡ NSE F&amp;O</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#444;
                    margin-top:3px;text-transform:uppercase;letter-spacing:1.5px;">Dashboard</div>
    </div>""", unsafe_allow_html=True)

    st.page_link(sectors_page,   label="📊  Sectors Overview")
    st.page_link(stocks_page,    label="🔍  Stocks by Sector")
    st.page_link(watchlist_page, label="⭐  My Watchlist")

    st.markdown(f"""
    <div style="position:fixed;bottom:0;left:0;width:280px;padding:14px 20px;
                background:#111;border-top:1px solid #1e1e1e;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#444;
                    text-transform:uppercase;letter-spacing:1px;">Signed in as</div>
        <div style="font-size:0.85rem;font-weight:600;color:#f0f0f0;margin-top:2px;">
            {st.session_state['username']}
        </div>
    </div>""", unsafe_allow_html=True)

# ─── Sign-out button pinned to top-right via CSS + JS ─────────────────────────
st.markdown(SIGNOUT_CSS, unsafe_allow_html=True)
# Render it first thing in the main area; JS moves it to fixed position
if st.button("⎋  Sign Out", key="global_signout"):
    st.session_state.clear()
    st.rerun()

# JS: grab the sign-out button's parent stButton div and fix it top-right
st.markdown("""
<script>
(function fix() {
    const btns = window.parent.document.querySelectorAll('[data-testid="stMainBlockContainer"] button');
    for (const b of btns) {
        if (b.innerText.includes('Sign Out')) {
            const wrap = b.closest('[data-testid="stButton"]') || b.parentElement;
            Object.assign(wrap.style, {
                position: 'fixed', top: '12px', right: '24px',
                zIndex: '99999', width: 'auto'
            });
            Object.assign(b.style, {
                background: '#1a1a1a', color: '#555',
                border: '1px solid #2a2a2a', borderRadius: '6px',
                fontFamily: 'IBM Plex Mono, monospace', fontSize: '0.68rem',
                padding: '5px 14px', width: 'auto', minWidth: 'unset'
            });
            break;
        }
    }
}());
</script>
""", unsafe_allow_html=True)

pg.run()