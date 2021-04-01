import datetime
import pandas as pd

class InformeCovid():
    """
    Esta classe tem como objetivo carregar os informes
    da covid do estado do paraná. Ao utilizar a função
    carrega_informe() o resultado será um dataframe 
    com o informe do dia, mes e ano.

    Use o método carrega_informe(): para carregar todo o
        informe do paraná.
    
    OU

    Use o método carrega_informe_mm(): para carregar as 
    médias móveis da cidade do paraná. É possível modificar
    o parâmetro move_average para mudar a janela.
    """
    def __init__(self):
        pass

    def carrega_informe(self, data):
        ano = data.year
        mes = data.month
        dia = data.day

        self._data_informe = datetime.date(ano, mes, dia)
        self.dia, self.mes, self.ano = self.__ajusta_data(self._data_informe)
        self.__uri = self.__ajusta_uri(self.dia, self.mes, self.ano)

        try:
            dados_informe_covid = pd.read_csv(self.__uri, sep=';')
            print('lido com sucesso...')
        except:
            raise Exception(f'Não Tem dados disponíveis neste dia.\n{self.__uri}')

        try:
            dados_informe_covid = self.__pre_processamento(dados_informe_covid)
            print('pré processamento concluido...')
        except:
            raise Exception('Não ocorreu o pré processamento...')
        
        print('dados carregados com sucesso...')
        return dados_informe_covid


    def carrega_informe_mm(self, data, janela = 14):
        dados = self.carrega_informe(data)
        dados = self.__pre_processamento(dados)
        dados_agrupados = dados.groupby(['MUN_ATENDIMENTO','DATA_CONFIRMACAO_DIVULGACAO'])

        self.informe_mm = dados_agrupados[
            ['CASO_CONFIRMADO',
            'OBITO']
            ].sum().rolling(janela).mean()[janela:]
        
        return self.informe_mm



    def __ajusta_uri(self, dia, mes, ano):
        dia = str(dia)
        mes = str(mes)
        ano = str(ano)

        if dia in ['1','2','3','4','6','7','8','9']:
            dia = '0' + dia

        if ano == '2020':
            arquivo = f'INFORME_EPIDEMIOLOGICO_{dia}_{mes}_GERAL.csv'
        elif ano == '2021':
            arquivo = f'informe_epidemiologico_{dia}_{mes}_{ano}_geral.csv' 

        ano_mes = ano + '-' + mes
        dominio = 'https://www.saude.pr.gov.br'
        caminho = f'/sites/default/arquivos_restritos/files/documento/{ano_mes}/'   
        
        uri = dominio + caminho + arquivo 

        return uri

    
    def __ajusta_data(self, data_informe):
        ano = str(data_informe.year)
        mes = str(data_informe.month)
        dia = str(data_informe.day)
        
        if mes != 10 and mes != 11 and mes != 12:
            mes = '0'+str(data_informe.month)
        else:
            mes = str(data_informe.month)

        if dia in [1,2,3,4,6,7,8,9]:
            dia = '0'+str(data_informe.day)
        
        return dia, mes, ano


    def __pre_processamento(self, dataframe):
        """
        Esta função faz o pré processamento dos dados
        - converte_variaveis_em_datas
        - tira_variaveis_IBGE
        - cria_variavel_caso_confirmado_no_dia(dataframe)
        - replace_nas_variaveis_obito_status(dataframe)
        - usa 'DATA_CONFIRMACAO_DIVULGACAO' como indice
        - ordena pelo índice

        retorna o dataframe.
        """

        dataframe = self.__converte_variaveis_em_datas(dataframe)
        dataframe = self.__tira_variaveis_IBGE(dataframe)
        dataframe =  self.__cria_variavel_caso_confirmado(dataframe)
        dataframe = self.__replace_nas_variaveis_obito_status(dataframe)
        dataframe = dataframe.set_index('DATA_CONFIRMACAO_DIVULGACAO')
        dataframe = dataframe.sort_index()

        return dataframe
        

    def __converte_variaveis_em_datas(self, dataframe):
        for variavel in dataframe.columns:
            if 'DATA' in variavel:
                try:
                    dataframe[variavel] = pd.to_datetime(dataframe[variavel], format='%d/%m/%Y')
                
                except:
                    print(f'Variável "{variavel}" contém um erro e conversão/formatação')
                    pass
            else:
                pass 
        return dataframe


    def __tira_variaveis_IBGE(self, dataframe):
        dataframe = dataframe.drop(['IBGE_RES_PR','IBGE_ATEND_PR'], axis='columns')
        return dataframe


    def __cria_variavel_caso_confirmado(self, dataframe):
        dataframe['CASO_CONFIRMADO'] = 1
        return dataframe


    def __replace_nas_variaveis_obito_status(self, dataframe):

        if 'OBITO' in dataframe.columns:
            dataframe['OBITO'] = dataframe['OBITO'].replace('SIM','Sim')
            dataframe['OBITO'] = dataframe['OBITO'].replace('Não','Nao')
        
            dataframe['OBITO'] = dataframe['OBITO'].replace('Sim',1)
            dataframe['OBITO'] = dataframe['OBITO'].replace('Nao',0)
        else:
            pass
        if 'STATUS' in dataframe.columns:
            dataframe['STATUS'] = dataframe['STATUS'].replace('Recuperado','recuperado')
            dataframe['STATUS'] = dataframe['STATUS'].replace('recuperado', 1)
            dataframe['STATUS'] = dataframe['STATUS'].replace('nan', 0)
        else:
            pass
        return dataframe


    def atualiza_dados_diarios(hoje):
        informe_covid = self.carrega_informe(hoje.year, hoje.month, hoje.day - 1)

        move_average_15_por_cidade = informe_covid.groupby(['MUN_ATENDIMENTO','DATA_CONFIRMACAO_DIVULGACAO'])[['CASO_CONFIRMADO_NO_DIA','OBITO']].sum().rolling(14).mean()[14:].round()
        move_average_15_por_cidade.to_csv('../dados_recentes/cidades_mm15.csv', sep=';')

        casos_por_cidade = informe_covid.groupby(['MUN_ATENDIMENTO','DATA_CONFIRMACAO_DIVULGACAO'])[['CASO_CONFIRMADO_NO_DIA','OBITO']].sum().round()
        casos_por_cidade.to_csv('../dados_recentes/casos_por_cidade.csv', sep=';')    






        