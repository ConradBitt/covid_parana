import streamlit as st

from load_data import baixa_base_de_dados_casos_gerais
import datetime


st.title('Covid no Estado do Paraná e região')


def main():
    # Baixa base de dados do Governo do Paraná
    hoje = datetime.date.today()
    baixa_base_de_dados_casos_gerais(hoje.year, hoje.month, hoje.day - 1)



if __name__ == '__main__':
    main()

