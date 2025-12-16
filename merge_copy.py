import pandas as pd
from mapeamentos import QE_I19_LABELS
import matplotlib.pyplot as plt

# Defina os caminhos baseados na sua pasta
FILE_CURSO = "data/raw/enade/microdados2023_arq1.txt"  # Dados do Curso (UF, Região)
FILE_NOTAS = "data/raw/enade/microdados2023_arq3.txt"  # Notas (NT_GER)
FILE_RENDA = "data/raw/enade/microdados2023_arq14.txt" # Renda (QE_I08)
FILE_SEXO  = "data/raw/enade/microdados2023_arq5.txt"  # Sexo (TP_SEXO)
FILE_AVALIACAO = "data/raw/enade/microdados2023_arq4.txt"  # Avaliação (TP_ANO_CONCLUIU)
FILE_INCENTIVO = "data/raw/enade/microdados2023_arq25.txt"  # Incentivo (QE_I27)

def processar_enade_2023():
    print("--- 1. Carregando Tabela de CURSOS (Dimensão) ---")
    df_curso = pd.read_csv(FILE_CURSO, sep=';', encoding='latin1')
    cols_curso = ['CO_CURSO', 'CO_UF_CURSO', 'CO_REGIAO_CURSO', 'CO_IES']
    df_curso = df_curso[cols_curso]
    df_curso = df_curso.drop_duplicates(subset=['CO_CURSO'])
    
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