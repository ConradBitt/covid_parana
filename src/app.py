import streamlit as st

import load_data
import datetime

hoje = datetime.date.today()

st.title('Covid no Estado do Paraná e região')

@st.cache
load_data.baixa_base_de_dados_casos_gerais(hoje.ano, hoje.month, hoje.day - 1)


