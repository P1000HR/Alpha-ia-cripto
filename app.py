import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Alpha V5 GOD", page_icon="👑", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp {background:#050507; color:#eee;}
.god {font-size:54px; font-weight:900; background: linear-gradient(90deg,#00ff88,#00ccff); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.card {background:#15151a; border:1px solid #2a2a35; padding:16px; border-radius:16px; margin-bottom:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="god">👑 ALPHA V5 GOD MODE</div>', unsafe_allow_html=True)
st.caption("Fear & Greed + Meme Radar + Trending + AI Chat | Terminal profissional")

SYMBOL_MAP = {"BTC":"bitcoin","ETH":"ethereum","SOL":"solana","DOGE":"dogecoin","SHIB":"shiba-inu","PEPE":"pepe","BONK":"bonk","WIF":"dogwifcoin","FLOKI":"floki","BRETT":"brett"}

def calc_rsi(s, p=14):
    d=s.diff(); g=d.where(d>0,0).rolling(p).mean(); l=-d.where(d<0,0).rolling(p).mean()
    return 100-(100/(1+g/l))

@st.cache_data(ttl=600)
def get_fear_greed():
    try:
        r=requests.get("https://api.alternative.me/fng/?limit=1", timeout=8).json()
        return int(r['data'][0]['value']), r['data'][0]['value_classification']
    except: return 50,"Neutral"

@st.cache_data(ttl=300)
def get_trending():
    try:
        r=requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10).json()
        return r['coins']
    except: return []

@st.cache_data(ttl=600)
def get_markets():
    url="https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&price_change_percentage=24h"
    try: return requests.get(url, timeout=15).json()
    except: return []

@st.cache_data(ttl=300)
def get_coin_full(cid):
    try:
        url=f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart?vs_currency=usd&days=30"
        hist=pd.DataFrame(requests.get(url, timeout=12).json()['prices'], columns=['t','price'])
        hist['date']=pd.to_datetime(hist['t'], unit='ms')
        hist['MA7']=hist['price'].rolling(7).mean()
        hist['MA25']=hist['price'].rolling(25).mean()
        hist['RSI']=calc_rsi(hist['price'])
        info=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}", timeout=10).json()['market_data']
        return hist, info
    except: return None, None

# SIDEBAR GOD
markets = get_markets()
fg_val, fg_txt = get_fear_greed()
trending = get_trending()

with st.sidebar:
    st.metric("😱 Fear & Greed", f"{fg_val}/100", fg_txt)
    if fg_val<25: st.error("MEDO EXTREMO - Oportunidade de compra")
    elif fg_val>75: st.warning("GANÂNCIA EXTREMA - Cuidado com topo")

    st.divider()
    entrada=st.text_input("Moeda:", value="bitcoin")
    coin_id=SYMBOL_MAP.get(entrada.upper(), entrada.lower())

    st.divider()
    st.subheader("🔥 Trending AGORA")
    for t in trending[:6]:
        item=t['item']
        st.write(f"**{item['symbol']}** - {item['name']} (rank {item['market_cap_rank']})")

    st.divider()
    st.subheader("💎 Meme Radar (<$0.01 + >10% hoje)")
    if markets:
        memes=[m for m in markets if m['current_price']<0.01 and (m.get('price_change_percentage_24h') or 0)>10]
        for m in memes[:8]:
            st.write(f"{m['symbol'].upper():6} ${m['current_price']:.6f} {m['price_change_percentage_24h']:+.1f}%")

# MAIN COIN
res = get_coin_full(coin_id)
if res[0] is None:
    st.error(f"{coin_id} não encontrada")
    st.stop()
hist, md = res
price=md['current_price']['usd']
ch24=md['price_change_percentage_24h']
ch7=md.get('price_change_percentage_7d',0)
rsi_now=hist['RSI'].iloc[-1]

c1,c2,c3 = st.columns([2,1,1])
with c1:
    st.markdown(f"## {coin_id.upper()} ${price:,.8f}" if price<0.01 else f"## {coin_id.upper()} ${price:,.2f}")
    st.write(f"Market Cap ${md['market_cap']['usd']/1e9:.2f}B | Vol ${md['total_volume']['usd']/1e9:.2f}B | ATH ${md['ath']['usd']:,.2f}")
with c2:
    st.metric("24h", f"{ch24:.2f}%")
    st.metric("RSI", f"{rsi_now:.0f}", "Sobrecompra" if rsi_now>70 else "Sobrevenda" if rsi_now<30 else "Neutro")
with c3:
    # OPORTUNIDADE SCORE
    score=0
    if rsi_now<35: score+=30
    if ch24<-8: score+=20
    if fg_val<30: score+=25
    if price<hist['MA25'].iloc[-1]: score+=15
    st.metric("👑 GOD Score", f"{score}/90", "ALTA Oportunidade" if score>60 else "Neutro")

t1,t2,t3,t4 = st.tabs(["📈 Gráfico GOD", "🤖 IA Insights", "💼 Simulador Whale", "💬 Alpha Chat"])

with t1:
    st.line_chart(hist.set_index('date')[['price','MA7','MA25']], height=400)
    st.caption("Preto=Preço | Azul=MA7 | Vermelho=MA25 | Cruzamento MA7>MA25 = Alta")

with t2:
    colA,colB = st.columns(2)
    with colA:
        st.markdown(f"""
        <div class="card">
        <b>🧠 Análise IA Automática</b><br><br>
        • RSI: {rsi_now:.0f} - {"Sobrecomprado, risco de correção" if rsi_now>70 else "Sobrevendido, possível reversão" if rsi_now<30 else "Neutro, tendência segue"}<br>
        • vs MA25: {"Acima da média (força)" if price>hist['MA25'].iloc[-1] else "Abaixo da média (fraqueza)"}<br>
        • Fear & Greed {fg_val} ({fg_txt}) - {"Mercado com medo, bons pontos de entrada" if fg_val<40 else "Mercado ganancioso, realizar lucros"}<br>
        • Volatilidade 7d: {(hist['price'].pct_change().std()*100):.2f}%<br>
        </div>
        """, unsafe_allow_html=True)
    with colB:
        # previsão
        x=np.arange(len(hist.tail(10))); y=hist.tail(10)['price'].values
        coef=np.polyfit(x,y,1)
        alvo=y[-1]+coef[0]*7
        st.markdown(f"""
        <div class="card">
        <b>🔮 Previsão 7 dias (modelo linear)</b><br><br>
        Tendência: <b>{"ALTA 📈" if coef[0]>0 else "BAIXA 📉"}</b><br>
        Alvo estimado: <b>${alvo:,.6f}</b><br>
        Retorno estimado: <b>{(alvo/price-1)*100:+.2f}%</b><br><br>
        ⚠️ Não é conselho financeiro, apenas estatística.
        </div>
        """, unsafe_allow_html=True)

with t3:
    st.subheader("🐋 Simulador Whale")
    aporte=st.slider("Se investisse quanto?", 100, 10000, 1000, step=100)
    qtd_token=aporte/price
    st.write(f"Com ${aporte} você compra {qtd_token:,.2f} {coin_id.upper()}")
    st.write(f"Se voltar no ATH (${md['ath']['usd']:,.2f}), seu valor seria: **${qtd_token*md['ath']['usd']:,.2f}** ({(md['ath']['usd']/price-1)*100:+.1f}%)")
    st.bar_chart(pd.DataFrame({"valor":[aporte, qtd_token*md['ath']['usd']]}, index=["Hoje","No ATH"]))

with t4:
    st.subheader("💬 Alpha Chat (simulado IA)")
    pergunta=st.text_input("Pergunte: 'Devo comprar agora?', 'Qual meme vai bombar?'")
    if pergunta:
        if "comprar" in pergunta.lower():
            resp = f"Baseado em RSI {rsi_now:.0f} e Fear {fg_val}, {'é bom momento de compra escalonada' if rsi_now<40 and fg_val<40 else 'melhor aguardar correção, mercado ganancioso' if rsi_now>65 else 'mercado neutro, compre 50% agora e 50% se cair 10%'}."
        elif "meme" in pergunta.lower():
            top_meme = sorted([m for m in markets if m['current_price']<1], key=lambda x: x.get('price_change_percentage_24h',0) or 0, reverse=True)[:3] if markets else []
            resp = f"Meme coins bombando hoje: {', '.join([m['symbol'].upper()+' '+str(round(m.get('price_change_percentage_24h',0),1))+'%' for m in top_meme])}. Foco em volume alto."
        else:
            resp = f"{coin_id.upper()} está com tendência {'de alta' if ch24>0 else 'de baixa'} de {ch24:.2f}% 24h, RSI {rsi_now:.0f}. Minha leitura: { 'acumular' if rsi_now<40 else 'realizar parcialmente' if rsi_now>70 else 'hold'}."
        st.info(f"🤖 Alpha: {resp}")

# FOOTER PROMO
st.divider()
promo=f"👑 GOD ALERT: {coin_id.upper()} ${price:.6f} {ch24:+.2f}% | RSI {rsi_now:.0f} | Fear {fg_val} ({fg_txt}) | GOD Score {score}/90 | #AlphaV5 #CriptoGOD"
col1,col2,col3=st.columns(3)
col1.code(promo)
col2.download_button("📥 Exportar 30d CSV", hist.to_csv(index=False), f"{coin_id}_V5.csv")
col3.link_button("🐦 Postar no X", f"https://twitter.com/intent/tweet?text={promo[:250]}")

st.success("V5 GOD no ar! Agora você tem terminal melhor que muita corretora.")
