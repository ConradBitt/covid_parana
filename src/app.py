import streamlit as st
import pandas as pd
import seaborn as sns
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
        Este trabalho tem como objetivo dar um panorâma sobre a
        situação sanitária com respeito ao número de casos em
        cada cidade do estado do paraná. As informações são
        coletadas da secretaria de saúde do estado.
    ''')

def carrega_medias_moveis_cidades():
    medias_moveis = pd.read_csv(uri_medias_moveis, sep=';', engine='python')
    if 'DATA_CONFIRMACAO_DIVULGACAO' in medias_moveis.columns:
        medias_moveis['DATA_CONFIRMACAO_DIVULGACAO'] = pd.to_datetime(medias_moveis['DATA_CONFIRMACAO_DIVULGACAO'])
        medias_moveis = medias_moveis.set_index('DATA_CONFIRMACAO_DIVULGACAO')

    return medias_moveis

def cidades_do_parana(dataframe):
    return dataframe.MUN_ATENDIMENTO.unique()

def exibe_serie_temporal(dataframe,cidade, titulo):
    sns.set_context('talk')
    sns.set_style('darkgrid')
    
    dataframe = dataframe.query(f'MUN_ATENDIMENTO == "{cidade}"')
    
    fig, ax = plt.subplots()
    
    ax = sns.lineplot(data = dataframe,
     x = 'DATA_CONFIRMACAO_DIVULGACAO',
     y= 'CASO_CONFIRMADO_NO_DIA', 
     label='Média Móvel (15)')
    ax.set_title(f'{titulo} - {cidade}', pad=20)
    ax.set_ylabel('Casos confirmados')
    ax.set_xlabel('Data confirmação')
    ax.figure.set_size_inches(15,10)
    plt.xticks(rotation=45)

    return fig


def main():
    st.title('Covid no Estado do Paraná e região')    
    apresentacao()
    
    medias_moveis = carrega_medias_moveis_cidades()

    cidades = cidades_do_parana(medias_moveis)
    opcao_cidade = st.sidebar.selectbox('Selecione uma cidade', cidades)
    figura_cidade = exibe_serie_temporal(medias_moveis, opcao_cidade, 'Casos confirmados')
    st.pyplot(figura_cidade)

if __name__ == '__main__':
    main()

