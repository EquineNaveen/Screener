"""
Run this script once from your project root to find F&O stocks
that are in the FO_SYMBOLS list but missing from fo_sector_map.json.

Usage:
    python find_missing_fo_stocks.py
"""
import json
import os

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

JSON_PATH = os.path.join(os.path.dirname(__file__), "fo_sector_map.json")

with open(JSON_PATH, "r") as f:
    data = json.load(f)

in_sector_map = set()
for stocks in data["sectors"].values():
    in_sector_map.update(stocks)

missing = sorted(FO_SYMBOLS - in_sector_map)
extra   = sorted(in_sector_map - FO_SYMBOLS)

print(f"\nTotal in FO_SYMBOLS     : {len(FO_SYMBOLS)}")
print(f"Total in fo_sector_map  : {len(in_sector_map)}")
print(f"\n{'─'*50}")
print(f"Stocks in FO_SYMBOLS but NOT in any sector ({len(missing)}):")
for s in missing:
    print(f"  {s}")

print(f"\nStocks in sector map but NOT in FO_SYMBOLS ({len(extra)}):")
for s in extra:
    print(f"  {s}")