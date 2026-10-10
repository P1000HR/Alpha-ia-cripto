import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="ALPHA GOD V1-V8.3 COMPLETO", page_icon="fire", layout="wide")
st.title("ALPHA GOD V1-V8.3 COMPLETO")
st.caption("V1 Preco | V2 250 | V3 Comparacao | V4 Portfolio RSI | V5 Fear Meme Trending | V6 Auto | V7 Candle Baleias | V8 Indicadores")

SYMBOL_MAP = {"BTC":"bitcoin","ETH":"ethereum","SOL":"solana","PEPE":"pepe","DOGE":"dogecoin","SHIB":"shiba-inu","BONK":"bonk"}

def calc_rsi(s, p=14):
    d = s.diff()
    g = d.where(d>0,0).rolling(p).mean()
    l = -d.where(d<0,0).rolling(p).mean()
    rs = g / l
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=600)
def get_fng():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6).json()
        return int(r["data"][0]["value"]), r["data"][0]["value_classification"]
    except:
        return 50, "Neutral"

@st.cache_data(ttl=600)
def get_markets():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&price_change_percentage=24h,7d"
    try:
        return requests.get(url, timeout=12).json()
    except:
        return []

@st.cache_data(ttl=600)
def get_trending():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=8).json()
        return r["coins"]
    except:
        return []

@st.cache_data(ttl=300)
def get_hist(cid, days=30):
    try:
        md = requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}", timeout=10).json()
        chart = requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart?vs_currency=usd&days={days}", timeout=10).json()["prices"]
        hist = pd.DataFrame(chart, columns=["ts","price"])
        hist["date"] = pd.to_datetime(hist["ts"], unit="ms")
        return md, hist
    except:
        return None, None

@st.cache_data(ttl=300)
def get_candle(cid, days=30):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{cid}/ohlc?vs_currency=usd&days={days}"
        r = requests.get(url, timeout=10).json()
        if not r or len(r) < 5:
            return None
        df = pd.DataFrame(r, columns=["time","open","high","low","close"])
        for c in ["open","high","low","close"]:
            df[c] = df[c].astype(float)
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        df["vol"] = abs(df["close"]-df["open"])*1000+1000
        df["RSI"] = calc_rsi(df["close"],14)
        df["vol_media"] = df["vol"].rolling(20).mean()
        df["baleia"] = df["vol"] > df["vol_media"]*1.8
        df["MA20"] = df["close"].rolling(20).mean()
        df["MA50"] = df["close"].rolling(50).mean()
        return df
    except:
        return None

# V6 AUTO MODE
params = st.query_params
if params.get("auto") == "1
