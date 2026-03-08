import json
import os
import streamlit as st

JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fo_sector_map.json")

# ─── Complete NSE F&O universe (206 stocks) ────────────────────────────────────
FO_SYMBOLS = {
    "360ONE", "ABB", "APLAPOLLO", "AUBANK", "ADANIENSOL", "ADANIENT",
    "ADANIGREEN", "ADANIPORTS", "ABCAPITAL", "ALKEM", "AMBER", "AMBUJACEM",
    "ANGELONE", "APOLLOHOSP", "ASHOKLEY", "ASIANPAINT", "ASTRAL", "AUROPHARMA",
    "DMART", "AXISBANK", "BSE", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV",
    "BAJAJHLDNG", "BANDHANBNK", "BANKBARODA", "BANKINDIA", "BDL", "BEL",
    "BHARATFORG", "BHEL", "BPCL", "BHARTIARTL", "BIOCON", "BLUESTARCO",
    "BOSCHLTD", "BRITANNIA", "CGPOWER", "CANBK", "CDSL", "CHOLAFIN",
    "CIPLA", "COALINDIA", "COFORGE", "COLPAL", "CAMS", "CONCOR",
    "CROMPTON", "CUMMINSIND", "DLF", "DABUR", "DALBHARAT", "DELHIVERY",
    "DIVISLAB", "DIXON", "DRREDDY", "ETERNAL", "EICHERMOT", "EXIDEIND",
    "NYKAA", "FORTIS", "GAIL", "GMRAIRPORT", "GLENMARK", "GODREJCP",
    "GODREJPROP", "GRASIM", "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE",
    "HAVELLS", "HEROMOTOCO", "HINDALCO", "HAL", "HINDPETRO", "HINDUNILVR",
    "HINDZINC", "POWERINDIA", "HUDCO", "ICICIBANK", "ICICIGI", "ICICIPRULI",
    "IDFCFIRSTB", "ITC", "INDIANB", "IEX", "IOC", "IRFC",
    "IREDA", "INDUSTOWER", "INDUSINDBK", "NAUKRI", "INFY", "INOXWIND",
    "INDIGO", "JINDALSTEL", "JSWENERGY", "JSWSTEEL", "JIOFIN", "JUBLFOOD",
    "KEI", "KPITTECH", "KALYANKJIL", "KAYNES", "KFINTECH", "KOTAKBANK",
    "LTF", "LICHSGFIN", "LTM", "LT", "LAURUSLABS", "LICI",
    "LODHA", "LUPIN", "M&M", "MANAPPURAM", "MANKIND", "MARICO",
    "MARUTI", "MFSL", "MAXHEALTH", "MAZDOCK", "MPHASIS", "MCX",
    "MUTHOOTFIN", "NBCC", "NHPC", "NMDC", "NTPC", "NATIONALUM",
    "NESTLEIND", "NUVAMA", "OBEROIRLTY", "ONGC", "OIL", "PAYTM",
    "OFSS", "POLICYBZR", "PGEL", "PIIND", "PNBHOUSING", "PAGEIND",
    "PATANJALI", "PERSISTENT", "PETRONET", "PIDILITIND", "PPLPHARMA", "POLYCAB",
    "PFC", "POWERGRID", "PREMIERENE", "PRESTIGE", "PNB", "RBLBANK",
    "RECLTD", "RVNL", "RELIANCE", "SBICARD", "SBILIFE", "SHREECEM",
    "SRF", "SAMMAANCAP", "MOTHERSON", "SHRIRAMFIN", "SIEMENS", "SOLARINDS",
    "SONACOMS", "SBIN", "SAIL", "SUNPHARMA", "SUPREMEIND", "SUZLON",
    "SWIGGY", "SYNGENE", "TATACONSUM", "TVSMOTOR", "TCS", "TATAELXSI",
    "TMPV", "TATAPOWER", "TATASTEEL", "TATATECH", "TECHM", "FEDERALBNK",
    "INDHOTEL", "PHOENIXLTD", "TITAN", "TORNTPHARM", "TORNTPOWER", "TRENT",
    "TIINDIA", "UNOMINDA", "UPL", "ULTRACEMCO", "UNIONBANK", "UNITDSPR",
    "VBL", "VEDL", "IDEA", "VOLTAS", "WAAREEENER", "WIPRO",
    "YESBANK", "ZYDUSLIFE",
}


@st.cache_data
def load_sector_map():
    """Load fo_sector_map.json once and keep in memory."""
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    return data  # { "metadata": {...}, "sectors": { "NIFTY AUTO": [...], ... } }

def get_sectors():
    """Return dict of sector_name -> list of stock symbols."""
    data = load_sector_map()
    return data["sectors"]

def get_metadata():
    data = load_sector_map()
    return data["metadata"]

def get_all_fo_stocks():
    """Return sorted list of all 206 NSE F&O stocks."""
    return sorted(list(FO_SYMBOLS))