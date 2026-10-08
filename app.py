import streamlit as st
import requests

st.set_page_config(
    page_title="Alpha AI Crypto Analyzer",
    page_icon="₿",
    layout="centered"
)

st.title("₿ Alpha AI Crypto Analyzer")
st.write("Análise rápida do mercado de criptomoedas.")

coin = st.text_input(
    "Digite o ID da criptomoeda",
    value="bitcoin",
    placeholder="Ex.: bitcoin, ethereum, solana"
).lower().strip()

if st.button("🔎 Analisar"):
    if not coin:
        st.warning("Digite uma criptomoeda.")
        st.stop()

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "ids": coin,
        "price_change_percentage": "24h"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            st.error("Não foi possível obter os dados.")
            st.stop()

        data = response.json()

        if not data:
            st.error("Criptomoeda não encontrada.")
            st.stop()

        crypto = data[0]

        price = crypto.get("current_price", 0)
        change = crypto.get("price_change_percentage_24h", 0)
        market_cap = crypto.get("market_cap", 0)
        volume = crypto.get("total_volume", 0)

        st.subheader(crypto["name"])

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Preço",
                f"${price:,.4f}"
            )

        with col2:
            st.metric(
                "24h",
                f"{change:.2f}%"
            )

        st.write(f"**Market Cap:** ${market_cap:,.0f}")
        st.write(f"**Volume 24h:** ${volume:,.0f}")

        st.divider()

        st.subheader("📊 Análise Alpha")

        if change >= 5:
            trend = "🟢 Forte movimento positivo"
        elif change > 0:
            trend = "🟢 Movimento positivo"
        elif change <= -5:
            trend = "🔴 Forte movimento negativo"
        else:
            trend = "🟡 Movimento negativo"

        st.write(f"**Tendência de 24h:** {trend}")

        if volume > 0 and market_cap > 0:
            volume_ratio = volume / market_cap

            if volume_ratio >= 0.20:
                activity = "🔥 Alta atividade de negociação"
            elif volume_ratio >= 0.05:
                activity = "🟡 Atividade moderada"
            else:
                activity = "⚪ Atividade relativamente baixa"

            st.write(f"**Atividade:** {activity}")

        st.divider()

        st.caption(
            "Alpha AI Crypto Analyzer — ferramenta educacional. "
            "Os dados podem apresentar atrasos e não constituem recomendação financeira."
        )

    except requests.RequestException:
        st.error("Erro de conexão com a API.")
