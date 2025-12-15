import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from mapeamentos import QE_I19_LABELS # Certifique-se que este arquivo existe

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Análise ENADE 2023 - Incentivo (QE_I19)",
    layout="wide"
)

# --- 2. FUNÇÃO PRINCIPAL DE PROCESSAMENTO (ADAPTADA) ---

def processar_e_plotar_incentivo(df_incentivo):
    """
    Processa a coluna QE_I19 e plota o gráfico de barras.
    Recebe o DataFrame já carregado.
    """
    st.header("Análise da Pergunta: Incentivo (QE_I19)")
    
    # Processamento: Mapear e Tratar Vazios
    # Assumindo que a coluna de interesse é 'QE_I19'
    if 'QE_I19' in df_incentivo.columns:
        df_incentivo['Descricao'] = df_incentivo['QE_I19'].map(QE_I19_LABELS).fillna("Sem Resposta")
        
        # Preparação dos Dados para o Gráfico
        incentivo_counts = df_incentivo['Descricao'].value_counts().sort_values(ascending=True) # Ordena do menor para o maior para Barh
        
        st.subheader("Distribuição dos Tipos de Incentivo")
        
        # 3. Plotagem do Gráfico com Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Usando gráfico de barras HORIZONTAIS para textos longos (Melhor Visualização)
        incentivo_counts.plot(kind='barh', color='#1f77b4', ax=ax) # Usamos ax=ax para desenhar no eixo
        
        ax.set_title('Distribuição dos Tipos de Incentivo (QE_I19)', fontsize=14)
        ax.set_xlabel('Contagem de Estudantes', fontsize=12)
        ax.set_ylabel('Tipo de Incentivo', fontsize=12)
        ax.grid(axis='x', linestyle='--', alpha=0.6)
        
        # Adiciona o valor em cada barra (Opcional, mas útil)
        for index, value in enumerate(incentivo_counts):
            ax.text(value, index, f' {value}', va='center', fontweight='bold', fontsize=9)
            
        plt.tight_layout()
        
        # Comando mágico do Streamlit para exibir o gráfico!
        st.pyplot(fig)
        
        st.write("Total de observações processadas:", len(df_incentivo))

    else:
        st.error("Coluna 'QE_I19' não encontrada no arquivo de Incentivo!")

# --- 3. CARREGAMENTO INTERATIVO DOS ARQUIVOS (PARA NÃO PRECISAR DO CAMINHO FIXO) ---

def main():
    st.title("Sistema de Análise ENADE 2023 🇧🇷")
    st.write("texto")

    # Upload do Arquivo de Incentivo
    uploaded_file = "data/raw/enade/microdados2023_arq25.txt"

    if uploaded_file is not None:
        try:
            # Carrega o arquivo com o separador correto
            df_incentivo = pd.read_csv(uploaded_file, sep=';', encoding='latin1')
            st.success("Arquivo carregado com sucesso!")
            
            # Chama a função que processa e plota
            processar_e_plotar_incentivo(df_incentivo)

        except Exception as e:
            st.error(f"Erro ao ler ou processar o arquivo. Verifique se o separador é o ponto e vírgula (';') e se a codificação é 'latin1'. Erro: {e}")

if __name__ == "__main__":
    main()