import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.watchlist import get_watchlist, add_to_watchlist, remove_from_watchlist, update_note
from utils.data_loader import get_all_fo_stocks
from utils.market_data import get_stocks_data, is_market_open

# ─── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated"):
    st.error("Please log in to view your watchlist.")
    st.stop()

username = st.session_state["username"]

# ─── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="height:1px;background:#1a1a1a;margin:4px 0 16px 0;"></div>', unsafe_allow_html=True)
    if st.button("↺  Refresh Now"):
        st.cache_data.clear()
        st.rerun()

# ─── CSS: kill all horizontal rules / top margins Streamlit adds ───────────────
st.markdown("""
<style>
[data-testid="stHorizontalBlock"] { margin-top: 0 !important; gap: 8px !important; }
[data-testid="stVerticalBlock"] hr { display: none !important; }
div.block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)

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
    <h1 style="font-size:2rem;font-weight:700;letter-spacing:-1px;margin:14px 0 4px 0;">My Watchlist</h1>
    <p style="color:#444;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;margin:0;letter-spacing:0.5px;">
        {username} · Track your F&amp;O stocks · Add notes
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Add stock — plain inline row, no card/bar wrapper ────────────────────────
all_fo_stocks = get_all_fo_stocks()
watchlist     = get_watchlist(username)
watched_syms  = [item["symbol"] for item in watchlist]
available     = [s for s in all_fo_stocks if s not in watched_syms]

a1, a2, a3 = st.columns([2, 4, 2])
with a1:
    new_sym = st.selectbox("Symbol", ["— select —"] + available, label_visibility="collapsed")
with a2:
    new_note = st.text_input("Note", placeholder="e.g. breakout watch, support at 2400…", label_visibility="collapsed")
with a3:
    if st.button("＋  Add to Watchlist", use_container_width=True):
        if new_sym == "— select —":
            st.warning("Select a symbol first.")
        else:
            ok = add_to_watchlist(username, new_sym, new_note)
            if ok:
                st.success(f"{new_sym} added!")
                st.rerun()
            else:
                st.warning(f"{new_sym} is already in your watchlist.")

st.markdown('<div style="height:1px;background:#1e1e1e;margin:14px 0 18px 0;"></div>', unsafe_allow_html=True)

# ─── Watchlist ─────────────────────────────────────────────────────────────────
watchlist = get_watchlist(username)

if not watchlist:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;color:#333;
                font-family:'IBM Plex Mono',monospace;font-size:0.8rem;">
        Your watchlist is empty. Add stocks above.
    </div>""", unsafe_allow_html=True)
    st.stop()

# fetch live data
symbols = tuple(item["symbol"] for item in watchlist)
with st.spinner(f"Fetching data for {len(symbols)} stocks..."):
    rows_data = get_stocks_data(symbols)

rows_map = {r["symbol"]: r for r in rows_data}

# summary bar
g       = sum(1 for r in rows_data if r["pct"] is not None and r["pct"] > 0)
l       = sum(1 for r in rows_data if r["pct"] is not None and r["pct"] < 0)
n       = len(rows_data) - g - l
now_str = __import__('datetime').datetime.now().strftime('%H:%M:%S')

st.markdown(f"""
<div style="display:flex;gap:10px;align-items:center;margin:0 0 14px;flex-wrap:wrap;">
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#22c55e;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▲ {g} Gainers</span>
    <span style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:#ef4444;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▼ {l} Losers</span>
    <span style="background:#1a1a1a;border:1px solid #2a2a2a;color:#444;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">— {n} N/A</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#2a2a2a;">{now_str}</span>
</div>
""", unsafe_allow_html=True)

# ─── Column headers ────────────────────────────────────────────────────────────
th = "font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:1.5px;color:#333;padding:0 4px 8px 4px;"
st.markdown(f"""
<div style="display:grid;grid-template-columns:1.2fr 0.9fr 0.9fr 3fr 0.4fr;
            gap:8px;padding:0 2px 6px 2px;border-bottom:1px solid #1e1e1e;margin-bottom:4px;">
    <div style="{th}">Symbol</div>
    <div style="{th}">Price</div>
    <div style="{th}">Change</div>
    <div style="{th}">Note</div>
    <div style="{th}"></div>
</div>
""", unsafe_allow_html=True)

# ─── Each stock row ─────────────────────────────────────────────────────────────
for item in watchlist:
    sym    = item["symbol"]
    note   = item["note"]
    r      = rows_map.get(sym, {})
    price  = r.get("price")
    pct    = r.get("pct")
    tv_url = r.get("tv_url", f"https://www.tradingview.com/chart/?symbol=NSE:{sym}")

    if pct is None:
        pct_color, pct_str = "#444", "—"
    elif pct >= 0:
        pct_color, pct_str = "#22c55e", f"▲ +{pct:.2f}%"
    else:
        pct_color, pct_str = "#ef4444", f"▼ {pct:.2f}%"

    price_str = f"₹{price:,.2f}" if price else "—"

    c_sym, c_price, c_pct, c_note, c_del = st.columns([1.2, 0.9, 0.9, 3, 0.4])

    with c_sym:
        st.markdown(f"""
        <div style="padding:8px 4px;">
            <a href="{tv_url}" target="_blank"
               style="font-family:'IBM Plex Mono',monospace;font-size:0.88rem;font-weight:700;
                      color:#f5a623;text-decoration:none;">{sym}</a>
        </div>""", unsafe_allow_html=True)

    with c_price:
        st.markdown(f"""
        <div style="padding:8px 4px;font-family:'IBM Plex Mono',monospace;
                    font-size:0.82rem;color:#888;">{price_str}</div>
        """, unsafe_allow_html=True)

    with c_pct:
        st.markdown(f"""
        <div style="padding:8px 4px;font-family:'IBM Plex Mono',monospace;
                    font-size:0.82rem;font-weight:600;color:{pct_color};">{pct_str}</div>
        """, unsafe_allow_html=True)

    with c_note:
        new_note_val = st.text_input(
            "note", value=note,
            placeholder="Add a note…",
            key=f"note_{sym}",
            label_visibility="collapsed",
        )
        if new_note_val != note:
            update_note(username, sym, new_note_val)
            st.rerun()

    with c_del:
        if st.button("🗑", key=f"del_{sym}", help=f"Remove {sym}"):
            remove_from_watchlist(username, sym)
            st.rerun()

    st.markdown('<div style="height:1px;background:#161616;margin:0 2px;"></div>', unsafe_allow_html=True)