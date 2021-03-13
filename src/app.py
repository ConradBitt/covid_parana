import streamlit as st
import pandas as pd
import plotly.express as px 
import datetime
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from matplotlib import pyplot as plt

from informe_covid import InformeCovid
from carrega_internacoes import CarregaInternacoes
import enderecos




def apresentacao():
    st.markdown('''
        Este trabalho tem como objetivo fornecer um panorama sobre a
        situação sanitária com respeito ao número de casos de COVID-19 em
        cada cidade do estado do Paraná. As informações são
        coletadas da secretaria de saúde do estado e são atualizadas a cada 
        quatro dias.

        Você pode consultar a situação de cada cidade na barra de 
        seleção ao lado. Algumas cidades não pertencem ao estado pois
        é possível que o paciente tenha feito um teste fora das regionais 
        de saúde do Paraná e só depois tenha recebido o resultado.
    ''')


def fonte_informações():
    st.markdown('Fonte de informação:')
    st.markdown(' 1. [Secretaria de Saúde Governo do Estado do Paraná](https://www.saude.pr.gov.br/Pagina/Coronavirus-COVID-19)')
    st.markdown(' 2. [Ministério da Saúde - Sistema de informações hospitalares do SUS (SIH/SUS)](https://datasus.saude.gov.br/acesso-a-informacao/producao-hospitalar-sih-sus/)')


def contato():
    st.sidebar.markdown(
        '*Este projeto ainda esta em desenvolvimento, ficaria grato com a contribuição*')
    st.sidebar.markdown('Repositorio: [COVID-19 No PR e Região](https://github.com/ConradBitt/covid_parana)')
    st.sidebar.markdown('Feito por: [Conrado Bittencourt](https://github.com/ConradBitt)')

@st.cache
def carrega_medias_moveis_cidades():
    medias_moveis = pd.read_csv(enderecos.uri_medias_moveis, sep=';', engine='python')
    if 'DATA_CONFIRMACAO_DIVULGACAO' in medias_moveis.columns:
        medias_moveis['DATA_CONFIRMACAO_DIVULGACAO'] = pd.to_datetime(medias_moveis['DATA_CONFIRMACAO_DIVULGACAO'])
        #medias_moveis = medias_moveis.set_index('DATA_CONFIRMACAO_DIVULGACAO')

    return medias_moveis


@st.cache
def carrega_dados_gov_pr(data):
    
    informes = InformeCovid()
    try:
        informes_covid = informes.carrega_informe(data)
        if 'DATA_DIAGNOSTICO' in informes_covid.columns:
            
            informes_covid['DATA_CONFIRMACAO_DIVULGACAO'] = pd.to_datetime(informes_covid['DATA_DIAGNOSTICO'])
            informes_covid = informes_covid.set_index('DATA_CONFIRMACAO_DIVULGACAO')

        return informes_covid
    except:
        raise Exception('Não foi possível carregar dados')
        pass
        #print('Não foi possível carregar os dados da secretaria de saúde...')
        #return carrega_medias_moveis_cidades()
        
@st.cache
def carrega_internacoes_parana():
    carregador = CarregaInternacoes()
    internacoes = carregador.carregar_internacoes()
    return internacoes


def cidades_do_parana(dataframe):
    return dataframe['MUN_ATENDIMENTO'].unique()


def exibe_evolucao_casos(dataframe, cidade):
    dataframe = dataframe.query(f'MUN_ATENDIMENTO == "{cidade.upper()}"')
    dataframe = dataframe.groupby(['DATA_CONFIRMACAO_DIVULGACAO'], as_index=True).sum().reset_index()

    datas = dataframe['DATA_CONFIRMACAO_DIVULGACAO']
    dataframe = dataframe.rolling(14).mean().iloc[14:,:]
    dataframe['DATA_CONFIRMACAO_DIVULGACAO'] = datas.iloc[14:]


    dataframe = dataframe[['DATA_CONFIRMACAO_DIVULGACAO', 'CASO_CONFIRMADO']]

    fig = px.line(
        dataframe,
        x = 'DATA_CONFIRMACAO_DIVULGACAO',
        y = 'CASO_CONFIRMADO',
        color_discrete_sequence = px.colors.sequential.Cividis
        )

    fig.update_layout(
        title = f'Evolução dos casos por dia em {cidade.title()}',
        xaxis_title = 'Data de confirmação',
        yaxis_title = 'Quantidade de casos'
    )

    return fig


def exibe_internacoes_cidade(dataframe, cidade):
    cidade = cidade.upper()
    internacoes = dataframe[cidade]
    internacoes.rename_axis('Data', inplace=True)

    fig = px.bar(dataframe[cidade], x=internacoes.index, y = f'{cidade}',
     color=f'{cidade}', height=400, labels={f'{cidade}': 'Internados'})
    fig.layout.title.text = f'Internações por COVID-19 - {cidade}'
    fig.layout.xaxis.title.text = 'Mês de internação'
    fig.layout.yaxis.title.text = ''
    fig.update_coloraxes(
        colorbar=dict(title='Internações'),
        colorbar_title_font_size=22,
        colorbar_title_side='top')

    return fig


def executa_prophet(dataframe, cidade):
    dataframe = dataframe.query(f'MUN_ATENDIMENTO == "{cidade.upper()}"')
    dataframe = dataframe.groupby(['DATA_CONFIRMACAO_DIVULGACAO'], as_index=True).sum().reset_index()
    
    indice = dataframe['DATA_CONFIRMACAO_DIVULGACAO']
    dataframe = dataframe.rolling(14).mean()
    dataframe['DATA_CONFIRMACAO_DIVULGACAO'] = indice
    
    dataframe = dataframe[['DATA_CONFIRMACAO_DIVULGACAO', 'CASO_CONFIRMADO']]
    
    modelo = Prophet()
    modelo.add_seasonality(name='monthly', period=11, fourier_order=6)
    

    dataframe.columns = ['ds','y']
    modelo_treinado = modelo.fit(dataframe)

    futuro = modelo_treinado.make_future_dataframe(14, freq='D')
    resultado_prophet = modelo_treinado.predict(futuro)

    fig, ax = plt.subplots()
    modelo_treinado.plot(
        resultado_prophet[['ds','yhat','yhat_lower','yhat_upper']],
        ax = ax
    )
    ax.figure.set_size_inches(10,6)
    ax.set_ylabel('Quantidade de casos', fontsize= 18)
    ax.set_xlabel('Data de Confirmação', fontsize = 18)
    ax.legend(['Casos anteriores','Curva de casos','Intervalo Confiança'])
    ax.set_title(f'Estimativa de casos para {cidade.title()}', fontsize=20, pad = 20)

    return fig


def executa_pca(dataframe, cidade):
    dataframe = dataframe.query(f'MUN_ATENDIMENTO == "{cidade.upper()}"')
    dataframe = dataframe.groupby(['DATA_CONFIRMACAO_DIVULGACAO'], as_index=True).sum().reset_index()

    indice = dataframe['DATA_CONFIRMACAO_DIVULGACAO']
    dataframe = dataframe.rolling(14).mean()
    dataframe['DATA_CONFIRMACAO_DIVULGACAO'] = indice
    

    dataframe = dataframe[['DATA_CONFIRMACAO_DIVULGACAO', 'CASO_CONFIRMADO']]
    
    modelo = Prophet()
    modelo.add_seasonality(name='monthly', period=11, fourier_order=6)
    

    dataframe.columns = ['ds','y']
    modelo_treinado = modelo.fit(dataframe)

    futuro = modelo_treinado.make_future_dataframe(14, freq='D')
    resultado_prophet = modelo_treinado.predict(futuro)
    fig, ax = plt.subplots()
    fig = modelo_treinado.plot_components(
        resultado_prophet
    )

    return fig


def executa_estimativas(dados_covid, opcao_cidade):
    st.title('Estimando Número de casos - (Prophet)')
    st.text("""
    A depender da quantidade de dados disponíveis em cada cidade
    o modelo vai tentar estimar a possível quantidade de casos
    para os próximos 6 meses. Vale ressaltar que a disponibilidade
    de amostras pode afetar as estimativas.
    """)
    figura_prophet = executa_prophet(dados_covid, opcao_cidade)
    st.pyplot(figura_prophet)

    st.markdown("""
    #### Comentário sobre estimador Prophet
    > Note que alguns casos podem estar fora do intervalo de
    confiança, isto acontece não só porque a quantidade de dados
    disponível pode ser pequena, como também pode ocorrer devido
    a erros de estimativas de sasonalidade, tendência e ruido.
    """)

    st.title('Análise de Componente Principal')
    st.text("""
    As componentes principais indicam não só a tendência do numero 
    de casos da cidade, mas também como esta se comportanto as semanas 
    e os mêses. O intervalo para a análise da componente principal 
    estima os próximos 14 dias.
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


def main():
    # Definições 
    hoje = datetime.date.today()
   
    st.title('Covid no Estado do Paraná e região')    
    st.text(f'{hoje.day}/{hoje.month}/{hoje.year}')
    
    apresentacao()
    contato()

    dados_covid = carrega_dados_gov_pr(hoje)
    internacoes = carrega_internacoes_parana()
    cidades = cidades_do_parana(dados_covid)


    opcao_cidade = st.sidebar.selectbox('Selecione uma cidade', cidades)
    
    figura_cidade = exibe_evolucao_casos(dados_covid, opcao_cidade)
    st.plotly_chart(figura_cidade)

    if opcao_cidade in internacoes.columns:
        st.markdown("""
        # Procedimento hospitalar

        Estas informações são retiradas do datasus e descrevem não só a 
        quantidade de tratamentos por infecção pelo coronavirus (COVID-19) mas
        também considera a diária permanência maior dos pacientes. 
        """)
        figura_internacoes = exibe_internacoes_cidade(internacoes, opcao_cidade)
        st.plotly_chart(figura_internacoes,use_container_width=True)

        st.markdown("""
        Dados referêntes aos últimos 6 meses e sujeitos a atualização        
        """)
    else:
        pass

    
    opcao_estimativas = st.sidebar.selectbox('Deseja realizar estimativas de casos?', ['Não','Sim'])
    if opcao_estimativas == 'Sim':
        executa_estimativas(dados_covid, opcao_cidade)
        st.markdown('## Comentários finais')
        st.text("""
        É importante salientar que são estimativas, a tendência
        sasonalidade e ruidos podem não estar tão calibrados, portanto
        não leve essas estimativas como verdade absoluta, por mais que os
        estimadores sejam baseados em modelos matemáticos ainda são
        estimativas.
        """)





if __name__ == '__main__':
    main()
    fonte_informações()



