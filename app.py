import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Alpha AI Crypto Analyzer v3", page_icon="🚀", layout="wide")
st.title("🚀 Alpha AI Crypto Analyzer v3 - 250+ Moedas")
st.caption("Agora com 250+ criptos, comparação e top gainers")

# MAPA DE SÍMBOLOS -> ID (pra aceitar BTC, ETH, etc)
SYMBOL_MAP = {
    "BTC":"bitcoin", "ETH":"ethereum", "SOL":"solana", "BNB":"binancecoin",
    "XRP":"ripple", "DOGE":"dogecoin", "ADA":"cardano", "SHIB":"shiba-inu",
    "PEPE":"pepe", "BONK":"bonk", "FLOKI":"floki", "WIF":"dogwifcoin",
    "AVAX":"avalanche-2", "DOT":"polkadot", "LINK":"chainlink", "MATIC":"matic-network",
    "LTC":"litecoin", "UNI":"uniswap", "TRX":"tron", "ETC":"ethereum-classic"
}

@st.cache_data(ttl=3600)
def get_top_coins():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false"
        r = requests.get(url, timeout=15).json()
        df = pd.DataFrame([{"id":x['id'], "symbol":x['symbol'].upper(), "name":x['name']} for x in r])
        return r, df
    except:
        return [], pd.DataFrame()

@st.cache_data(ttl=600)
def get_coin_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        r = requests.get(url, timeout=10).json()
        price = r['market_data']['current_price']['usd']
        ch24 = r['market_data']['price_change_percentage_24h']
        ch7 = r['market_data']['price_change_percentage_7d']
        mcap = r['market_data']['market_cap']['usd']
        vol = r['market_data']['total_volume']['usd']
        url2 = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
        r2 = requests.get(url2, timeout=10).json()
        hist = pd.DataFrame(r2['prices'], columns=['timestamp','price'])
        hist['date'] = pd.to_datetime(hist['timestamp'], unit='ms')
        hist['coin'] = coin_id
        return price, ch24, ch7, mcap, vol, hist
    except:
        return None

# CARREGA LISTA
markets, coins_df = get_top_coins()

# SIDEBAR
st.sidebar.header("🔍 Buscar Cripto")
modo = st.sidebar.radio("Como quer buscar?", ["Lista Top 250", "Digitar nome/símbolo"])

if modo == "Lista Top 250" and not coins_df.empty:
    opcoes = [f"{row['name']} ({row['symbol']}) - {row['id']}" for _, row in coins_df.iterrows()]
    escolha = st.sidebar.selectbox("Escolha a cripto:", opcoes)
    cripto_id = escolha.split(" - ")[-1]
    comparacao = st.sidebar.multiselect("Comparar com (até 2):", coins_df['id'].tolist(), max_selections=2)
else:
    entrada = st.sidebar.text_input("Digite (ex: bitcoin, BTC, pepe):", value="bitcoin").strip()
    e_upper = entrada.upper()
    cripto_id = SYMBOL_MAP.get(e_upper, entrada.lower())
    comparacao = []

# TOP GAINERS
if markets:
    st.sidebar.divider()
    st.sidebar.subheader("🔥 Top 5 Alta hoje")
    top = sorted(markets, key=lambda x: x.get('price_change_percentage_24h',0) or 0, reverse=True)[:5]
    for t in top:
        st.sidebar.write(f"{t['symbol'].upper()}: {t.get('price_change_percentage_24h',0):.2f}%")

# ANALISE PRINCIPAL
data = get_coin_data(cripto_id)
if not data:
    st.error(f"'{cripto_id}' não encontrada. Tenta da lista Top 250.")
    st.stop()

price, ch24, ch7, mcap, vol, hist = data
st.markdown(f"## {cripto_id.upper()} - ${price:,.6f}" if price < 1 else f"## {cripto_id.upper()} - ${price:,.2f}")
c1,c2,c3,c4 = st.columns(4)
c1.metric("24h", f"{ch24:.2f}%", f"{ch24:.2f}%")
c2.metric("7d", f"{ch7:.2f}%", f"{ch7:.2f}%")
c3.metric("Market Cap", f"${mcap/1e9:.2f}B")
c4.metric("Volume", f"${vol/1e9:.2f}B")

# GRAFICO COMPARATIVO
st.subheader("📈 Comparativo 7 dias")
all_hist = hist.copy()
for comp_id in comparacao:
    d2 = get_coin_data(comp_id)
    if d2:
        _,_,_,_,_,h2 = d2
        # normaliza pra % pra comparar
        h2['price_norm'] = (h2['price']/h2['price'].iloc[0]-1)*100
        all_hist = pd.concat([all_hist, h2])

if comparacao:
    # grafico normalizado
    pivot = pd.DataFrame()
    for cid in [cripto_id]+comparacao:
        d = get_coin_data(cid)
        if d:
            _,_,_,_,_,h = d
            h = h.set_index('date')
            h[f'{cid} %'] = (h['price']/h['price'].iloc[0]-1)*100
            pivot = pd.concat([pivot, h[[f'{cid} %']]], axis=1)
    st.line_chart(pivot, height=350)
else:
    st.line_chart(hist.set_index('date')['price'], height=350)

# SINAL
if ch24 > 5: sinal="🟢 COMPRA FORTE"
elif ch24 > 1: sinal="🟢 COMPRA"
elif ch24 < -5: sinal="🔴 VENDA"
elif ch24 < -1: sinal="🟡 CAUTELA"
else: sinal="🟡 NEUTRO"
if "COMPRA" in sinal: st.success(f"### {sinal} - {ch24:.2f}% 24h")
elif "VENDA" in sinal: st.error(f"### {sinal} - {ch24:.2f}% 24h")
else: st.info(f"### {sinal} - {ch24:.2f}% 24h")

st.divider()
promo = f"🚀 ALPHA V3: {cripto_id.upper()} ${price:.4f} ({ch24:+.2f}% 24h) {sinal} | Top 250 moedas | #alphaIA #cripto"
st.code(promo)
