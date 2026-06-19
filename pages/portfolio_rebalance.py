"""
Page 2: Portfolio & Rebalance
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.auth import require_login
require_login()

import json
import pickle
import pandas as pd
import yfinance as yf
from datetime import timedelta, date

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
LOOKBACK_MONTHS   = [3, 12]
PRICE_MIN         = 100
PRICE_MAX         = 10_000
TOP_N_UNIVERSE    = 20
TOP_N_PORTFOLIO   = 10
DATA_DIR          = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
PICKLE_DIR        = os.path.join(DATA_DIR, 'pickle')
SYMBOLS_FILE      = os.path.join(DATA_DIR, 'nifty200_symbols.json')
PORTFOLIO_FILE    = os.path.join(DATA_DIR, 'portfolio_state.json')
MIN_ROWS_REQUIRED = 100

_FO_SYMBOLS_NS = [
    "360ONE.NS","ABB.NS","APLAPOLLO.NS","AUBANK.NS","ADANIENSOL.NS","ADANIENT.NS",
    "ADANIGREEN.NS","ADANIPORTS.NS","ABCAPITAL.NS","ALKEM.NS","AMBER.NS","AMBUJACEM.NS",
    "ANGELONE.NS","APOLLOHOSP.NS","ASHOKLEY.NS","ASIANPAINT.NS","ASTRAL.NS","AUROPHARMA.NS",
    "DMART.NS","AXISBANK.NS","BSE.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS",
    "BAJAJHLDNG.NS","BANDHANBNK.NS","BANKBARODA.NS","BANKINDIA.NS","BDL.NS","BEL.NS",
    "BHARATFORG.NS","BHEL.NS","BPCL.NS","BHARTIARTL.NS","BIOCON.NS","BLUESTARCO.NS",
    "BOSCHLTD.NS","BRITANNIA.NS","CGPOWER.NS","CANBK.NS","CDSL.NS","CHOLAFIN.NS",
    "CIPLA.NS","COALINDIA.NS","COFORGE.NS","COLPAL.NS","CAMS.NS","CONCOR.NS",
    "CROMPTON.NS","CUMMINSIND.NS","DLF.NS","DABUR.NS","DALBHARAT.NS","DELHIVERY.NS",
    "DIVISLAB.NS","DIXON.NS","DRREDDY.NS","EICHERMOT.NS","EXIDEIND.NS",
    "NYKAA.NS","FORTIS.NS","GAIL.NS","GLENMARK.NS","GODREJCP.NS",
    "GODREJPROP.NS","GRASIM.NS","HCLTECH.NS","HDFCAMC.NS","HDFCBANK.NS","HDFCLIFE.NS",
    "HAVELLS.NS","HEROMOTOCO.NS","HINDALCO.NS","HAL.NS","HINDPETRO.NS","HINDUNILVR.NS",
    "HINDZINC.NS","HUDCO.NS","ICICIBANK.NS","ICICIGI.NS","ICICIPRULI.NS",
    "IDFCFIRSTB.NS","ITC.NS","INDIANB.NS","IEX.NS","IOC.NS","IRFC.NS",
    "IREDA.NS","INDUSTOWER.NS","INDUSINDBK.NS","NAUKRI.NS","INFY.NS","INOXWIND.NS",
    "INDIGO.NS","JINDALSTEL.NS","JSWENERGY.NS","JSWSTEEL.NS","JIOFIN.NS","JUBLFOOD.NS",
    "KEI.NS","KPITTECH.NS","KALYANKJIL.NS","KAYNES.NS","KFINTECH.NS","KOTAKBANK.NS",
    "LTF.NS","LICHSGFIN.NS","LT.NS","LAURUSLABS.NS","LICI.NS",
    "LODHA.NS","LUPIN.NS","M&M.NS","MANAPPURAM.NS","MANKIND.NS","MARICO.NS",
    "MARUTI.NS","MFSL.NS","MAXHEALTH.NS","MAZDOCK.NS","MPHASIS.NS","MCX.NS",
    "MUTHOOTFIN.NS","NBCC.NS","NHPC.NS","NMDC.NS","NTPC.NS","NATIONALUM.NS",
    "NESTLEIND.NS","NUVAMA.NS","OBEROIRLTY.NS","ONGC.NS","OIL.NS","PAYTM.NS",
    "OFSS.NS","POLICYBZR.NS","PIIND.NS","PNBHOUSING.NS","PAGEIND.NS",
    "PATANJALI.NS","PERSISTENT.NS","PETRONET.NS","PIDILITIND.NS","PPLPHARMA.NS","POLYCAB.NS",
    "PFC.NS","POWERGRID.NS","PRESTIGE.NS","PNB.NS","RBLBANK.NS",
    "RECLTD.NS","RVNL.NS","RELIANCE.NS","SBICARD.NS","SBILIFE.NS","SHREECEM.NS",
    "SRF.NS","MOTHERSON.NS","SHRIRAMFIN.NS","SIEMENS.NS","SOLARINDS.NS",
    "SONACOMS.NS","SBIN.NS","SAIL.NS","SUNPHARMA.NS","SUPREMEIND.NS","SUZLON.NS",
    "SWIGGY.NS","SYNGENE.NS","TATACONSUM.NS","TVSMOTOR.NS","TCS.NS","TATAELXSI.NS",
    "TATAPOWER.NS","TATASTEEL.NS","TATATECH.NS","TECHM.NS","FEDERALBNK.NS",
    "INDHOTEL.NS","PHOENIXLTD.NS","TITAN.NS","TORNTPHARM.NS","TORNTPOWER.NS","TRENT.NS",
    "TIINDIA.NS","UNOMINDA.NS","UPL.NS","ULTRACEMCO.NS","UNIONBANK.NS","UNITDSPR.NS",
    "VBL.NS","VEDL.NS","IDEA.NS","VOLTAS.NS","WIPRO.NS",
    "YESBANK.NS","ZYDUSLIFE.NS",
]


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _default_state():
    return {"holdings": [], "last_rebalance": None, "next_rebalance": None}


def load_portfolio_state():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE) as f:
                s = json.load(f)
            base = _default_state()
            base.update(s)
            return base
        except Exception:
            pass
    return _default_state()


def save_portfolio_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(state, f, indent=2)


@st.cache_data(show_spinner=False)
def load_symbols():
    if os.path.exists(SYMBOLS_FILE):
        with open(SYMBOLS_FILE) as f:
            syms = json.load(f)
        if syms:
            return syms
    return _FO_SYMBOLS_NS


@st.cache_data(show_spinner=False, ttl=3600)
def load_data():
    tickers = load_symbols()
    data = {}
    to_download = []
    for ticker in tickers:
        path = os.path.join(PICKLE_DIR, ticker.replace('/', '_') + '.pkl')
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    df = pickle.load(f)
                df.index = pd.to_datetime(df.index)
                if len(df) >= MIN_ROWS_REQUIRED:
                    data[ticker] = df
                    continue
            except Exception:
                pass
        to_download.append(ticker)

    if to_download:
        bar = st.progress(0, text=f"Downloading data for {len(to_download)} stocks…")
        for i, ticker in enumerate(to_download, 1):
            try:
                df = yf.download(ticker, period='2y', progress=False, auto_adjust=True)
                if df is None or df.empty:
                    continue
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.loc[:, ~df.columns.duplicated()]
                if len(df) < MIN_ROWS_REQUIRED:
                    continue
                os.makedirs(PICKLE_DIR, exist_ok=True)
                with open(os.path.join(PICKLE_DIR, ticker.replace('/', '_') + '.pkl'), 'wb') as f:
                    pickle.dump(df, f)
                data[ticker] = df
            except Exception:
                pass
            bar.progress(i / len(to_download), text=f"Downloading… {i}/{len(to_download)}")
        bar.empty()
    return data


def _safe_close(df):
    """Return Close as a 1-D Series regardless of yfinance MultiIndex quirks."""
    col = df['Close']
    if isinstance(col, pd.DataFrame):
        col = col.iloc[:, 0]
    return col


def _momentum(df, months):
    days = months * 21
    close = _safe_close(df)
    if len(close) < days:
        return None
    cur  = float(close.iloc[-1])
    past = float(close.iloc[-days])
    return None if past == 0 else (cur - past) / past * 100


@st.cache_data(show_spinner=False, ttl=3600)
def rank_stocks_cached():
    data = load_data()
    rows = []
    for ticker, df in data.items():
        df_cur = df.copy()
        if isinstance(df_cur.columns, pd.MultiIndex):
            df_cur.columns = df_cur.columns.get_level_values(0)
        # drop duplicate columns (keep first)
        df_cur = df_cur.loc[:, ~df_cur.columns.duplicated()]
        if len(df_cur) < 126:
            continue
        returns = {}
        skip = False
        for months in LOOKBACK_MONTHS:
            r = _momentum(df_cur, months)
            if r is None:
                skip = True
                break
            returns[f'return_{months}m'] = r
        if skip:
            continue
        row = {'ticker': ticker, 'price': float(_safe_close(df_cur).iloc[-1])}
        row.update(returns)
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    df_m = pd.DataFrame(rows)
    for months in LOOKBACK_MONTHS:
        df_m[f'rank_{months}m'] = df_m[f'return_{months}m'].rank(ascending=False)
    df_m['avg_rank'] = df_m[[f'rank_{m}m' for m in LOOKBACK_MONTHS]].mean(axis=1)
    df_m = df_m.sort_values('avg_rank').reset_index(drop=True)
    df_m['final_rank'] = range(1, len(df_m) + 1)
    return df_m


def get_rebalance_actions(df_ranked, current_holdings):
    current_holdings = set(current_holdings)
    df_f = df_ranked[
        (df_ranked['price'] >= PRICE_MIN) & (df_ranked['price'] <= PRICE_MAX)
    ].copy().reset_index(drop=True)
    df_f['final_rank'] = range(1, len(df_f) + 1)

    top_universe     = df_f.head(TOP_N_UNIVERSE).reset_index(drop=True)
    universe_tickers = set(top_universe['ticker'])

    sells = [t for t in current_holdings if t not in universe_tickers]
    holds = [t for t in current_holdings if t in universe_tickers]

    open_slots = TOP_N_PORTFOLIO - len(holds)
    buys = []
    for _, row in top_universe.iterrows():
        if open_slots <= 0:
            break
        if row['ticker'] not in current_holdings:
            buys.append(row['ticker'])
            open_slots -= 1

    return {'top_universe': top_universe, 'sells': sells, 'buys': buys, 'holds': holds}


def _ret_str(val):
    if val is None:
        return "—", "#555"
    color = "#22c55e" if val >= 0 else "#ef4444"
    arrow = "▲" if val >= 0 else "▼"
    return f"{arrow} {val:+.1f}%", color


# ─────────────────────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
div.block-container { padding-top: 2rem !important; }
[data-testid="stHorizontalBlock"] { gap: 8px !important; }
</style>
""", unsafe_allow_html=True)

state = load_portfolio_state()
today = date.today()

# Auto-rebalance
auto_rebalanced = False
if state["next_rebalance"]:
    next_rb = date.fromisoformat(state["next_rebalance"])
    if today >= next_rb:
        with st.spinner("Auto-applying monthly rebalance…"):
            _df = rank_stocks_cached()
        if not _df.empty:
            _actions = get_rebalance_actions(_df, state["holdings"])
            _new = list(set(state["holdings"]) - set(_actions["sells"])) + _actions["buys"]
            state["holdings"]       = _new[:TOP_N_PORTFOLIO]
            state["last_rebalance"] = today.isoformat()
            state["next_rebalance"] = (today + timedelta(days=30)).isoformat()
            save_portfolio_state(state)
            auto_rebalanced = True

with st.spinner("Loading momentum data…"):
    df_ranked = rank_stocks_cached()

prices = dict(zip(df_ranked['ticker'], df_ranked['price']))        if not df_ranked.empty else {}
ret3m  = dict(zip(df_ranked['ticker'], df_ranked['return_3m']))   if not df_ranked.empty else {}
ret12m = dict(zip(df_ranked['ticker'], df_ranked['return_12m']))  if not df_ranked.empty else {}
all_tickers = sorted(load_symbols())

# ─── Header ────────────────────────────────────────────────────────────────────
last_rb_str = state["last_rebalance"] or "—"
next_rb_str = state["next_rebalance"] or "—"
days_label  = ""
if state["next_rebalance"]:
    d = (date.fromisoformat(state["next_rebalance"]) - today).days
    days_label = f"&nbsp;·&nbsp; <span style='color:#f5a623;'>{d} days until next rebalance</span>"

st.markdown(f"""
<div style="padding:32px 0 20px 0;">
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#f5a623;
                 background:rgba(245,166,35,0.08);border:1px solid rgba(245,166,35,0.25);
                 padding:3px 10px;border-radius:4px;letter-spacing:2px;">● PORTFOLIO</span>
    <h1 style="font-size:2rem;font-weight:700;letter-spacing:-1px;margin:14px 0 4px 0;">
        Portfolio &amp; Rebalance
    </h1>
    <p style="color:#444;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;margin:0;letter-spacing:0.5px;">
        Last rebalance: {last_rb_str} &nbsp;·&nbsp; Next: {next_rb_str}{days_label}
    </p>
</div>
""", unsafe_allow_html=True)

if auto_rebalanced:
    st.success("✅ Monthly rebalance auto-applied! Portfolio updated.")

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="height:1px;background:#1a1a1a;margin:4px 0 16px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;color:#444;'
                'text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">Customise Portfolio</div>',
                unsafe_allow_html=True)

    available_to_add = [t for t in all_tickers if t not in state["holdings"]]
    add_sym = st.selectbox("Add stock", ["— select —"] + available_to_add,
                           key="add_sym", label_visibility="collapsed")
    if st.button("＋  Add to Portfolio"):
        if add_sym != "— select —" and add_sym not in state["holdings"]:
            state["holdings"].append(add_sym)
            save_portfolio_state(state)
            st.rerun()

    st.markdown('<div style="height:1px;background:#1a1a1a;margin:12px 0;"></div>', unsafe_allow_html=True)

    if state["holdings"]:
        remove_sym = st.selectbox("Remove stock", ["— select —"] + state["holdings"],
                                  key="remove_sym", label_visibility="collapsed")
        if st.button("✕  Remove from Portfolio"):
            if remove_sym != "— select —" and remove_sym in state["holdings"]:
                state["holdings"].remove(remove_sym)
                save_portfolio_state(state)
                st.rerun()

    st.markdown('<div style="height:1px;background:#1a1a1a;margin:12px 0;"></div>', unsafe_allow_html=True)

    if st.button("⚡  Apply Rebalance Now"):
        if not df_ranked.empty:
            _a = get_rebalance_actions(df_ranked, state["holdings"])
            _new = list(set(state["holdings"]) - set(_a["sells"])) + _a["buys"]
            state["holdings"]       = _new[:TOP_N_PORTFOLIO]
            state["last_rebalance"] = today.isoformat()
            state["next_rebalance"] = (today + timedelta(days=30)).isoformat()
            save_portfolio_state(state)
            st.rerun()

    st.markdown('<div style="height:1px;background:#1a1a1a;margin:12px 0;"></div>', unsafe_allow_html=True)

    if st.button("↺  Refresh Data"):
        st.cache_data.clear()
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — CURRENT PORTFOLIO
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin:24px 0 12px 0;">
    <span style="font-size:1.1rem;font-weight:700;letter-spacing:-0.5px;">Current Portfolio</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#444;margin-left:10px;">
        holdings you own right now
    </span>
</div>
""", unsafe_allow_html=True)

if not state["holdings"]:
    st.markdown("""
    <div style="text-align:center;padding:40px 0;color:#333;
                font-family:'IBM Plex Mono',monospace;font-size:0.8rem;">
        No holdings yet. Add stocks from the sidebar or apply a rebalance.
    </div>""", unsafe_allow_html=True)
else:
    if state["last_rebalance"] is None:
        state["last_rebalance"] = today.isoformat()
        state["next_rebalance"] = (today + timedelta(days=30)).isoformat()
        save_portfolio_state(state)

    TH = "font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:1.5px;color:#555;"
    c1, c2, c3, c4, c5, c6 = st.columns([0.4, 1.6, 1.1, 1.1, 1.1, 0.5])
    with c1: st.markdown(f'<div style="{TH};padding-bottom:6px;">#</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div style="{TH};padding-bottom:6px;">Ticker</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div style="{TH};padding-bottom:6px;">Price (₹)</div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div style="{TH};padding-bottom:6px;">3m Return</div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div style="{TH};padding-bottom:6px;">12m Return</div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div style="{TH};padding-bottom:6px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:#1e1e1e;margin-bottom:4px;"></div>', unsafe_allow_html=True)

    for i, ticker in enumerate(state["holdings"], 1):
        price          = prices.get(ticker)
        r3,   r3_col  = _ret_str(ret3m.get(ticker))
        r12,  r12_col = _ret_str(ret12m.get(ticker))
        price_str      = f"₹{price:,.2f}" if price else "—"

        c1, c2, c3, c4, c5, c6 = st.columns([0.4, 1.6, 1.1, 1.1, 1.1, 0.5])
        with c1:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.76rem;color:#444;">{i}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.88rem;font-weight:700;color:#f5a623;">{ticker.replace(".NS","")}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.82rem;color:#888;">{price_str}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.82rem;font-weight:600;color:{r3_col};">{r3}</div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.82rem;font-weight:600;color:{r12_col};">{r12}</div>', unsafe_allow_html=True)
        with c6:
            if st.button("🗑", key=f"del_hold_{ticker}", help=f"Remove {ticker}"):
                state["holdings"].remove(ticker)
                save_portfolio_state(state)
                st.rerun()
        st.markdown('<div style="height:1px;background:#161616;"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SECTION 2 — REBALANCE LIST
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin:40px 0 12px 0;">
    <span style="font-size:1.1rem;font-weight:700;letter-spacing:-0.5px;">Rebalance List</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#444;margin-left:10px;">
        based on latest momentum ranking
    </span>
</div>
""", unsafe_allow_html=True)

if df_ranked.empty:
    st.warning("Ranking data not available. Click Refresh Data in the sidebar.")
    st.stop()

actions = get_rebalance_actions(df_ranked, state["holdings"])
sells, buys, holds = actions["sells"], actions["buys"], actions["holds"]

# rank lookup
rank_lookup = {}
for _, rr in actions["top_universe"].iterrows():
    rank_lookup[rr["ticker"]] = int(rr["final_rank"])
for _, rr in df_ranked.iterrows():
    rank_lookup.setdefault(rr["ticker"], int(rr["final_rank"]))

# Summary pills
st.markdown(f"""
<div style="display:flex;gap:10px;margin:0 0 20px;flex-wrap:wrap;">
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#22c55e;
                 padding:4px 16px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;font-weight:700;">
        BUY &nbsp;{len(buys)}
    </span>
    <span style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:#ef4444;
                 padding:4px 16px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;font-weight:700;">
        SELL &nbsp;{len(sells)}
    </span>
    <span style="background:rgba(245,166,35,0.08);border:1px solid rgba(245,166,35,0.2);color:#f5a623;
                 padding:4px 16px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;font-weight:700;">
        HOLD &nbsp;{len(holds)}
    </span>
</div>
""", unsafe_allow_html=True)

# ── Three columns ──────────────────────────────────────────────
col_buy, col_sell, col_hold = st.columns(3)

def _card_header(col, label, accent):
    with col:
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
            f'text-transform:uppercase;letter-spacing:2px;color:{accent};'
            f'border-bottom:1px solid #1e1e1e;padding-bottom:8px;margin-bottom:4px;">'
            f'{label}</div>',
            unsafe_allow_html=True,
        )

def _card_row(col, ticker, rank, price, r3, r12):
    r3_str,  r3_col  = _ret_str(r3)
    r12_str, r12_col = _ret_str(r12)
    price_str = f"₹{price:,.2f}" if price else "—"
    with col:
        st.markdown(
            f'<div style="padding:8px 0;border-bottom:1px solid #1a1a1a;">'
            f'  <div style="display:flex;justify-content:space-between;align-items:center;">'
            f'    <span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.85rem;'
            f'                 font-weight:700;color:#f5a623;">{ticker.replace(".NS","")}</span>'
            f'    <span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.68rem;color:#444;">#{rank}</span>'
            f'  </div>'
            f'  <div style="display:flex;gap:10px;margin-top:3px;flex-wrap:wrap;">'
            f'    <span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#666;">{price_str}</span>'
            f'    <span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:{r3_col};">3m {r3_str}</span>'
            f'    <span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:{r12_col};">12m {r12_str}</span>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

def _card_empty(col):
    with col:
        st.markdown(
            '<div style="padding:20px 0;font-family:\'IBM Plex Mono\',monospace;'
            'font-size:0.75rem;color:#333;text-align:center;">None</div>',
            unsafe_allow_html=True,
        )

_card_header(col_buy,  "BUY",  "#22c55e")
_card_header(col_sell, "SELL", "#ef4444")
_card_header(col_hold, "HOLD", "#f5a623")

if buys:
    for t in buys:
        _card_row(col_buy, t, rank_lookup.get(t,"—"), prices.get(t), ret3m.get(t), ret12m.get(t))
else:
    _card_empty(col_buy)

if sells:
    for t in sells:
        _card_row(col_sell, t, rank_lookup.get(t,"—"), prices.get(t), ret3m.get(t), ret12m.get(t))
else:
    _card_empty(col_sell)

if holds:
    for t in holds:
        _card_row(col_hold, t, rank_lookup.get(t,"—"), prices.get(t), ret3m.get(t), ret12m.get(t))
else:
    _card_empty(col_hold)


# ═══════════════════════════════════════════════════════════════
# SECTION 3 — NEW PORTFOLIO PREVIEW
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin:40px 0 12px 0;">
    <span style="font-size:1.1rem;font-weight:700;letter-spacing:-0.5px;">New Portfolio Preview</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#444;margin-left:10px;">
        what your portfolio looks like after this rebalance
    </span>
</div>
""", unsafe_allow_html=True)

new_portfolio = sorted(
    list((set(state["holdings"]) - set(sells)) | set(buys)),
    key=lambda t: rank_lookup.get(t, 9999)
)[:TOP_N_PORTFOLIO]

if new_portfolio:
    TH = "font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:1.5px;color:#555;"
    c1,c2,c3,c4,c5,c6 = st.columns([0.5, 1.6, 1.1, 1.1, 1.1, 0.8])
    with c1: st.markdown(f'<div style="{TH};padding-bottom:6px;">Rank</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div style="{TH};padding-bottom:6px;">Ticker</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div style="{TH};padding-bottom:6px;">Price (₹)</div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div style="{TH};padding-bottom:6px;">3m Return</div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div style="{TH};padding-bottom:6px;">12m Return</div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div style="{TH};padding-bottom:6px;">Action</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:#1e1e1e;margin-bottom:4px;"></div>', unsafe_allow_html=True)

    for ticker in new_portfolio:
        rank           = rank_lookup.get(ticker, "—")
        price          = prices.get(ticker)
        r3,   r3_col  = _ret_str(ret3m.get(ticker))
        r12,  r12_col = _ret_str(ret12m.get(ticker))
        price_str      = f"₹{price:,.2f}" if price else "—"
        action_label   = "BUY"  if ticker in buys  else "HOLD"
        action_color   = "#22c55e" if ticker in buys else "#f5a623"

        c1,c2,c3,c4,c5,c6 = st.columns([0.5, 1.6, 1.1, 1.1, 1.1, 0.8])
        with c1:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.76rem;color:#444;">#{rank}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.88rem;font-weight:700;color:#f5a623;">{ticker.replace(".NS","")}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.82rem;color:#888;">{price_str}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.82rem;font-weight:600;color:{r3_col};">{r3}</div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.82rem;font-weight:600;color:{r12_col};">{r12}</div>', unsafe_allow_html=True)
        with c6:
            st.markdown(f'<div style="padding:7px 0;font-family:\'IBM Plex Mono\',monospace;font-size:0.76rem;font-weight:700;color:{action_color};">{action_label}</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:#161616;"></div>', unsafe_allow_html=True)

# Confirm button
st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
_, btn_col, _ = st.columns([2, 2, 2])
with btn_col:
    if st.button("✅  Confirm & Apply Rebalance", use_container_width=True):
        state["holdings"]       = new_portfolio
        state["last_rebalance"] = today.isoformat()
        state["next_rebalance"] = (today + timedelta(days=30)).isoformat()
        save_portfolio_state(state)
        st.success("✅ Portfolio updated! Next rebalance in 30 days.")
        st.rerun()