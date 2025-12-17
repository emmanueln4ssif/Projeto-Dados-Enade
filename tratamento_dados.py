import pandas as pd
from mapeamentos import FAIXA_ETARIA_BINS, FAIXA_ETARIA_LABELS, QE_I19_LABELS, QE_I02_LABELS, GENDER_LABELS, REGIONS_LABELS, TP_PR_GER_LABELS, CO_UF_CURSO_LABELS, CO_REGIAO_CURSO_LABELS
import matplotlib.pyplot as plt

ARQUIVO_INFO_GERAL = "data/raw/enade/microdados2023_arq1.txt"
ARQUIVO_INFO_ESTUDANTES = "data/raw/enade/microdados2023_arq2.txt"
ARQUIVO_INFO_PROVA = "data/raw/enade/microdados2023_arq3.txt"
ARQUIVO_INFO_GENERO = "data/raw/enade/microdados2023_arq5.txt"
ARQUIVO_INFO_IDADE = "data/raw/enade/microdados2023_arq6.txt"
ARQUIVO_INFO_RACA = "data/raw/enade/microdados2023_arq8.txt"
ARQUIVO_IDH = "data/processed/idh_atlasbrasil.xlsx"


def tratar_dados_gerais():
    
    print("Carregando dados gerais dos estudantes...")
    
    cols_arquivo1 = ['CO_IES', 'CO_CURSO', 'CO_UF_CURSO', 'CO_REGIAO_CURSO']
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
    print("Dados gerais tratados com sucesso.")
    
    df_geral['Desc_UF_Curso'] = df_geral['CO_UF_CURSO'].map(CO_UF_CURSO_LABELS).fillna("Não Informado")
    df_geral['Desc_Regiao_Curso'] = df_geral['CO_REGIAO_CURSO'].map(CO_REGIAO_CURSO_LABELS).fillna("Não Informado")
    df_geral['Desc_Raca'] = df_geral['QE_I02'].map(QE_I02_LABELS).fillna("Não Informado")
    df_geral['Desc_Genero'] = df_geral['TP_SEXO'].map(GENDER_LABELS).fillna("Não Informado")
    df_geral['Presenca'] = df_geral['TP_PR_GER'].map(TP_PR_GER_LABELS).fillna("Não Informado")
    
    df_geral['Faixa_Idade'] = pd.cut(
        df_geral['NU_IDADE'],
        bins=FAIXA_ETARIA_BINS,
        labels=FAIXA_ETARIA_LABELS,
        right=True
    )
    
    df_geral.to_parquet("data/processed/dados_gerais_estudantes.parquet", index=False)
    
    return df_geral


def tratar_dados_idh():
    
    cols_arquivo_idh = ['Territorialidades', 'IDHM 2021','IDHM Educação 2021', 'IDHM Renda 2021']
    df_idh = pd.read_excel(ARQUIVO_IDH, usecols=cols_arquivo_idh, engine='openpyxl')
    
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
    
    df_final = pd.merge(
        df_final,
        df_idh,
        on='Territorialidades',
        how='left'
    )
    
    print(f"Total de registros válidos para análise: {len(df_final)}")
    print(df_final[:800])
    df_final.to_parquet("data/processed/idh_notas_estudos.parquet", index=False)
    
    return df_final
    
    
if __name__ == "__main__":
    tratar_dados_gerais()
    tratar_dados_idh()
    relacionar_idh_estados_nota()
    
    
    

    