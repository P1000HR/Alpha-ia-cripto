import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Alpha V6 AUTO", page_icon="🤖", layout="wide")

st.markdown("<h1>🤖 ALPHA V6 - AUTO POST GOD</h1>", unsafe_allow_html=True)
st.caption("Watchlist + Auto Post 9h + Modo Robô | VERSÃO FINAL")

SYMBOL_MAP={"BTC":"bitcoin","ETH":"ethereum","SOL":"solana","DOGE":"dogecoin","SHIB":"shiba-inu","PEPE":"pepe","BONK":"bonk","WIF":"dogwifcoin"}

@st.cache_data(ttl=300)
def get_price(cid):
    try:
        r=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}", timeout=10).json()['market_data']
        return r['current_price']['usd'], r['price_change_percentage_24h'], r['market_cap']['usd']
    except: return None

@st.cache_data(ttl=600)
def get_markets():
    url="https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=10&order=market_cap_desc"
    try: return requests.get(url, timeout=10).json()
    except: return []

# MODO AUTO PARA O ROBO (quando acessa?auto=1)
params = st.query_params
is_auto = params.get("auto") == "1"

if is_auto:
    # Gera texto puro para o robô do GitHub Actions ler
    markets = get_markets()
    txt = f"🤖 ALPHA AUTO {datetime.now().strftime('%d/%m %H:%M')}:\n"
    for m in markets[:5]:
        txt+=f"{m['symbol'].upper()} ${m['current_price']} {m.get('price_change_percentage_24h',0):+.2f}%\n"
    txt+="#AlphaV6 #Cripto"
    st.code(txt)
    st.write("AUTO_MODE_TEXT:" + txt.replace("\n"," | "))
    st.stop()

# MODO NORMAL
st.sidebar.header("⭐ Minha Watchlist (5 moedas)")
watchlist_default=["bitcoin","ethereum","solana","pepe","dogecoin"]
watchlist=st.sidebar.multiselect("Escolha 5:", [m['id'] for m in get_markets()] + list(SYMBOL_MAP.values()), default=watchlist_default, max_selections=5)

if st.sidebar.button("💾 Salvar Watchlist"):
    st.sidebar.success("Salva! (Na V6 fica na memória da sessão)")

# DASHBOARD
if watchlist:
    cols=st.columns(len(watchlist))
    total_val=0
    promos=[]
    for i, cid in enumerate(watchlist):
        data=get_price(cid)
        if data:
            price,ch24,mcap=data
            promos.append(f"{cid.upper()} ${price} {ch24:+.1f}%")
            with cols[i]:
                st.metric(cid.upper(), f"${price:,.4f}" if price<1 else f"${price:,.2f}", f"{ch24:.2f}%")
                total_val+=price

    st.divider()
    # GRAFICO COMPARADO
    st.subheader("📈 Comparativo Watchlist 7 dias (normalizado %)")
    try:
        chart_data=pd.DataFrame()
        for cid in watchlist[:3]:
            hist=requests.get(f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart?vs_currency=usd&days=7", timeout=10).json()['prices']
            df=pd.DataFrame(hist, columns=['t','price'])
            df['date']=pd.to_datetime(df['t'], unit='ms')
            df=df.set_index('date')
            df[f'{cid} %']=(df['price']/df['price'].iloc[0]-1)*100
            chart_data=pd.concat([chart_data, df[[f'{cid} %']]], axis=1)
        st.line_chart(chart_data, height=350)
    except:
        st.write("Gráfico carregando...")

    # TEXTO AUTO
    st.subheader("📢 Texto Auto 9h")
    promo_text=f"🚀 ALPHA V6 AUTO {datetime.now().strftime('%d/%m')}: {' | '.join(promos[:4])} | Watchlist GOD | #Cripto #AlphaAuto"
    st.code(promo_text)
    c1,c2=st.columns(2)
    c1.link_button("🐦 Postar Agora no X", f"https://twitter.com/intent/tweet?text={promo_text[:250]}")
    if c2.button("🤖 Testar Modo Robô"):
        st.switch_page(f"?auto=1")

st.divider()
st.markdown("""
### 🤖 COMO ATIVAR O POST AUTOMÁTICO 9H DA MANHÃ (PASSO FINAL)

**Você vai criar um robô no GitHub que posta sozinho:**

1. No seu GitHub `Alpha-ia-cripto`, clica em **Add file > Create new file**
2. No nome do arquivo, digita EXATAMENTE: `.github/workflows/daily.yml`
3. Cola esse código dentro:
```yaml
name: Alpha Auto Post 9h
on:
  schedule:
    - cron: '0 12 * * *' # 9h Brasil = 12h UTC
  workflow_dispatch:

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - name: Get Alpha Data
        run: |
          curl -s "https://SEU-LINK-AQUI.streamlit.app/?auto=1" > auto.txt
          cat auto.txt
      - name: Telegram Post (opcional)
        if: false
        run: |
          curl -s "https://api.telegram.org/bot${{ secrets.TELEGRAM_TOKEN }}/sendMessage?chat_id=${{ secrets.TELEGRAM_CHAT }}&text=ALPHA AUTO POST"
