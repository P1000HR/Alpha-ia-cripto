import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="ALPHA ULTIMATE", page_icon="fire", layout="wide")
st.title("ALPHA ULTIMATE V1-V8")
st.caption("Fix 8.1 - Sem erro de sintaxe")

SYMBOL_MAP = {"BTC":"bitcoin","ETH":"ethereum","SOL":"solana","PEPE":"pepe","DOGE":"dogecoin","SHIB":"shiba-inu","BONK":"bonk"}
BINANCE_MAP = {"bitcoin":"BTCUSDT","ethereum":"ETHUSDT","solana":"SOLUSDT","pepe":"PEPEUSDT","dogecoin":"DOGEUSDT","BTC":"BTCUSDT","ETH":"ETHUSDT","SOL":"SOLUSDT","PEPE":"PEPEUSDT"}

def calc_rsi(s, p=14):
    d=s.diff()
    g=d.where(d>0,0).rolling(p).mean()
    l=-d.where(d<0,0).rolling(p).mean()
    rs=g/l
    return 100-(100/(1+rs))

def calc_bb(s, p=20, std=2):
    ma=s.rolling(p).mean()
    sd=s.rolling(p).std()
    return ma+sd*std, ma, ma-sd*std

@st.cache_data(ttl=600)
def get_fng():
    try:
        r=requests.get("https://api.alternative.me/fng/?limit=1", timeout=6).json()
        return int(r['data'][0]['value']), r['data'][0]['value_classification']
    except:
        return 50,"Neutral"

@st.cache_data(ttl=600)
def get_markets():
    url="https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&price_change_percentage=24h,7d"
    try:
        return requests.get(url, timeout=12).json()
    except:
        return []

@st.cache_data(ttl=300)
def get_coingecko_hist(cid, days=30):
    try:
        md=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}", timeout=10).json()
        chart=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart?vs_currency=usd&days={days}", timeout=10).json()['prices']
        hist=pd.DataFrame(chart, columns=['ts','price'])
        hist['date']=pd.to_datetime(hist['ts'], unit='ms')
        return md, hist
    except:
        return None, None

def get_binance_candles(binance_symbol, interval_map, limit=200):
    try:
        url=f"https://api.binance.com/api/v3/klines?symbol={binance_symbol}&interval={interval_map}&limit={limit}"
        r=requests.get(url, timeout=10).json()
        df=pd.DataFrame(r, columns=['time','open','high','low','close','vol','ct','qav','trades','tbav','tqav','ignore'])
        for col in ['open','high','low','close','vol']:
            df[col]=df[col].astype(float)
        df['time']=pd.to_datetime(df['time'], unit='ms')
        df['RSI']=calc_rsi(df['close'], 14)
        df['vol_media']=df['vol'].rolling(20).mean()
        df['baleia']=df['vol'] > df['vol_media']*2.2
        return df
    except:
        return None

params=st.query_params
if params.get("auto")=="1":
    mk=get_markets()
    txt="ALPHA AUTO "
    if mk:
        for m in mk[:5]:
            txt+=f"{m['symbol'].upper()} {m['current_price']} "
    st.code(txt)
    st.stop()

markets=get_markets()
fng_val,fng_txt=get_fng()

with st.sidebar:
    st.metric("Fear & Greed", f"{fng_val}/100", fng_txt)
    st.divider()
    modo=st.radio("Busca:", ["Lista 250","Digitar BTC/PEPE"])
    if modo=="Lista 250" and markets:
        opts=[f"{m['name']} ({m['symbol'].upper()}) - {m['id']}" for m in markets]
        sel=st.selectbox("Escolha:", opts)
        coin_id=sel.split(" - ")[-1]
        inp=coin_id
    else:
        inp=st.text_input("Digite:", value="bitcoin").strip()
        coin_id=SYMBOL_MAP.get(inp.upper(), inp.lower())
    bin_symbol=BINANCE_MAP.get(coin_id, f"{inp.upper()}USDT")

    st.divider()
    timeframe=st.selectbox("Tempo:", ["1m","3m","5m","15m","30m","1h","4h","1d","1w","1M"], index=5)
    map_interval={"1m":"1m","3m":"3m","5m":"5m","15m":"15m","30m":"30m","1h":"1h","4h":"4h","1d":"1d","1w":"1w","1M":"1M"}
    bin_interval=map_interval[timeframe]

    st.divider()
    show_ma=st.checkbox("MA 20/50", value=True)
    show_rsi=st.checkbox("RSI", value=True)
    show_baleia=st.checkbox("Baleias", value=True)
    show_bb=st.checkbox("Bollinger", value=False)

md, hist_line = get_coingecko_hist(coin_id, 30)
if md is None:
    st.error(f"{coin_id} nao achada. Tenta bitcoin, ethereum, pepe")
    st.stop()

md_data=md['market_data']
price=md_data['current_price']['usd']
ch24=md_data['price_change_percentage_24h']
ch7=md_data.get('price_change_percentage_7d',0)

df_candle=get_binance_candles(bin_symbol, bin_interval)

if df_candle is not None:
    price_display=df_candle['close'].iloc[-1]
    rsi_display=df_candle['RSI'].iloc[-1]
else:
    hist_line['RSI']=calc_rsi(hist_line['price'])
    price_display=price
    if hist_line['RSI'].dropna().empty:
        rsi_display=50
    else:
        rsi_display=float(hist_line['RSI'].dropna().iloc[-1])

st.markdown(f"## {coin_id.upper()} / {bin_symbol}")
st.write(f"Preco: ${price_display}")
c1,c2,c3,c4=st.columns(4)
c1.metric("24h", f"{ch24:.2f}%")
c2.metric("7d", f"{ch7:.2f}%")
c3.metric("RSI", f"{rsi_display:.0f}")
c4.metric("Fear", f"{fng_val}")

score=0
if rsi_display<35:
    score+=30
if ch24<-8:
    score+=20
if fng_val<30:
    score+=25
st.progress(min(score,90)/90, text=f"GOD SCORE: {score}/90")

tab_candle, tab_line = st.tabs(["CANDLE PRO","LINHA"])

with tab_candle:
    if df_candle is None:
        st.line_chart(hist_line.set_index('date')['price'], height=350)
    else:
        df_candle['MA20']=df_candle['close'].rolling(20).mean()
        df_candle['MA50']=df_candle['close'].rolling(50).mean()
        df_candle['BB_up'], df_candle['BB_mid'], df_candle['BB_low']=calc_bb(df_candle['close'])
        fig=make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75,0.25], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(x=df_candle['time'], open=df_candle['open'], high=df_candle['high'], low=df_candle['low'], close=df_candle['close'], name="Candle"), row=1, col=1)
        if show_ma:
            fig.add_trace(go.Scatter(x=df_candle['time'], y=df_candle['MA20'], name="MA20"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_candle['time'], y=df_candle['MA50'], name="MA50"), row=1, col=1)
        if show_bb:
            fig.add_trace(go.Scatter(x=df_candle['time'], y=df_candle['BB_up'], name="BB Up"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_candle['time'], y=df_candle['BB_low'], name="BB Low"), row=1, col=1)
        if show_baleia:
            baleias=df_candle[df_candle['baleia']]
            fig.add_trace(go.Scatter(x=baleias['time'], y=baleias['high']*1.005, mode='markers', name='BALEIA', marker=dict(size=10, color='gold', symbol='star')), row=1, col=1)
        if show_rsi:
            fig.add_trace(go.Scatter(x=df_candle['time'], y=df_candle['RSI'], name="RSI"), row=2, col=1)
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with tab_line:
    st.line_chart(hist_line.set_index('date')['price'], height=350)

if rsi_display>70:
    sinal="VENDER TOPO"
elif rsi_display<30:
    sinal="COMPRAR FUNDO"
elif ch24>2:
    sinal="COMPRA"
elif ch24<-2:
    sinal="VENDA"
else:
    sinal="HOLD"

if "COMPRA" in sinal:
    st.success(sinal)
elif "VENDA" in sinal:
    st.error(sinal)
else:
    st.info(sinal)

promo=f"ULTIMATE V1-V8: {coin_id.upper()} {bin_symbol} {price_display:.4f} {ch24:+.2f}% RSI {rsi_display:.0f} Fear {fng_val} {sinal} | {timeframe}"
st.code(promo)
st.link_button("Postar no X", f"https://twitter.com/intent/tweet?text={promo[:250]}")
st.write("ULTIMATE V1-V8 FIX 8.1 CARREGADO")
