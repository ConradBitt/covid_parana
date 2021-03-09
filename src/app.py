import streamlit as st
import load_data



# Baixa base de dados do Governo do Paraná
hoje = datetime.date.today()
baixa_base_de_dados_casos_gerais(hoje.year, hoje.month, hoje.day - 1)


def main():
    st.title('Covid no Estado do Paraná e região')




if __name__ == '__main__':
    main()

