import pandas as pd
from mapeamentos import FAIXA_ETARIA_BINS, FAIXA_ETARIA_LABELS, QE_I19_LABELS, QE_I02_LABELS, GENDER_LABELS, REGIONS_LABELS, TP_PR_GER_LABELS, CO_UF_CURSO_LABELS, CO_REGIAO_CURSO_LABELS, CO_CATEGAD_LABELS, CO_MODALIDADE_LABELS, CO_GRUPO_LABELS, CODIGO_UF_PARA_SIGLA
import matplotlib.pyplot as plt

ARQUIVO_INFO_GERAL = "data/raw/enade/microdados2023_arq1.txt"
ARQUIVO_INFO_ESTUDANTES = "data/raw/enade/microdados2023_arq2.txt"
ARQUIVO_INFO_PROVA = "data/raw/enade/microdados2023_arq3.txt"
ARQUIVO_INFO_GENERO = "data/raw/enade/microdados2023_arq5.txt"
ARQUIVO_INFO_IDADE = "data/raw/enade/microdados2023_arq6.txt"
ARQUIVO_INFO_RACA = "data/raw/enade/microdados2023_arq8.txt"
ARQUIVO_IDH = "data/processed/idh_atlasbrasil.xlsx"


def tratar_dados_gerais():
    
    cols_arquivo1 = ['CO_IES', 'CO_CURSO', 'CO_MUNIC_CURSO','CO_UF_CURSO', 'CO_REGIAO_CURSO', 'CO_GRUPO']
    df_info_geral = pd.read_csv(ARQUIVO_INFO_GERAL, sep=';', encoding='latin1', usecols=cols_arquivo1)
    
    cols_arquivo3 = ['TP_PR_GER']
    df_info_prova = pd.read_csv(ARQUIVO_INFO_PROVA, sep=';', encoding='latin1', usecols=cols_arquivo3)
    
    cols_arquivo5 = ['TP_SEXO']
    df_info_genero = pd.read_csv(ARQUIVO_INFO_GENERO, sep=';', encoding='latin1', usecols=cols_arquivo5)
    
    cols_arquivo6 = ['NU_IDADE']
    df_info_idade = pd.read_csv(ARQUIVO_INFO_IDADE, sep=';', encoding='latin1', usecols=cols_arquivo6)
    
    cols_arquivo8 = ['QE_I02']
    df_info_raca = pd.read_csv(ARQUIVO_INFO_RACA, sep=';', encoding='latin1', usecols=cols_arquivo8)
    
    df_geral = pd.concat([df_info_geral,df_info_prova, df_info_genero, df_info_idade, df_info_raca], axis=1)
    
    df_geral['Desc_UF_Curso'] = df_geral['CO_UF_CURSO'].map(CO_UF_CURSO_LABELS).fillna("Não Informado")
    df_geral['Desc_Regiao_Curso'] = df_geral['CO_REGIAO_CURSO'].map(CO_REGIAO_CURSO_LABELS).fillna("Não Informado")
    df_geral['Desc_Raca'] = df_geral['QE_I02'].map(QE_I02_LABELS).fillna("Não Informado")
    df_geral['Desc_Genero'] = df_geral['TP_SEXO'].map(GENDER_LABELS).fillna("Não Informado")
    df_geral['Presenca'] = df_geral['TP_PR_GER'].map(TP_PR_GER_LABELS).fillna("Não Informado")
    df_geral['NOME_CURSO'] = df_geral['CO_GRUPO'].map(CO_GRUPO_LABELS).fillna(df_geral['CO_GRUPO'].astype(str))
    
    df_geral['Faixa_Idade'] = pd.cut(
        df_geral['NU_IDADE'],
        bins=FAIXA_ETARIA_BINS,
        labels=FAIXA_ETARIA_LABELS,
        right=True
    )
    
    df_geral.to_parquet("data/processed/dados_gerais_estudantes.parquet", index=False)
    print("Dados gerais tratados com sucesso.")
    
    return df_geral


def tratar_dados_idh():
    
    cols_arquivo_idh = ['Territorialidades', 'IDHM 2021','IDHM Educação 2021', 'IDHM Renda 2021']
    df_idh = pd.read_excel(ARQUIVO_IDH, usecols=cols_arquivo_idh, engine='openpyxl')
    print("Dados de IDH tratados com sucesso.")
    
    return df_idh


def relacionar_idh_estados_nota():

    df_prova = pd.read_csv(ARQUIVO_INFO_PROVA, sep=';', encoding='latin1', usecols=['NT_GER'])
    df_geral = pd.read_csv(ARQUIVO_INFO_GERAL, sep=';', encoding='latin1', usecols=['CO_UF_CURSO'])
    
    df_final = pd.concat([df_geral, df_prova], axis=1)
    
    if df_final['NT_GER'].dtype == 'O':
        df_final['NT_GER'] = df_final['NT_GER'].str.replace(',', '.').astype(float)
    
    df_final = df_final.dropna(subset=['NT_GER'])
    
    df_final['Territorialidades'] = df_final['CO_UF_CURSO'].map(CO_UF_CURSO_LABELS)
    
    df_idh = tratar_dados_idh()
    
    df_final = pd.merge(df_final, df_idh, on='Territorialidades', how='left')

    df_final.to_parquet("data/processed/idh_notas_estudos.parquet", index=False)
    print("Dados de IDH e nota tratados com sucesso.")
    
    return df_final


def obter_dados_juiz_de_fora():
    
    cols_curso = ['CO_CURSO', 'CO_MUNIC_CURSO', 'CO_CATEGAD', 'CO_MODALIDADE', 'CO_GRUPO', 'CO_IES']
    
    df_cursos = pd.read_csv(ARQUIVO_INFO_GERAL, sep=';', encoding='latin1', usecols=cols_curso)
    
    cursos_jf = df_cursos[df_cursos['CO_MUNIC_CURSO'] == 3136702].copy()
    cursos_jf = cursos_jf.drop_duplicates(subset=['CO_CURSO'])
    cursos_jf['TIPO_IES'] = cursos_jf['CO_CATEGAD'].map(CO_CATEGAD_LABELS)
    cursos_jf['MODALIDADE'] = cursos_jf['CO_MODALIDADE'].map(CO_MODALIDADE_LABELS)
    
    lista_ids_jf = cursos_jf['CO_CURSO'].unique()
    
    df_notas = pd.read_csv(ARQUIVO_INFO_PROVA, sep=';', encoding='latin1', decimal=',', usecols=['CO_CURSO', 'NT_GER'], dtype={'NT_GER': str})
    df_notas['NT_GER'] = pd.to_numeric(df_notas['NT_GER'].str.strip().str.replace(',','.'), errors='coerce')
    df_notas = df_notas.dropna(subset=['NT_GER'])
   
    df_notas_jf = df_notas[df_notas['CO_CURSO'].isin(lista_ids_jf)].dropna()
    
    df_analise_jf = pd.merge(df_notas_jf, cursos_jf, on='CO_CURSO', how='inner')
    df_analise_jf.to_parquet('data/processed/analise_munic_jf.parquet', index=False)
    
    print("Dados de Juiz de Fora tratados com sucesso.")
    
    return df_analise_jf

    
if __name__ == "__main__":
    tratar_dados_gerais()
    tratar_dados_idh()
    relacionar_idh_estados_nota()
    obter_dados_juiz_de_fora()
    
    
    

    