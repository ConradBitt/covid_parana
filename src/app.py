import streamlit as st
import pandas as pd
import plotly.express as px 
from fbprophet import Prophet
from fbprophet.plot import plot_plotly

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


def carrega_dados_gov_pr():
    informes = InformeCovid()

    try:
        informes_covid = informes.carrega_informe(hoje.year, hoje.month, hoje.day - 2)

        if 'DATA_CONFIRMACAO_DIVULGACAO' in informes_covid.columns:
            informes_covid['DATA_CONFIRMACAO_DIVULGACAO'] = pd.to_datetime(informes_covid['DATA_CONFIRMACAO_DIVULGACAO'])
            informes_covid = informes_covid.set_index('DATA_CONFIRMACAO_DIVULGACAO')

        return informes_covid
    except:
        return carrega_medias_moveis_cidades()
        
    

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
    fig.layout.title.text = f'Evolução dos casos por dia em {cidade.title()}'
    fig.layout.xaxis.title.text = 'Data de confirmação'
    fig.layout.yaxis.title.text = 'Quantidade de casos'

    #fig.update_layout(
    #    margin = dict(l=20, r=20,t=30,b=10)
    #)

    return fig



def executa_prophet(dataframe, cidade):
    dataframe = dataframe.query(f'MUN_ATENDIMENTO == "{cidade.upper()}"')
    dataframe = dataframe[['DATA_CONFIRMACAO_DIVULGACAO', 'CASO_CONFIRMADO_NO_DIA']]
    
    modelo = Prophet()
    modelo.add_seasonality(name='monthly', period=11, fourier_order=6)
    

    dataframe.columns = ['ds','y']
    modelo_treinado = modelo.fit(dataframe)

    futuro = modelo_treinado.make_future_dataframe(5, freq='M')
    resultado_prophet = modelo_treinado.predict(futuro)

    fig, ax = plt.subplots()
    modelo_treinado.plot(
        resultado_prophet[['ds','yhat','yhat_lower','yhat_upper']],
        ax = ax
    )
    ax.figure.set_size_inches(10,6)
    ax.set_ylabel('Quantidade de casos', fontsize= 18)
    ax.set_xlabel('Data de Confirmação', fontsize = 18)
    ax.legend(['Casos anteriores','Curva ajustada','Intervalo Confiança'])
    ax.set_title(f'Estimativa de casos para {cidade.title()}', fontsize=20, pad = 20)

    return fig


def executa_pca(dataframe, cidade):
    dataframe = dataframe.query(f'MUN_ATENDIMENTO == "{cidade.upper()}"')
    dataframe = dataframe[['DATA_CONFIRMACAO_DIVULGACAO', 'CASO_CONFIRMADO_NO_DIA']]
    
    modelo = Prophet()
    modelo.add_seasonality(name='monthly', period=11, fourier_order=6)
    

    dataframe.columns = ['ds','y']
    modelo_treinado = modelo.fit(dataframe)

    futuro = modelo_treinado.make_future_dataframe(5, freq='M')
    resultado_prophet = modelo_treinado.predict(futuro)
    fig, ax = plt.subplots()
    fig = modelo_treinado.plot_components(
        resultado_prophet
    )

    return fig


def main():
    st.title('Covid no Estado do Paraná e região')    
    apresentacao()

    dados_covid = carrega_dados_gov_pr()
    cidades = cidades_do_parana(dados_covid)
    opcao_cidade = st.sidebar.selectbox('Selecione uma cidade', cidades)
    figura_cidade = exibe_evolucao_casos(dados_covid, opcao_cidade)
    st.plotly_chart(figura_cidade)
    fonte_informações()

    
    opcao_estimativas = st.sidebar.selectbox('Deseja realizar estimativas de casos?', ['Não','Sim'])
    if opcao_estimativas == 'Sim':
        st.title('Estimando Número de casos - (ARIMA)')
        st.text("""
        Esta etapa pode demorar alguns segundos. A depender da quantidade de dados disponíveis em cada cidade o modelo ARIMA vai tentar estimar a possível quantidade de casos para os próximos 6 meses.
        """)
        figura_prophet = executa_prophet(dados_covid, opcao_cidade)
        st.pyplot(figura_prophet)

        st.markdown("""
        #### Comentário sobre estimador ARIMA
        > Note que alguns casos podem pode estar fora do intervalor
        de confiança, isto acontece não só porque a quantidade de dados
        disponível pode ser pequena, como também pode ocorrer devido
        a erros de estimativas de sasonalidade, tendência e ruido.
        """)

        st.title('Análise de Componente Principal')
        st.text("""
        As componentes principais indicam não só a tendência do numero 
        de casos da cidade, mas também como esta se comportanto a semana 
        e o mês. O intervalo de tempo para análise da tendência é de 14 dias.
        """)
        figura_pca = executa_pca(dados_covid, opcao_cidade)
        
        st.pyplot(figura_pca)
        st.markdown("""
        #### Comentário sobre as componentes principais
        > Os graficos acima tentam decompor a série temporam em suas componentes
        principais. Indica a tendência, sasonalidade semanal e a sasonalidade anual.
        A tendiência indica a basicamente a taxa de variação dos número de casos confirmados.
        Já a sasonalidade semanal e mensal tentam captar quais os momentos de queda e aumento
        no número de casos.
        """)





if __name__ == '__main__':
    main()
    


