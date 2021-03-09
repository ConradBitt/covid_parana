import streamlit as st



st.title('Covid no Estado do Paraná e região')


def main():

    from load_data import baixa_base_de_dados_casos_gerais
    import datetime
    # Baixa base de dados do Governo do Paraná
    hoje = datetime.date.today()
    baixa_base_de_dados_casos_gerais(hoje.year, hoje.month, hoje.day - 1)



if __name__ == '__main__':
    main()

