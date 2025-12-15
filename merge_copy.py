import pandas as pd
from mapeamentos import QE_I19_LABELS
import matplotlib.pyplot as plt

# Defina os caminhos baseados na sua pasta
# DICA: Verifique se o arquivo descompactado tem exatamente esse nome ou se é .csv/.txt
FILE_CURSO = "data/raw/enade/microdados2023_arq1.txt"  # Dados do Curso (UF, Região)
FILE_NOTAS = "data/raw/enade/microdados2023_arq3.txt"  # Notas (NT_GER)
FILE_RENDA = "data/raw/enade/microdados2023_arq14.txt" # Renda (QE_I08)
FILE_SEXO  = "data/raw/enade/microdados2023_arq5.txt"  # Sexo (TP_SEXO)
FILE_AVALIACAO = "data/raw/enade/microdados2023_arq4.txt"  # Avaliação (TP_ANO_CONCLUIU)
FILE_INCENTIVO = "data/raw/enade/microdados2023_arq25.txt"  # Incentivo (QE_I27)

def processar_enade_2023():
    print("--- 1. Carregando Tabela de CURSOS (Dimensão) ---")
    # Arquivo 1: Traz a UF e Região do curso 
    # Chave primária: CO_CURSO
    df_curso = pd.read_csv(FILE_CURSO, sep=';', encoding='latin1')
    #salvar em excel:
    cols_curso = ['CO_CURSO', 'CO_UF_CURSO', 'CO_REGIAO_CURSO', 'CO_IES']
    df_curso = df_curso[cols_curso]
    # Remove duplicatas de curso (caso haja) para garantir relação 1:N
    df_curso = df_curso.drop_duplicates(subset=['CO_CURSO'])
    #em excel:
    #df_curso.to_excel("data/processed/df_curso.xlsx", index=False)
    
    print("--- 2. Carregando Tabela de prova (Fato Principal) ---")
    
    cols_uteis = ['NU_ANO', 'CO_CURSO', 'QE_I27']
    df_avaliacao = pd.read_csv(FILE_AVALIACAO, sep=';', encoding='latin1', usecols = cols_uteis)
    #em excel:
    #df_avaliacao.to_excel("data/processed/df_avaliacao.xlsx", index=False)
    
    # print("--- 3. Adicionando Informações do CURSO (Merge) ---")
    # #MERGE
    # df_final = pd.merge(df_avaliacao, df_curso, on='CO_CURSO', how='left')
    # #em excel:
    # df_final.to_excel("data/processed/df_final.xlsx", index=False)
    
    print("--- 4. Incentivo ---")
    df_incentivo = pd.read_csv(FILE_INCENTIVO, sep=';', encoding='latin1')
    df_incentivo['Descricao'] = df_incentivo['QE_I19'].map(QE_I19_LABELS).fillna("Sem Resposta")
    #df_incentivo.to_excel("data/processed/df_incentivo.xlsx", index=False)

    #plotar gráfico de barras da coluna Descricao
    incentivo_counts = df_incentivo['Descricao'].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    incentivo_counts.plot(kind='bar', color='skyblue')
    plt.title('Distribuição dos Tipos de Incentivo (QE_I19)')
    plt.xlabel('Tipo de Incentivo')
    plt.ylabel('Contagem de Estudantes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("data/processed/incentivo_qe_i19.png")
    plt.show()

if __name__ == "__main__":
    processar_enade_2023()