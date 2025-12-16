import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mapeamentos import QE_I19_LABELS

st.set_page_config(
    page_title="Análise de Dados do ENADE 2023",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("📂 Configurações")
    st.markdown("Faça o upload dos microdados para gerar a análise.")
    
    uploaded_file = "data/raw/enade/microdados2023_arq25.txt"
    
    st.divider()
    st.info("ℹ️ **Sobre**: Dashboard desenvolvido para análise de incentivo acadêmico baseado nos microdados do INEP/ENADE.")

st.title("Análise de dados do ENADE 2023")
st.markdown("Desafio prático CAEd - Estagiário em Pesquisa de Avaliação")

if uploaded_file is not None:
    try:
        # Carregamento com cache para não recarregar toda hora que mudar um filtro
        @st.cache_data
        def load_data(file):
            return pd.read_csv(file, sep=';', encoding='latin1')

        df = load_data(uploaded_file)
        
        if 'QE_I19' in df.columns:
            # --- PROCESSAMENTO ---
            df['Descricao'] = df['QE_I19'].map(QE_I19_LABELS).fillna("Não Informado")
            incentivo_counts = df['Descricao'].value_counts().sort_values(ascending=True)
            
            # Cálculos para os KPIs (Indicadores)
            total_respondentes = len(df)
            top_incentivo = incentivo_counts.idxmax() # O nome do maior incentivo
            top_incentivo_qtd = incentivo_counts.max()
            pct_top = (top_incentivo_qtd / total_respondentes) * 100

            st.divider()

            # --- LINHA DE KPIs (MÉTRICAS) ---
            # Aqui criamos 3 colunas para mostrar números grandes
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(label="Total de Estudantes", value=f"{total_respondentes:,}".replace(",", "."))
            
            with col2:
                st.metric(label="Maior Incentivador", value=top_incentivo)
            
            with col3:
                st.metric(label="Dominância do Líder", value=f"{pct_top:.1f}%")

            st.divider()

            # --- ÁREA DO GRÁFICO ---
            col_grafico, col_tabela = st.columns([2, 1]) # Proporção: Gráfico ocupa 2/3, Tabela 1/3

            with col_grafico:
                st.subheader("📊 Distribuição de Respostas")
                
                # Plotagem "Clean"
                fig, ax = plt.subplots(figsize=(8, 5))
                # Cor personalizada e barras horizontais
                incentivo_counts.plot(kind='barh', color='#2E86C1', edgecolor='none', ax=ax, width=0.7)
                
                # Removendo poluição visual do gráfico (bordas)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_color('#DDDDDD')
                
                ax.set_xlabel("Quantidade", color='#555555')
                ax.set_ylabel("") # Remove o label Y pois os textos já explicam
                ax.tick_params(axis='x', colors='#555555')
                ax.tick_params(axis='y', left=False) # Remove os tracinhos do eixo Y
                
                # Grid vertical suave
                ax.grid(axis='x', linestyle=':', alpha=0.5)

                # Valores na ponta das barras
                for index, value in enumerate(incentivo_counts):
                    ax.text(value + (value * 0.01), index, f' {value}', va='center', fontsize=9, color='#333333')

                st.pyplot(fig)

            with col_tabela:
                st.subheader("📋 Detalhes")
                # Criando um dataframe mais bonito para exibição
                df_display = incentivo_counts.sort_values(ascending=False).reset_index()
                df_display.columns = ['Incentivo', 'Qtd']
                
                # Mostra a tabela interativa sem o índice numérico
                st.dataframe(
                    df_display, 
                    hide_index=True, 
                    use_container_width=True,
                    height=400 # Altura fixa para alinhar com o gráfico
                )

            # --- DADOS BRUTOS (Escondidos) ---
            with st.expander("🔍 Ver amostra dos dados brutos (Raw Data)"):
                st.dataframe(df.head(50))

        else:
            st.error("A coluna QE_I19 não foi encontrada.")

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")

else:
    # Estado inicial (sem arquivo)
    # Mostra um "placeholder" bonito
    st.info("👈 Utilize a barra lateral para carregar seus dados.")
    
    # Dica visual: Cria colunas vazias só para ilustrar como ficaria
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Estudantes", "---")
    c2.metric("Maior Incentivador", "---")
    c3.metric("Percentual", "---")