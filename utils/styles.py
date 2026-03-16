GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

:root {
    --bg:        #0d0d0d;
    --bg2:       #111111;
    --card:      #161616;
    --border:    #2a2a2a;
    --border2:   #888;
    --gold:      #f5a623;
    --gold2:     #e8870a;
    --green:     #22c55e;
    --green-dim: rgba(34,197,94,0.08);
    --red:       #ef4444;
    --red-dim:   rgba(239,68,68,0.08);
    --text:      #f0f0f0;
    --text2:     #a0a0a0;
    --text3:     #555;
}

/* ── Base ─────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
* { font-family: 'Space Grotesk', sans-serif !important; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit auto-generated top nav in sidebar ────── */
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Hide sidebar collapse/expand arrow button ───────────── */
[data-testid="collapsedControl"]          { display: none !important; }
button[kind="header"]                     { display: none !important; }
[data-testid="stSidebarCollapseButton"]   { display: none !important; }

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 280px !important;
    max-width: 280px !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    background: var(--gold) !important;
    color: #000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: var(--gold2) !important;
    transform: translateY(-1px) !important;
}

/* ── Selectbox ───────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* ── Page links in sidebar ───────────────────────────────── */
[data-testid="stSidebar"] a {
    color: var(--text2) !important;
    text-decoration: none !important;
    font-size: 0.88rem !important;
}
[data-testid="stSidebar"] a:hover { color: var(--gold) !important; }

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ── Hide footer / menu / decoration ────────────────────── */
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { background: transparent !important; }
</style>
"""