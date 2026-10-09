import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Alpha AI Crypto Analyzer v2", page_icon="🚀", layout="wide")

st.title("🚀 Alpha AI Crypto Analyzer v2")
st.caption("Análise com IA + Gráfico + Sinais automáticos")

cripto = st.text_input("Digite a cripto (ex: bitcoin, ethereum, solana, pepe):", value="bitcoin").lower().strip()

def get_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        r = requests.get(url, timeout=10).json()
        price = r['market_data']['current_price']['usd']
        ch24 = r['market_data']['price_change_percentage_24h']
        ch7 = r['market_data']['price_change_percentage_7d']
        mcap = r['market_data']['market_cap']['usd']
        vol = r['market_data']['total_volume']['usd']
        desc = r['description']['en'].split('.')[0] + "."
        url2 = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
        r2 = requests.get(url2, timeout=10).json()
        prices = pd.DataFrame(r2['prices'], columns=['timestamp','price'])
        prices['date'] = pd.to_datetime(prices['timestamp'], unit='ms')
        return price, ch24, ch7, mcap, vol, desc, prices
    except:
        return None

data = get_data(cripto)
if not data:
    st.error(f"Cripto '{cripto}' não encontrada. Tenta: bitcoin, ethereum, solana, dogecoin, pepe")
    st.stop()

price, ch24, ch7, mcap, vol, desc, hist = data
st.markdown(f"## ${price:,.2f}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("24h", f"{ch24:.2f}%", f"{ch24:.2f}%")
c2.metric("7 dias", f"{ch7:.2f}%", f"{ch7:.2f}%")
c3.metric("Market Cap", f"${mcap/1e9:.2f}B")
c4.metric("Volume", f"${vol/1e9:.2f}B")

st.subheader("📈 Gráfico últimos 7 dias")
st.line_chart(hist.set_index('date')['price'], height=300)

st.subheader("🤖 Análise IA Alpha")
media7 = hist['price'].mean()
ultimo = hist['price'].iloc[-1]
tendencia = "ALTA" if ultimo > hist['price'].iloc[0] else "BAIXA"

if ch24 > 5:
    sinal = "🟢 COMPRA FORTE"
    st.success(f"### {sinal} - Momento de alta com força")
elif ch24 > 1:
    sinal = "🟢 COMPRA"
    st.success(f"### {sinal} - Tendência de alta")
elif ch24 < -5:
    sinal = "🔴 VENDA"
    st.error(f"### {sinal} - Queda forte, aguarde")
elif ch24 < -1:
    sinal = "🟡 CAUTELA"
    st.warning(f"### {sinal} - Correção em andamento")
else:
    sinal = "🟡 NEUTRO"
    st.info(f"### {sinal} - Mercado lateral")

texto_promo = f"🚀 ALPHA ALERT: {cripto.upper()} ${price:.2f} ({ch24:+.2f}% 24h). {sinal}. Tendência {tendencia} 7d. #cripto #alphaIA"
st.divider()
st.subheader("📢 Texto para promoção automática")
st.code(texto_promo)
