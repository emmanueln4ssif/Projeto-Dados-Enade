import pandas as pd

# Defina os caminhos baseados na sua pasta
# DICA: Verifique se o arquivo descompactado tem exatamente esse nome ou se é .csv/.txt
FILE_CURSO = "data/raw/enade/microdados2023_arq1.txt"  # Dados do Curso (UF, Região)
FILE_NOTAS = "data/raw/enade/microdados2023_arq3.txt"  # Notas (NT_GER)
FILE_RENDA = "data/raw/enade/microdados2023_arq14.txt" # Renda (QE_I08)
FILE_SEXO  = "data/raw/enade/microdados2023_arq5.txt"  # Sexo (TP_SEXO)

def processar_enade_2023():
    print("--- 1. Carregando Tabela de CURSOS (Dimensão) ---")
    # Arquivo 1: Traz a UF e Região do curso 
    # Chave primária: CO_CURSO
    cols_curso = ['CO_CURSO', 'CO_UF_CURSO', 'CO_REGIAO_CURSO', 'CO_IES']
    df_curso = pd.read_csv(FILE_CURSO, sep=';', encoding='latin1', usecols=cols_curso)
    
    # Remove duplicatas de curso (caso haja) para garantir relação 1:N
    df_curso = df_curso.drop_duplicates(subset=['CO_CURSO'])
    
    print("--- 2. Carregando Tabela de NOTAS (Fato Principal) ---")
    # Arquivo 3: Traz a Nota Geral 
    # IMPORTANTE: Estamos assumindo que NU_INSCRICAO existe no arquivo.
    # Se der erro de 'KeyError', o INEP pode ter mudado o nome da coluna de ID.
    cols_notas = ['NU_INSCRICAO', 'CO_CURSO', 'NT_GER', 'TP_PRES']
    
    # Lendo apenas as primeiras linhas para verificar se NU_INSCRICAO existe
    check_cols = pd.read_csv(FILE_NOTAS, sep=';', encoding='latin1', nrows=5).columns
    if 'NU_INSCRICAO' not in check_cols:
        raise ValueError("ERRO CRÍTICO: Não encontrei a coluna NU_INSCRICAO para cruzar os alunos!")

    df_main = pd.read_csv(FILE_NOTAS, sep=';', encoding='latin1', decimal=',', usecols=cols_notas)
    
    # Filtrar apenas quem esteve presente (TP_PRES geralmente 555 ou presente na prova)
    # Ajuste conforme dicionário real, mas vamos manter quem tem nota
    df_main = df_main.dropna(subset=['NT_GER'])

    print("--- 3. Cruzando com RENDA (Merge 1) ---")
    # Arquivo 14: Traz a Renda (QE_I08 ou QE_108 - confirme no arquivo real) 
    # O manual diz 'QE_108', mas às vezes no header vem 'QE_I08'. Vamos checar.
    cols_renda = ['NU_INSCRICAO', 'QE_I08'] # Tente 'QE_108' se der erro
    
    try:
        df_renda = pd.read_csv(FILE_RENDA, sep=';', encoding='latin1', usecols=cols_renda)
    except ValueError:
        # Fallback se o nome for diferente
        cols_renda = ['NU_INSCRICAO', 'QE_108']
        df_renda = pd.read_csv(FILE_RENDA, sep=';', encoding='latin1', usecols=cols_renda)

    df_final = pd.merge(df_main, df_renda, on='NU_INSCRICAO', how='left')

    print("--- 4. Cruzando com SEXO (Merge 2) ---")
    # Arquivo 5: Traz o Sexo 
    cols_sexo = ['NU_INSCRICAO', 'TP_SEXO']
    df_sexo = pd.read_csv(FILE_SEXO, sep=';', encoding='latin1', usecols=cols_sexo)
    
    df_final = pd.merge(df_final, df_sexo, on='NU_INSCRICAO', how='left')

    print("--- 5. Adicionando Informações do CURSO (Merge 3) ---")
    # Agora cruzamos usando CO_CURSO para saber de qual Estado o aluno é
    df_final = pd.merge(df_final, df_curso, on='CO_CURSO', how='left')

    print("--- Salvando Dataset Consolidado ---")
    df_final.to_parquet("data/enade_2023_completo.parquet")
    print(f"Processo concluído! Base pronta com {len(df_final)} alunos.")

if __name__ == "__main__":
    processar_enade_2023()