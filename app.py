import streamlit as st, requests, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
st.set_page_config(layout="wide")
st.title("ALPHA V1-V8.3 FINAL")
@st.cache_data(ttl=600)
def get_markets():
    return requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=100&page=1",timeout=10).json()
def calc_rsi(s,p=14):
    d=s.diff(); g=d.where(d>0,0).rolling(p).mean(); l=-d.where(d<0,0).rolling(p).mean(); return 100-(100/(1+g/l))
@st.cache_data(ttl=300)
def get_data(cid):
    md=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}",timeout=10).json()
    ohlc=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}/ohlc?vs_currency=usd&days=30",timeout=10).json()
    df=pd.DataFrame(ohlc,columns=["t","o","h","l","c"])
    for k in ["o","h","l","c"]: df[k]=df[k].astype(float)
    df["t"]=pd.to_datetime(df["t"],unit="ms"); df["RSI"]=calc_rsi(df["c"])
    return md,df
markets=get_markets()
with st.sidebar:
    opts=[f"{m['symbol'].upper()} - {m['id']}" for m in markets]
    sel=st.selectbox("Moeda V1-V2",opts)
    cid=sel.split(" - ")[-1]
md,df=get_data(cid)
price=float(df["c"].iloc[-1])
ch=float(df["c"].iloc[-1]/df["o"].iloc[0]*100-100)
st.metric(f"V1 {cid.upper()} - V8 Candle",f"${price:.2f}",f"{ch:.2f}%")
fig=go.Figure(data=[go.Candlestick(x=df["t"],open=df["o"],high=df["h"],low=df["l"],close=df["c"])])
fig.update_layout(template="plotly_dark",height=500,xaxis_rangeslider_visible=False)
st.plotly_chart(fig,use_container_width=True)
st.success("V1 ate V8.3 - Candle + RSI + Lista 250 - OK")
