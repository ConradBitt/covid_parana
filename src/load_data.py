import datetime


def converte_variaveis_em_datas(dataframe):
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


def tira_variaveis_IBGE(dataframe):
    dataframe = dataframe.drop(['IBGE_RES_PR','IBGE_ATEND_PR'], axis='columns')
    return dataframe


def cria_variavel_caso_confirmado_no_dia(dataframe):
    dataframe['CASO_CONFIRMADO_NO_DIA'] = 1
    return dataframe


def replace_nas_variaveis_obito_status(dataframe):

    dataframe['OBITO'] = dataframe['OBITO'].replace('SIM','Sim')
    dataframe['OBITO'] = dataframe['OBITO'].replace('Não','Nao')

    dataframe['OBITO'] = dataframe['OBITO'].replace('Sim',1)
    dataframe['OBITO'] = dataframe['OBITO'].replace('Nao',0)

    dataframe['STATUS'] = dataframe['STATUS'].replace('Recuperado','recuperado')
    dataframe['STATUS'] = dataframe['STATUS'].replace('recuperado', 1)
    dataframe['STATUS'] = dataframe['STATUS'].replace('nan', 0)

    return dataframe
    

def pre_processamento(dataframe):
    dataframe = converte_variaveis_em_datas(dataframe)
    dataframe = tira_variaveis_IBGE(dataframe)
    dataframe = cria_variavel_caso_confirmado_no_dia(dataframe)
    dataframe = replace_nas_variaveis_obito_status(dataframe)
    dataframe = dataframe.set_index('DATA_CONFIRMACAO_DIVULGACAO')
    dataframe = dataframe.sort_index()
    return dataframe

def baixa_base_de_dados_casos_gerais(ano,mes,dia):
    """
    Esta função baixa a base de dados disponível no ano, mes e dia.
    retorna um dataframe do pandas com os dados disponpiveis.
    """
    data = datetime.date(ano, mes, dia)
    ano = str(data.year)

    if mes != 10 and mes != 11 and mes != 12:
        mes = '0'+str(data.month)
    else:
        mes = str(data.month)

    if dia in [1,2,3,4,6,7,8,9]:
        dia = '0'+str(data.day)

    ano_mes = ano+'-'+mes

    if ano == '2020':
        arquivo = f'INFORME_EPIDEMIOLOGICO_{dia}_{mes}_GERAL.csv'
    elif ano == '2021':
        arquivo = f'informe_epidemiologico_{dia}_{mes}_{ano}_geral.csv'
    # Podem acontecer as seguintes variações no site do estado:
    # informe_epidemiologico_{dia}_{mes}_{ano}_geral.csv
    # informe_epidemiologico_{dia}_{mes}_geral.csv
    # INFORME_EPIDEMIOLOGICO_{dia}_{mes}_GERAL.csv



    dominio = 'https://www.saude.pr.gov.br'
    caminho = f'/sites/default/arquivos_restritos/files/documento/{ano_mes}/'
    try:

        url = dominio+caminho+arquivo
        base_de_dados = pd.read_csv(url, sep=';')
        base_de_dados = pre_processamento(base_de_dados)
        
    
    except:
        raise Exception('Não Tem dados disponíveis neste dia.')

    return base_de_dados


if __name__ == '__main__'
