import requests
import time
import urllib.parse
import json
from datetime import datetime

# -------------------------------
# F&O Stock List (206 stocks)
# -------------------------------
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
print(f"Total F&O stocks: {len(FO_SYMBOLS)}")

# -------------------------------
# Sector Mapping (Official NSE Names)
# -------------------------------
SECTORS = {
    "CNXREALTY":         "NIFTY REALTY",
    "CNXAUTO":           "NIFTY AUTO",
    "CNXFMCG":           "NIFTY FMCG",
    "CNXMETAL":          "NIFTY METAL",
    "CNXFINANCE":        "NIFTY FINANCIAL SERVICES",
    "CNXPHARMA":         "NIFTY PHARMA",
    "CNXCONSUMPTION":    "NIFTY INDIA CONSUMPTION",
    "NIFTY_HEALTHCARE":  "NIFTY HEALTHCARE INDEX",
    "NIFTYPVTBANK":      "NIFTY PRIVATE BANK",
    "NIFTY_CHEMICALS":   "NIFTY CHEMICALS",
    "NIFTY_MID_SELECT":  "NIFTY MID SELECT",
    "CNXINFRA":          "NIFTY INFRASTRUCTURE",
    "CNXCOMMODITIES":    "NIFTY COMMODITIES",
    "NIFTY_IND_DEFENCE": "NIFTY INDIA DEFENCE",
    "CNXPSUBANK":        "NIFTY PSU BANK",
    "CNXENERGY":         "NIFTY ENERGY",
    "NIFTY_OIL_AND_GAS": "NIFTY OIL & GAS",
    "CNXIT":             "NIFTY IT",
    "NIFTY_CONSR_DURBL": "NIFTY CONSUMER DURABLES",
    "CNXMEDIA":          "NIFTY MEDIA",
}

# -------------------------------
# NSE Session Setup
# -------------------------------
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept":     "application/json",
    "Referer":    "https://www.nseindia.com/",
}

print("Initialising NSE session...")
session.get("https://www.nseindia.com", headers=headers)
time.sleep(2)

# -------------------------------
# Fetch & Filter Per Sector
# -------------------------------
sector_fo_map = {}

for app_symbol, index_name in SECTORS.items():
    print(f"\n{'='*55}")
    print(f"  {index_name}")
    print(f"{'='*55}")

    try:
        encoded = urllib.parse.quote(index_name)
        url     = f"https://www.nseindia.com/api/equity-stockIndices?index={encoded}"
        resp    = session.get(url, headers=headers)

        if resp.status_code != 200:
            print(f"  ✗ API returned {resp.status_code} — skipping")
            sector_fo_map[index_name] = []
            time.sleep(1)
            continue

        data         = resp.json()
        all_stocks   = [item["symbol"] for item in data.get("data", [])]
        fo_stocks    = sorted([s for s in all_stocks if s in FO_SYMBOLS])
        non_fo_count = len(all_stocks) - len(fo_stocks)

        sector_fo_map[index_name] = fo_stocks

        print(f"  Total in index   : {len(all_stocks)}")
        print(f"  F&O eligible     : {len(fo_stocks)}")
        print(f"  Non-F&O filtered : {non_fo_count}")
        if fo_stocks:
            print(f"  Stocks           : {', '.join(fo_stocks)}")
        else:
            print("  Stocks           : None in F&O list")

        time.sleep(1)

    except Exception as e:
        print(f"  ✗ Error: {e}")
        sector_fo_map[index_name] = []

# -------------------------------
# Summary
# -------------------------------
print(f"\n{'='*55}")
print("SUMMARY — F&O STOCKS PER SECTOR")
print(f"{'='*55}")
print(f"  {'Sector':<35} {'F&O Count':>9}")
print(f"  {'-'*35} {'-'*9}")
for sector, stocks in sector_fo_map.items():
    print(f"  {sector:<35} {len(stocks):>9}")

from collections import defaultdict
stock_sectors = defaultdict(list)
for sector, stocks in sector_fo_map.items():
    for s in stocks:
        stock_sectors[s].append(sector)

multi = {s: secs for s, secs in stock_sectors.items() if len(secs) > 1}
if multi:
    print(f"\n  Stocks in multiple sectors ({len(multi)}):")
    for stock, secs in sorted(multi.items()):
        print(f"    {stock:<15} → {', '.join(secs)}")

# -------------------------------
# Save to JSON
# -------------------------------
output = {
    "metadata": {
        "last_updated": datetime.now().isoformat(),
        "total_sectors": len(sector_fo_map),
        "total_fo_symbols_tracked": len(FO_SYMBOLS),
        "source": "NSE India"
    },
    "sectors": sector_fo_map
}

with open("fo_sector_map.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nData saved to: fo_sector_map.json")
print("\nDONE")