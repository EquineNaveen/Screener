import json
import os
import streamlit as st

JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fo_sector_map.json")

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
    """Return flat list of all unique F&O stocks across all sectors."""
    sectors = get_sectors()
    all_stocks = set()
    for stocks in sectors.values():
        all_stocks.update(stocks)
    return sorted(list(all_stocks))