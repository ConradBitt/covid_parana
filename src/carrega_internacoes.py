from unidecode import unidecode
import pandas as pd
import enderecos

class CarregaInternacoes():
    def __init__(self):
        pass


    def __pre_processamento_dados_internacoes(self,dataframe):
        municipios = []
        for municipio in dataframe['Município']:
            municipios.append(unidecode(municipio[7:]).upper())

        dataframe['Município'] = municipios
        dataframe.drop('Total',axis='columns')
        dataframe = dataframe.T.iloc[:-1]

        #  Modificar esta linha, pois a cada mês de internação
        # deve-se adicionar um elemento à tupla
        index = (
            'MUN_ATENDIMENTO', '2020-03', '2020-04',
            '2020-05', '2020-06', '2020-07',
            '2020-08', '2020-09', '2020-10', 
            '2020-11', '2020-12', '2021-01',
            '2021-02', '2021-03'
            )

        dataframe.index = index
        dataframe = dataframe.T
        dataframe = dataframe.set_index('MUN_ATENDIMENTO')
        dataframe = dataframe.replace('-',0).astype(int)
        dataframe.columns = pd.to_datetime(dataframe.columns)
        return dataframe.T

    def carregar_internacoes(self):
        uri_internacoes = enderecos.uri_internacoes
        internacoes = pd.read_csv(uri_internacoes,sep=';',skiprows = 4,skipfooter=14,thousands=',', engine='python', encoding='iso-8859-1')
        internacoes = self.__pre_processamento_dados_internacoes(internacoes)

        return internacoes