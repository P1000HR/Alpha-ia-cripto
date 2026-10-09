import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Alpha Cripto IA", layout="wide")
st.title("🚀 Alpha AI Crypto Analyzer")

moeda = st.text_input("Digite a cripto (ex: bitcoin, ethereum, solana):", "bitcoin")

if st.button("Analisar"):
    url = f"https://api.coingecko.com/api/v3/coins/{moeda.lower()}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        preco = data['market_data']['current_price']['usd']
        st.metric("Preço USD", f"${preco}")
        st.write(data['description']['en'][:500])
    else:
        st.error("Moeda não encontrada. Tente bitcoin, ethereum, solana")

# Opcional: requirements.txt precisa ter
# streamlit
# requests
# pandas
