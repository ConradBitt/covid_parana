import streamlit as st

from load_data import baixa_base_de_dados_casos_gerais
import datetime

hoje = datetime.date.today()

st.title('Covid no Estado do Paraná e região')

@st.cache
baixa_base_de_dados_casos_gerais(hoje.ano, hoje.month, hoje.day - 1)


