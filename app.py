import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Alpha V6 AUTO", page_icon="🤖", layout="wide")
st.title("🤖 ALPHA V6 - AUTO POST GOD")
st.caption("Watchlist + Meme Radar + Fear & Greed + Auto Mode")

SYMBOL_MAP = {
    "BTC":"bitcoin","ETH":"ethereum","SOL":"solana","BNB":"binancecoin",
    "DOGE":"dogecoin","SHIB":"shiba-inu","PEPE":"pepe","BONK":"bonk",
    "FLOKI":"floki","WIF":"dogwifcoin"
}

def calc_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta>0,0).rolling(window=period).mean()
    loss = -delta.where(delta<0,0).rolling(window=period).mean()
    rs = gain/loss
    return 100 - (100/(1+rs))

@st.cache_data(ttl=600)
def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=8).json()
        return int(r['data'][0]['value']), r['data'][0]['value_classification']
    except:
        return 50, "Neutral"

@st.cache_data(ttl=300)
def get_markets():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1"
    try:
        return requests.get(url, timeout=12).json()
    except:
        return []

@st.cache_data(ttl=300)
def get_coin_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        r = requests.get(url, timeout=10).json()
        md = r['market_data']
        price = md['current_price']['usd']
        ch24 = md['price_change_percentage_24h']
        ch7 = md.get('price_change_percentage_7d',0)
        mcap = md['market_cap']['usd']
        vol = md['total_volume']['usd']
        url2 = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
        r2 = requests.get(url2, timeout=10).json()
        hist = pd.DataFrame(r2['prices'], columns=['timestamp','price'])
        hist['date'] = pd.to_datetime(hist['timestamp'], unit='ms')
        hist['MA7'] = hist['price'].rolling(7).mean()
        hist['RSI'] = calc_rsi(hist['price'])
        return price, ch24, ch7, mcap, vol, hist
    except:
        return None

# MODO AUTO?auto=1
params = st.query_params
is_auto = params.get("auto") == "1"

if is_auto:
    markets = get_markets()
    if markets:
        txt = "ALPHA AUTO %s | " % datetime.now().strftime("%d/%m")
        for m in markets[:5]:
            txt += f"{m['symbol'].upper()} ${m['current_price']} {m.get('price_change_percentage_24h',0):+.1f}% | "
        st.code(txt)
        st.write("ROBO_PRONTO")
