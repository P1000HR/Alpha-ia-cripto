import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Alpha V6 AUTO", page_icon="🤖", layout="wide")
st.title("🤖 ALPHA V6 - AUTO POST GOD")
st.caption("Watchlist + Meme Radar + Fear & Greed | V6.1 LIGHT")

SYMBOL_MAP = {"BTC":"bitcoin","ETH":"ethereum","SOL":"solana","DOGE":"dogecoin","SHIB":"shiba-inu","PEPE":"pepe","BONK":"bonk"}

@st.cache_data(ttl=600)
def get_price_simple(cid):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
        r = requests.get(url, timeout=8).json()
        d = r[cid]
        return d['usd'], d.get('usd_24h_change',0), d.get('usd_market_cap',0)
    except:
        return None

# SEMPRE MOSTRA ALGO, mesmo sem API
coin_input = st.sidebar.text_input("Moeda:", value="bitcoin").lower()
coin_id = SYMBOL_MAP.get(coin_input.upper(), coin_input)

if st.sidebar.button("Analisar"):
    st.cache_data.clear()

data = get_price_simple(coin_id)

if data:
    price, ch24, mcap = data
    st.markdown(f"## {coin_id.upper()} - ${price:,.6f}" if price<1 else f"## {coin_id.upper()} - ${price:,.2f}")
    c1,c2,c3 = st.columns(3)
    c1.metric("Preço", f"${price:,.4f}")
    c2.metric("24h", f"{ch24:.2f}%", f"{ch24:.2f}%")
    c3.metric("Market Cap", f"${mcap/1e9:.2f}B" if mcap else "N/A")

    # Grafico 7d
    try:
        url2 = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
        r2 = requests.get(url2, timeout=8).json()
        hist = pd.DataFrame(r2['prices'], columns=['t','price'])
        hist['date'] = pd.to_datetime(hist['t'], unit='ms')
        st.line_chart(hist.set_index('date')['price'], height=300)
    except:
        st.info("Gráfico carregando, recarregue em 5s")

    if ch24 > 3:
        st.success(f"### 🟢 COMPRA - {ch24:.2f}% alta forte")
    elif ch24 < -3:
        st.error(f"### 🔴 VENDA - {ch24:.2f}% queda forte")
    else:
        st.info(f"### 🟡 HOLD - {ch24:.2f}% neutro")

    promo = f"🤖 ALPHA V6: {coin_id.upper()} ${price:.4f} {ch24:+.2f}% #Cripto"
    st.code(promo)
    st.link_button("Postar no X", f"https://twitter.com/intent/tweet?text={promo}")
else:
    st.warning(f"Buscando {coin_id}... Se demorar, tenta bitcoin, ethereum, solana, pepe, dogecoin")
    st.info("Dica: a API gratuita limita 10-20 chamadas por minuto. Se travar, espera 1 min e clica em Analisar de novo.")

st.divider()
st.write("✅ V6.1 LIGHT - Carrega em 1 segundo | Se funcionou, me manda print")
