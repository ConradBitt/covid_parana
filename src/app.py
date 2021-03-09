import streamlit as st
import pandas as pd
import plotly.express as px 
from matplotlib import pyplot as plt


from informe_covid import InformeCovid
from enderecos import uri_medias_moveis

import datetime


# Definições 
hoje = datetime.date.today()


# demora carregar
#informes = InformeCovid()
#dados_informe = informes.carrega_informe_mm(hoje)

def apresentacao():
    st.markdown('''
        Este trabalho tem como objetivo dar um panorama sobre a
        situação sanitária com respeito ao número de casos de COVID-19 em
        cada cidade do estado do Paraná. As informações são
        coletadas da secretaria de saúde do estado e são atualizadas a cada 
        quatro dias.

        Você pode consultar a situação de cada cidade na barra de 
        seleção ao lado. Algumas cidades não pertencem ao estado pois
        é possível que o paciente tenha feito um teste fora das regionais 
        de saúde do Paraná.
    ''')

def fonte_informações():
    st.markdown('Fonte de informação:')
    st.markdown(' 1. [Secretaria de Saúde Governo do Estado do Paraná](https://www.saude.pr.gov.br/Pagina/Coronavirus-COVID-19)')
    st.sidebar.markdown('Feito por [Conrado Bittencourt](https://github.com/ConradBitt)')
    

def carrega_medias_moveis_cidades():
    medias_moveis = pd.read_csv(uri_medias_moveis, sep=';', engine='python')
    if 'DATA_CONFIRMACAO_DIVULGACAO' in medias_moveis.columns:
        medias_moveis['DATA_CONFIRMACAO_DIVULGACAO'] = pd.to_datetime(medias_moveis['DATA_CONFIRMACAO_DIVULGACAO'])
        #medias_moveis = medias_moveis.set_index('DATA_CONFIRMACAO_DIVULGACAO')

    return medias_moveis

def cidades_do_parana(dataframe):
    return dataframe.MUN_ATENDIMENTO.unique()

def exibe_evolucao_casos(dataframe, cidade):
    casos_na_cidade = dataframe.query(f'MUN_ATENDIMENTO == "{cidade.upper()}"')
    fig = px.line(
        casos_na_cidade,
        x = 'DATA_CONFIRMACAO_DIVULGACAO',
        y = 'CASO_CONFIRMADO_NO_DIA',
        color_discrete_sequence = px.colors.sequential.Cividis
        )
    fig.layout.title.text = f'Evolução dos casos em {cidade.title()}'
    fig.layout.xaxis.title.text = 'Data de confirmação'
    fig.layout.yaxis.title.text = 'Quantidade de casos'

    #fig.update_layout(
    #    margin = dict(l=20, r=20,t=30,b=10)
    #)

    return fig


def main():
    st.title('Covid no Estado do Paraná e região')    
    apresentacao()
    
    medias_moveis = carrega_medias_moveis_cidades()

    cidades = cidades_do_parana(medias_moveis)
    
    opcao_cidade = st.sidebar.selectbox('Selecione uma cidade', cidades)

    figura_cidade = exibe_evolucao_casos(medias_moveis, opcao_cidade)

    st.plotly_chart(figura_cidade)


if __name__ == '__main__':
    main()
    fonte_informações()

