import streamlit as st
import streamlit.components.v1 as components
import sys, os, time, json, math

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import get_sectors
from utils.market_data import get_sector_data, is_market_open, SECTOR_TV_MAP


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="height:1px;background:#1a1a1a;margin:4px 0 16px 0;"></div>',
                unsafe_allow_html=True)
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
                 background:{bb};border:1px solid {bd};padding:3px 10px;
                 border-radius:4px;letter-spacing:2px;">● NSE {bl}</span>
    <h1 style="font-size:2rem;font-weight:700;letter-spacing:-1px;margin:14px 0 4px 0;">
        Sectors Overview</h1>
    <p style="color:#444;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;
              margin:0;letter-spacing:0.5px;">
        NSE sector indices · Live % change
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
    sector_data = sorted(sector_data, key=lambda s: (s["pct_change"] is None, -(s["pct_change"] if s["pct_change"] is not None else 0)))
elif sort_by == "% Change ↑":
    sector_data = sorted(sector_data, key=lambda s: (s["pct_change"] is None,  (s["pct_change"] if s["pct_change"] is not None else 0)))
elif sort_by == "Name A-Z":
    sector_data = sorted(sector_data, key=lambda s: s["sector"])
elif sort_by == "Stock Count ↓":
    sector_data = sorted(sector_data, key=lambda s: s["stock_count"], reverse=True)

# ─── Summary bar ───────────────────────────────────────────────────────────────
gainers = sum(1 for s in sector_data if s["pct_change"] is not None and s["pct_change"] > 0)
losers  = sum(1 for s in sector_data if s["pct_change"] is not None and s["pct_change"] < 0)
na      = len(sector_data) - gainers - losers
now_str = __import__('datetime').datetime.now().strftime('%H:%M:%S')

st.markdown(f"""
<div style="display:flex;gap:10px;align-items:center;margin:16px 0 24px;flex-wrap:wrap;">
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);
                 color:#22c55e;padding:3px 12px;border-radius:4px;
                 font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▲ {gainers} Gainers</span>
    <span style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                 color:#ef4444;padding:3px 12px;border-radius:4px;
                 font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">▼ {losers} Losers</span>
    <span style="background:#1a1a1a;border:1px solid #2a2a2a;color:#444;
                 padding:3px 12px;border-radius:4px;
                 font-family:'IBM Plex Mono',monospace;font-size:0.7rem;">— {na} N/A</span>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                 color:#2a2a2a;">{now_str}</span>
</div>
""", unsafe_allow_html=True)

# ─── Build sector list ─────────────────────────────────────────────────────────
sectors_list = []
for s in sector_data:
    tv_symbol = SECTOR_TV_MAP.get(s["sector"], "")
    tv_url    = s["tv_url"]
    sectors_list.append({
        "name":        s["sector"],
        "tv_url":      tv_url,
        "pct_change":  s["pct_change"],
        "price":       s["price"],
        "stock_count": s["stock_count"],
        "source":      s["source"],
    })

sectors_json = json.dumps(sectors_list)

# ─── Cards-only HTML ───────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent; font-family: 'IBM Plex Mono', monospace; color: #888; }
#grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.card {
  background: #161616; border: 1px solid #222; border-radius: 10px;
  padding: 18px 16px; position: relative; overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
  text-decoration: none; display: block;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
.card-name   { font-size: 0.78rem; font-weight: 600; color: #888; margin-bottom: 10px;
               white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-pct    { font-size: 1.65rem; font-weight: 700; line-height: 1; }
.card-price  { font-size: 0.75rem; color: #555; margin-top: 4px; }
.card-stocks { font-size: 0.62rem; color: #888; margin-top: 12px; }
.card-src    { position: absolute; bottom: 5px; right: 8px; font-size: 0.5rem; color: #222; }
</style>
</head>
<body>
<div id="grid"></div>
<script>
var SECTORS = SECTORS_JSON;

function buildGrid() {
  var grid = document.getElementById('grid');
  SECTORS.forEach(function(s) {
    var pct = s.pct_change;
    var topC, pctC, gradBg, pctDisp, arrow;

    if (pct === null || pct === undefined) {
      topC = '#2a2a2a'; pctC = '#444'; gradBg = '#161616'; pctDisp = 'N/A'; arrow = '';
    } else if (pct >= 0) {
      topC = '#22c55e'; pctC = '#22c55e';
      gradBg = 'linear-gradient(160deg,#161616 0%,rgba(34,197,94,0.04) 100%)';
      pctDisp = '+' + pct.toFixed(2) + '%'; arrow = '▲ ';
    } else {
      topC = '#ef4444'; pctC = '#ef4444';
      gradBg = 'linear-gradient(160deg,#161616 0%,rgba(239,68,68,0.04) 100%)';
      pctDisp = pct.toFixed(2) + '%'; arrow = '▼ ';
    }

    var priceHtml = s.price
      ? '<div class="card-price">₹' + parseFloat(s.price).toLocaleString('en-IN',
          {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '</div>'
      : '';

    var card = document.createElement('a');
    card.className = 'card';
    card.href = s.tv_url;
    card.target = '_blank';
    card.style.background = gradBg;
    card.style.borderTop  = '2px solid ' + topC;
    card.dataset.topColor = topC;
    card.innerHTML =
      '<div class="card-name" title="' + s.name + '">' + s.name + '</div>' +
      '<div class="card-pct" style="color:' + pctC + '">' + arrow + pctDisp + '</div>' +
      priceHtml +
      '<div class="card-stocks">' + s.stock_count + ' F&O stocks</div>' +
      '<div class="card-src">' + s.source + '</div>';

    card.addEventListener('mouseover', function() {
      this.style.borderColor = this.dataset.topColor;
    });
    card.addEventListener('mouseout', function() {
      this.style.borderColor = '#222';
      this.style.borderTopColor = this.dataset.topColor;
    });
    grid.appendChild(card);
  });
}

buildGrid();
</script>
</body>
</html>"""

html = HTML.replace("SECTORS_JSON", sectors_json)

grid_rows    = math.ceil(len(sector_data) / 4)
total_height = (grid_rows * 140) + 40
components.html(html, height=total_height, scrolling=False)

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