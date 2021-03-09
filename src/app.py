import streamlit as st
from informe_covid import InformeCovid
import datetime


# Definições 
hoje = datetime.date.today()


# demora carregar
#informes = InformeCovid()
#dados_informe = informes.carrega_informe_mm(hoje)


st.dataframe(dados_informe.head())

def apresentacao():
    st.markdown('''
        Este trabalho tem como objetivo dar um panorâma sobre a
        situação sanitária com respeito ao número de casos em
        cada cidade do estado do paraná. As informações são
        coletadas da secretaria de saúde do estado.
    ''')


def main():
    st.title('Covid no Estado do Paraná e região')    
    apresentacao()

if __name__ == '__main__':
    main()

