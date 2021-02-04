import pandas as pd
import numpy as np
import re
from pandas_profiling import ProfileReport

#DEFINR DATASET PARA PREPROCESSAMENTO
data_set = 'data_ORIGINAL.csv'

#CRIAR DATAFRAME PANDAS
df_bot = pd.read_csv(data_set, sep=',',error_bad_lines=False,engine='python',encoding='utf-8',na_filter=True)
df = df_bot

#RESET INDEX
#df_bot.set_index('i')
#df.reset_index(drop=True)
#df.to_csv(data_set, sep=',')
#df.drop(['i'], axis='columns', inplace=True)
#df.to_csv(data_set, index=False)


#PROFILE JUPYTER NOTEBOOK VSCODE
def profile(a):
    profile = ProfileReport(a, title='Análise e Exploração dos Dados Processados', explorative=True)
    profile.to_file(output_file="Analise_Dados_Processados3.html")
    #return ProfileReport(a, title='Pandas Profiling Report', explorative=True)
    

#ORDENAR ALFABETICAMENTE
def ordenar(tabela_pandas, dados):
    tabela_pandas.sort_values(by=['FONTE','TEMA','ASSUNTO'], inplace=True, ascending=True)
    tabela_pandas.to_csv(dados, sep=',', index=False)
    print(' >> Linhas ordenadas')


#VERIFICAR QUANTIDADE DE LINHAS COM VALORES NULOS
def verificar_nulas(tabela_pandas):
    print(tabela_pandas.isnull().sum())
    print(' >> Verificado linhas com VALORES NULOS')
    
    
#REMOVER LINHAS COM VALORES NULOS 
def apagar_nulas(tabela_pandas,dados):
    b = tabela_pandas.dropna()
    b.to_csv(dados, sep=',', index=False)
    print(' >> Linhas SEM DADOS apagadas')


#REMOVER LINHAS EM DUPLICIDADE
def apagar_duplicadas(tabela_pandas,dados):
    b = tabela_pandas.drop_duplicates(subset=['FONTE','TEMA','ASSUNTO'], keep='first')
    b.to_csv(dados, sep=',', index=False)#True para criar index
    #b.to_csv(dados, sep=',', index=True)#True para criar index
    print(' >> Linhas DUPLICADAS apagadas')


#REMOVER LINHA COM STRING
def apagar_conteudo(tabela_pandas,dados,busca):
    textlikes = tabela_pandas.select_dtypes(include=[object, "string"])
    a = tabela_pandas[textlikes.apply(lambda column: column.str.contains(busca, regex=True, case=False, na=False)).any(axis=1)]
    print(a)
    tabela_pandas.index = tabela_pandas['i']
    c = a['i'].values.tolist()
    print(len(c))
    a = tabela_pandas.drop(c, inplace=False)
    a.info()
    a.to_csv(dados,index=False)


#REMOVER LINHAS SEM LINK NA COLUNA 
def apagar_sem_link(tabela_pandas,dados):
    textlikes = tabela_pandas.select_dtypes(include=[object, "string"])
    a = tabela_pandas[textlikes.apply(lambda column: column.str.contains("http", regex=True, case=False, na=False)).any(axis=1)]
    #Apagar coluna
    a.drop(['index'], axis='columns', inplace=True)
    a.to_csv(dados, index=False)
    a.info()


#REMOVER LINHAS COM LINKS IGUAIS
def links_iguais(tabela_pandas,dados):
    b = tabela_pandas[tabela_pandas.duplicated(subset=['Link'], keep='first')]
    b.to_csv(dados, sep=',', index=False)
    print('Links iguais na coluna removidos com sucesso...')


#REMOVER ESPAÇOS EM BRANCO NO DATAFRAME    
def espacos_branco(tabela_pandas,dados): #REMOVER ESPAÇOS EM BRANCO ENTRE PALAVRAS
    tabela_pandas = tabela_pandas.applymap((lambda x: " ".join(x.split()) if type(x) is str else x ))
    tabela_pandas.to_csv(dados, sep=',', index=False)
    print('Espacos em branco removidos...')
    
    
#ALTERAR TODOS OS TERMOS DENTRO DE DETERMINADA COLUNA    
def alterar_termo(tabela_pandas,dados):
    tabela_pandas = pd.read_csv(dados, sep=',',header=0)
    tabela_pandas["Texto"] = tabela_pandas["Texto"].apply(lambda x: str(x))
    #tabela_pandas = pd.DataFrame({'t'}, dtype='object')
    print(df.columns)
    df_bot.set_index('i')    
    tabela_pandas['Texto'] = tabela_pandas['Texto'].apply(lambda x: x.replace(' .', " "))
    tabela_pandas.to_csv(dados, sep=',', index=False)


#ALTERAR VALORES NULOS   
def alterar_na(tabela_pandas,dados):
    tabela_pandas.fillna(' ', inplace=True)
    tabela_pandas.to_csv(dados, sep=',', index=False)


lista_termos = ['/imprensa','/arquivos-e-imagens','/ato-declaratorio',
'Home','/author/','/educacao-fiscal/','govbr - Acesse sua conta','/licitacoes-e-contratos/','/agenda-tributaria',
'/acoes-e-programas/','/admissao-temporaria/','edital-de-intimacao-','.csv','.ods','-odt','-doc','.epub','-pdf',
'/windows','-zip','-linux','/mercadorias-apreendidas/','-windows','_start:int','/home-old','/institucional/','linux',
'-jar','/mac','/acesso-a-informacao/','More…','/unidades-no-brasil/']
  

#EXECUTAR FUNÇÕES DE PREPROCESSAMENTO

profile(df_bot)
#verificar_nulas(df_bot)
#verificar_nulasordenar(df_bot,data_set)
#apagar_duplicadas(df_bot,data_set)#INDEX FALSE OR TRUE PARA GERAR INDEX
#espacos_branco(df_bot,data_set)
#links_iguais(df_bot,data_set)
#apagar_sem_link(df_bot,data_set)
#for x in lista_termos:
#apagar_conteudo(df_bot,data_set,"{}".format('/unidades-no-brasil/'))
#apagar_nulas(df_bot,data_set)
#alterar_termo(df_bot,data_set)
#alterar_na(df_bot,data_set)



#ROTINAS EXTRAS:

#ALTERAR STRING PARA NAN VALUE
#df['TEXTO'].replace('.', np.NaN, inplace=True)
#df.to_csv('data_PROCESSADO.csv', sep=',', index=False)


#DEFINIR INDEX COLUNA
#df_bot.set_index('i')
#print(df_bot.head())


#REMOVE LINKS IGUAIS
#b = df_bot[df_bot.duplicated('l')]
#b.to_csv("data_tudook.csv", sep=',', index=False)


#JUNTAR COLUNAS
#df['n'] = df["tema"].astype(str) + ' ' + df["link"]
#df.to_csv("data_bruton.csv", sep=',', index=False)


#APAGAR DADOS NULOS POR COLUNA
#df = df.sort_values('n', ascending=True)

#1
#df = df.drop_duplicates(subset=['Link'], keep='first')
#df.to_csv('dataset_ORIGINAL4.csv', sep=',', index=False)

#2
#df = df.drop_duplicates(subset=['tema'], keep='first')
#df.to_csv('data_a.csv', sep=',', index=False)

#Apagar Valores Nulos coluna TEMA
#df.dropna(subset=['Tags'], how = 'all', inplace=True)
#df.to_csv('dataset_processado.csv', sep=',', index=False)

