import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="ALPHA ULTIMATE V1-V6", page_icon="👑", layout="wide")

st.markdown("""
<style>
.stApp {background:#07080c; color:#eee;}
.title {font-size:46px; font-weight:900; background:linear-gradient(90deg,#00ff88,#00d4ff,#ff00ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.card {background:#13141c; border:1px solid #222; padding:14px; border-radius:14px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">👑 ALPHA ULTIMATE V1→V6</div>', unsafe_allow_html=True)
st.caption("V1 Preço + V2 250 moedas + V3 Comparação + V4 RSI + V5 Fear & Meme + V6 Auto Post | TUDO EM 1")

# --- CORE FUNCS (V1-V6) ---
SYMBOL_MAP = {"BTC":"bitcoin","ETH":"ethereum","SOL":"solana","BNB":"binancecoin","XRP":"ripple","DOGE":"dogecoin","SHIB":"shiba-inu","PEPE":"pepe","BONK":"bonk","FLOKI":"floki","WIF":"dogwifcoin","AVAX":"avalanche-2","DOT":"polkadot","LINK":"chainlink","ADA":"cardano"}

def calc_rsi(s, p=14):
    d=s.diff(); g=d.where(d>0,0).rolling(p).mean(); l=-d.where(d<0,0).rolling(p).mean(); rs=g/l; return 100-(100/(1+rs))

@st.cache_data(ttl=600)
def get_fng():
    try:
        r=requests.get("https://api.alternative.me/fng/?limit=1", timeout=6).json()
        return int(r['data'][0]['value']), r['data'][0]['value_classification']
    except: return 50,"Neutral"

@st.cache_data(ttl=600)
def get_markets():
    url="https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&price_change_percentage=24h,7d"
    try: return requests.get(url, timeout=12).json()
    except: return []

@st.cache_data(ttl=300)
def get_trending():
    try: return requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=8).json()['coins']
    except: return []

@st.cache_data(ttl=300)
def get_coin_full(cid):
    try:
        md=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}", timeout=10).json()['market_data']
        chart=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart?vs_currency=usd&days=30", timeout=10).json()['prices']
        hist=pd.DataFrame(chart, columns=['ts','price'])
        hist['date']=pd.to_datetime(hist['ts'], unit='ms')
        hist['MA7']=hist['price'].rolling(7).mean()
        hist['MA25']=hist['price'].rolling(25).mean()
        hist['RSI']=calc_rsi(hist['price'])
        return md, hist
    except: return None, None

# --- MODO AUTO (V6)?auto=1 ---
params=st.query_params
if params.get("auto")=="1":
    mk=get_markets()
    txt=f"ALPHA AUTO {datetime.now().strftime('%d/%m %H:%M')} | "
    if mk:
        for m in mk[:5]: txt+=f"{m['symbol'].upper()} ${m['current_price']} {m.get('price_change_percentage_24h',0):+.1f}% | "
    st.code(txt); st.write("ROBO_PRONTO"); st.stop()

# --- SIDEBAR V2+V3+V5 ---
markets=get_markets()
fng_val,fng_txt=get_fng()
trending=get_trending()

with st.sidebar:
    st.metric("😱 Fear & Greed", f"{fng_val}/100", fng_txt)
    if fng_val<25: st.error("MEDO EXTREMO - COMPRAR")
    elif fng_val>75: st.warning("GANANCIA EXTREMA - VENDER")

    st.divider()
    st.subheader("🔍 Buscar (V2-V3)")
    modo=st.radio("Como buscar?", ["Lista Top 250","Digitar BTC/ETH/PEPE"])
    if modo=="Lista Top 250" and markets:
        opts=[f"{m['name']} ({m['symbol'].upper()}) - {m['id']}" for m in markets]
        sel=st.selectbox("Escolha:", opts)
        coin_id=sel.split(" - ")[-1]
    else:
        inp=st.text_input("Digite:", value="bitcoin").strip()
        coin_id=SYMBOL_MAP.get(inp.upper(), inp.lower())

    st.divider()
    st.subheader("⭐ Watchlist V3 (comparar até 2)")
    ids=[m['id'] for m in markets] if markets else list(SYMBOL_MAP.values())
    comp=st.multiselect("Comparar com:", ids, max_selections=2)

    st.divider()
    st.subheader("💼 Portfólio V4")
    qtd=st.number_input("Qtd moedas:", value=1.0)
    invest=st.number_input("Investido USD:", value=1000.0)

    st.divider()
    st.subheader("🔥 Trending V5")
    for t in trending[:5]:
        st.write(f"{t['item']['symbol']} - {t['item']['name']}")

    st.divider()
    st.subheader("💎 Meme Radar V5")
    if markets:
        memes=[m for m in markets if m['current_price']<0.01 and (m.get('price_change_percentage_24h') or 0)>10]
        for m in memes[:5]:
            st.write(f"{m['symbol'].upper()} {m['price_change_percentage_24h']:+.1f}%")

# --- MAIN V1-V6 ---
md,hist = get_coin_full(coin_id)
if md is None:
    st.error(f"{coin_id} não encontrada. Tenta bitcoin, ethereum, pepe")
    st.stop()

price=md['current_price']['usd']
ch24=md['price_change_percentage_24h']
ch7=md.get('price_change_percentage_7d',0)
ch30=md.get('price_change_percentage_30d',0)
mcap=md['market_cap']['usd']
vol=md['total_volume']['usd']
rsi_now=float(hist['RSI'].dropna().iloc[-1]) if not hist['RSI'].dropna().empty else 50

# V1 - PREÇO
st.markdown(f"## {coin_id.upper()} - ${price:,.8f}" if price<1 else f"## {coin_id.upper()} - ${price:,.2f}")
c1,c2,c3,c4=st.columns(4)
c1.metric("24h", f"{ch24:.2f}%", f"{ch24:.2f}%")
c2.metric("7d", f"{ch7:.2f}%")
c3.metric("RSI V4", f"{rsi_now:.0f}", "Sobrecompra" if rsi_now>70 else "Sobrevenda" if rsi_now<30 else "Neutro")
c4.metric("Market Cap", f"${mcap/1e9:.2f}B")

# V4 - SINAL + V5 - GOD SCORE
score=0
if rsi_now<35: score+=30
if ch24<-8: score+=20
if fng_val<30: score+=25
if price < float(hist['MA25'].dropna().iloc[-1]): score+=15
st.progress(min(score,100)/100, text=f"👑 GOD SCORE V5: {score}/90 - {'ALTA OPORTUNIDADE' if score>60 else 'NEUTRO'}")

# TABS V1-V6
tab1,tab2,tab3,tab4 = st.tabs(["📈 Gráfico + Médias V4","🤖 IA Previsão V5","💼 Portfólio V4","📢 Auto Post V6"])

with tab1:
    # V3 COMPARAÇÃO
    if comp:
        df_comp=pd.DataFrame()
        all_ids=[coin_id]+comp
        for cid in all_ids:
            _,h=get_coin_full(cid)
            if h is not None:
                tmp=h.set_index('date')[['price']].copy()
                tmp[f'{cid} %']=(tmp['price']/tmp['price'].iloc[0]-1)*100
                df_comp=pd.concat([df_comp, tmp[[f'{cid} %']]], axis=1)
        st.line_chart(df_comp, height=380)
        st.caption("V3 - Comparativo % normalizado 30 dias")
    else:
        st.line_chart(hist.set_index('date')[['price','MA7','MA25']], height=380)
        st.caption("V4 - Preço + MA7 + MA25")
    st.line_chart(hist.set_index('date')['RSI'], height=180)

with tab2:
    last10=hist.tail(10); x=np.arange(len(last10)); y=last10['price'].values
    coef=np.polyfit(x,y,1); alvo=y[-1]+coef[0]*7
    st.markdown(f"""
    <div class="card">
    <b>V5 IA Insights:</b><br>
    - RSI {rsi_now:.0f}: {"Sobrecompra - risco correção" if rsi_now>70 else "Sobrevenda - oportunidade" if rsi_now<30 else "Neutro"}<br>
    - Tendência: <b>{"ALTA" if coef[0]>0 else "BAIXA"}</b><br>
    - Alvo 7d: <b>${alvo:,.6f} ({(alvo/price-1)*100:+.2f}%)</b><br>
    - Fear {fng_val} ({fng_txt})<br>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    valor_atual=price*qtd; lucro=valor_atual-invest
    st.metric("Valor Atual", f"${valor_atual:,.2f}", f"${lucro:,.2f}")
    ath=md['ath']['usd']
    st.write(f"Se voltar no ATH ${ath:,.2f}, valeria **${qtd*ath:,.2f}** ({(ath/price-1)*100:+.1f}%)")

with tab4:
    sinal="HOLD"
    if rsi_now>70 and ch24>3: sinal="🔴 VENDER TOPO"
    elif rsi_now<30: sinal="🟢 COMPRAR FUNDO"
    elif ch24>2: sinal="🟢 COMPRA"
    elif ch24<-2: sinal="🔴 VENDA"
    else: sinal="🟡 HOLD"

    if "COMPRAR" in sinal or "COMPRA" in sinal: st.success(f"### {sinal}")
    elif "VENDER" in sinal or "VENDA" in sinal: st.error(f"### {sinal}")
    else: st.info(f"### {sinal}")

    promo=f"👑 ALPHA ULTIMATE V1-V6: {coin_id.upper()} ${price:.4f} {ch24:+.2f}% RSI {rsi_now:.0f} Fear {fng_val} {sinal} | gmdny.streamlit.app #CriptoGOD"
    st.code(promo)
    cA,cB,cC=st.columns(3)
    cA.link_button("🐦 Postar X", f"https://twitter.com/intent/tweet?text={promo[:250]}")
    cB.download_button("📥 CSV 30d", hist.to_csv(index=False), f"{coin_id}_ultimate.csv")
    if cC.button("🤖 Testar Modo Robô"):
        st.query_params["auto"]="1"; st.rerun()

st.success("✅ ULTIMATE V1-V6 CARREGADO - Você tem TODAS as versões em 1 só app!")
