"""
Page 1: Momentum Ranking
Ranks Nifty 200 stocks by 3m + 12m momentum, with filters.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.auth import require_login
require_login()

import pandas as pd
import json
import pickle
import yfinance as yf

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
MIN_ROWS_REQUIRED = 100


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

# Fallback universe — all NSE F&O symbols with .NS suffix for yfinance
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


@st.cache_data(show_spinner=False)
def load_symbols():
    """Load tickers from JSON if present, else fall back to built-in F&O list."""
    if os.path.exists(SYMBOLS_FILE):
        with open(SYMBOLS_FILE) as f:
            syms = json.load(f)
        if syms:
            return syms
    return _FO_SYMBOLS_NS


@st.cache_data(show_spinner=False, ttl=3600)
def load_data(refresh=False, period='2y'):
    tickers = load_symbols()
    data = {}
    to_download = []

    if not refresh:
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
    else:
        to_download = list(tickers)

    if to_download:
        progress_bar = st.progress(0, text=f"Downloading data for {len(to_download)} stocks…")
        for i, ticker in enumerate(to_download, 1):
            try:
                df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
                if df is None or df.empty:
                    continue
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.loc[:, ~df.columns.duplicated()]
                if len(df) < MIN_ROWS_REQUIRED:
                    continue
                # save to pickle for next time
                os.makedirs(PICKLE_DIR, exist_ok=True)
                path = os.path.join(PICKLE_DIR, ticker.replace('/', '_') + '.pkl')
                with open(path, 'wb') as f:
                    pickle.dump(df, f)
                data[ticker] = df
            except Exception:
                pass
            progress_bar.progress(i / len(to_download),
                                   text=f"Downloading… {i}/{len(to_download)}")
        progress_bar.empty()

    return data


def _safe_close(df):
    """Return the Close column as a 1-D Series regardless of yfinance MultiIndex quirks."""
    col = df['Close']
    if isinstance(col, pd.DataFrame):
        col = col.iloc[:, 0]   # take first column if duplicates
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
        price = float(_safe_close(df_cur).iloc[-1])
        last_date = df_cur.index[-1]
        row = {'ticker': ticker, 'price': price, 'last_date': str(last_date.date())}
        row.update(returns)
        rows.append(row)

    if not rows:
        return pd.DataFrame()

    df_m = pd.DataFrame(rows)
    for months in LOOKBACK_MONTHS:
        col      = f'return_{months}m'
        rank_col = f'rank_{months}m'
        df_m[rank_col] = df_m[col].rank(ascending=False)
    rank_cols = [f'rank_{m}m' for m in LOOKBACK_MONTHS]
    df_m['avg_rank'] = df_m[rank_cols].mean(axis=1)
    df_m = df_m.sort_values('avg_rank').reset_index(drop=True)
    df_m['final_rank'] = range(1, len(df_m) + 1)
    return df_m


# ─────────────────────────────────────────────────────────────
# PAGE LAYOUT
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
div.block-container { padding-top: 2rem !important; }
[data-testid="stHorizontalBlock"] { gap: 8px !important; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="padding:32px 0 20px 0;">
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#f5a623;
                 background:rgba(245,166,35,0.08);border:1px solid rgba(245,166,35,0.25);
                 padding:3px 10px;border-radius:4px;letter-spacing:2px;">
        ● MOMENTUM
    </span>
    <h1 style="font-size:2rem;font-weight:700;letter-spacing:-1px;margin:14px 0 4px 0;">
        Momentum Ranking
    </h1>
    <p style="color:#444;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;margin:0;letter-spacing:0.5px;">
        3-month &amp; 12-month combined rank · Nifty 200 universe · Monthly rebalance
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar — just refresh
with st.sidebar:
    st.markdown('<div style="height:1px;background:#1a1a1a;margin:4px 0 16px 0;"></div>', unsafe_allow_html=True)
    if st.button("↺  Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Load & rank
with st.spinner("Loading momentum data…"):
    df_ranked = rank_stocks_cached()

if df_ranked.empty:
    st.info("Fetching data for the first time — this may take a few minutes. Please wait…")
    st.stop()

# Apply price filter (always on)
df_filtered = df_ranked[
    (df_ranked['price'] >= PRICE_MIN) &
    (df_ranked['price'] <= PRICE_MAX)
].copy().reset_index(drop=True)
df_filtered['final_rank'] = range(1, len(df_filtered) + 1)

# Summary pills
total     = len(df_filtered)
gainers3  = int((df_filtered['return_3m']  > 0).sum())
gainers12 = int((df_filtered['return_12m'] > 0).sum())

st.markdown(f"""
<div style="display:flex;gap:10px;align-items:center;margin:0 0 18px;flex-wrap:wrap;">
    <span style="background:rgba(245,166,35,0.08);border:1px solid rgba(245,166,35,0.2);color:#f5a623;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">
        {total} stocks ranked
    </span>
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#22c55e;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">
        {gainers3} positive 3m
    </span>
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#22c55e;
                 padding:3px 12px;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">
        {gainers12} positive 12m
    </span>
</div>
""", unsafe_allow_html=True)

# Table header
th = "font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:1.5px;color:#555;padding:0 4px 8px 4px;"
st.markdown(f"""
<div style="display:grid;grid-template-columns:0.4fr 1.4fr 0.9fr 1fr 1fr 0.9fr 0.9fr;
            gap:6px;padding:0 2px 6px 2px;border-bottom:1px solid #1e1e1e;margin-bottom:4px;">
    <div style="{th}">#</div>
    <div style="{th}">Ticker</div>
    <div style="{th}">Price (₹)</div>
    <div style="{th}">3m Return</div>
    <div style="{th}">12m Return</div>
    <div style="{th}">Avg Rank</div>
    <div style="{th}">Last Date</div>
</div>
""", unsafe_allow_html=True)

# Rows
display_df = df_filtered.head(TOP_N_UNIVERSE)

for _, row in display_df.iterrows():
    rank   = int(row['final_rank'])
    ticker = row['ticker']
    price  = row['price']
    r3     = row['return_3m']
    r12    = row['return_12m']
    avg_r  = row['avg_rank']
    ldate  = row.get('last_date', '—')

    r3_color  = "#22c55e" if r3  >= 0 else "#ef4444"
    r12_color = "#22c55e" if r12 >= 0 else "#ef4444"
    r3_str    = f"{'▲' if r3>=0 else '▼'} {r3:+.1f}%"
    r12_str   = f"{'▲' if r12>=0 else '▼'} {r12:+.1f}%"

    # highlight top 10 row
    row_bg = "rgba(245,166,35,0.04)" if rank <= TOP_N_PORTFOLIO else "transparent"
    rank_color = "#f5a623" if rank <= TOP_N_PORTFOLIO else "#555"

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:0.4fr 1.4fr 0.9fr 1fr 1fr 0.9fr 0.9fr;
                gap:6px;padding:8px 2px;border-bottom:1px solid #161616;
                background:{row_bg};border-radius:4px;align-items:center;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.78rem;font-weight:700;color:{rank_color};padding:0 4px;">
            {rank}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.88rem;font-weight:700;color:#f5a623;padding:0 4px;">
            {ticker.replace('.NS','')}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#888;padding:0 4px;">
            ₹{price:,.2f}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.82rem;font-weight:600;color:{r3_color};padding:0 4px;">
            {r3_str}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.82rem;font-weight:600;color:{r12_color};padding:0 4px;">
            {r12_str}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.78rem;color:#555;padding:0 4px;">
            {avg_r:.1f}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#333;padding:0 4px;">
            {ldate}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Legend
st.markdown("""
<div style="margin-top:20px;padding:12px 16px;background:#111;border:1px solid #1e1e1e;
            border-radius:8px;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#444;">
    <span style="color:#f5a623;">●</span> Gold rows = Top 10 (target portfolio) &nbsp;|&nbsp;
    Avg Rank = average of 3m rank + 12m rank (lower is better)
</div>
""", unsafe_allow_html=True)