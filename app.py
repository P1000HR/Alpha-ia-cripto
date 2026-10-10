import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title='ALPHA V1-V8.3', layout='wide')
st.title('ALPHA GOD V1-V8.3 COMPLETO FIX')
st.caption('V1 Preco | V2 250 | V3 Comparacao | V4 Portfolio RSI | V5 Fear | V6 Auto | V7 Candle | V8 MA')

def calc_rsi(s,p=14):
    d=s.diff()
    g=d.where(d>0,0).rolling(p).mean()
    l=-d.where(d<0,0).rolling(p).mean()
    rs=g/l
    return 100-(100/(1+rs))

@st.cache_data(ttl=600)
def get_fng():
    try:
        r=requests.get('https://api.alternative.me/fng/?limit=1',timeout=6).json()
        return int(r['data'][0]['value']),r['data'][0]['value_classification']
    except:
        return 50,'Neutral'

@st.cache_data(ttl=600)
def get_markets():
    try:
        url='https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&price_change_percentage=24h,7d'
        return requests.get(url,timeout=10).json()
    except:
        return []

@st.cache_data(ttl=300)
def get_hist(cid,days=30):
    try:
        md=requests.get(f'https://api.coingecko.com/api/v3/coins/{cid}',timeout=10).json()
        chart=requests.get(f'https://api.coingecko.com/api/v3/coins/{cid}/market_chart?vs_currency=usd&days={days}',timeout=10).json()['prices']
        hist=pd.DataFrame(chart,columns=['ts','price'])
        hist['date']=pd.to_datetime(hist['ts'],unit='ms')
        return md,hist
    except:
        return None,None

@st.cache_data(ttl=300)
def get_candle(cid,days=30):
    try:
        url=f'https://api.coingecko.com/api/v3/coins/{cid}/ohlc?vs_currency=usd&days={days}'
        r=requests.get(url,timeout=10).json()
        if not r or len(r)<5:
            return None
        df=pd.DataFrame(r,columns=['time','open','high','low','close'])
        for c in ['open','high','low','close']:
            df[c]=df[c].astype(float)
        df['time']=pd.to_datetime(df['time'],unit='ms')
        df['vol']=abs(df['close']-df['open'])*1000+1000
        df['RSI']=calc_rsi(df['close'],14)
        df['vol_media']=df['vol'].rolling(20).mean()
        df['baleia']=df['vol']>df['vol_media']*1.8
        df['MA20']=df['close'].rolling(20).mean()
        df['MA50']=df['close'].rolling(50).mean()
        return df
    except:
        return None

# V6 AUTO - FIX com aspas simples pra nao quebrar
params=st.query_params
if str(params.get('auto'))=='1':
    mk=get_markets()
    txt='ALPHA AUTO V6 '
    if mk:
        for m in mk[:5]:
            txt+=f"{m['symbol'].upper()} {m['current_price']} "
    st.code(txt)
    st.stop()

markets=get_markets()
fng_val,fng_txt=get_fng()

with st.sidebar:
    st.metric('V5 Fear',f'{fng_val}/100',fng_txt)
    modo=st.radio('V2 Busca',['Lista 250','Digitar'],0)
    if modo=='Lista 250' and markets:
        opts=[f"{m['name']} ({m['symbol'].upper()}) - {m['id']}" for m in markets]
        sel=st.selectbox('Escolha',opts)
        coin_id=sel.split(' - ')[-1]
    else:
        inp=st.text_input('V1 Moeda',value='bitcoin').strip().lower()
        coin_id=inp
    st.divider()
    st.subheader('V3 Comparacao')
    ids=[m['id'] for m in markets] if markets else ['bitcoin','ethereum','solana','pepe']
    comp=st.multiselect('Compare ate 2',ids,max_selections=2)
    st.divider()
    qtd=st.number_input('V4 Qtd',value=1.0)
    invest=st.number_input('V4 Investido',value=1000.0)
    show_ma=st.checkbox('V8 MA',True)
    show_baleia=st.checkbox('V7 Baleias',True)

md,hist=get_hist(coin_id,30)
if md is None:
    st.error('Moeda nao achada')
    st.stop()

ch24=md['market_data']['price_change_percentage_24h']
price=md['market_data']['current_price']['usd']
ath=md['market_data']['ath']['usd']
mcap=md['market_data']['market_cap']['usd']

df=get_candle(coin_id,30)
if df is not None and len(df)>0:
    price_display=float(df['close'].iloc[-1])
    rsi_display=float(df['RSI'].dropna().iloc[-1]) if len(df['RSI'].dropna())>0 else 50.0
else:
    price_display=price
    rsi_display=50.0

st.markdown(f'## V1 {coin
