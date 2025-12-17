import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.api as sm

st.set_page_config(page_title="Diversidade e Inclusão", page_icon="🌈", layout="wide")

@st.cache_data
def load_idh_data():
    # Carrega os dados preparados para regressão (IDH x Notas)
    try:
        return pd.read_parquet("data/processed/idh_notas_estudos.parquet")
    except FileNotFoundError:
        return None

@st.cache_data
def load_general_data():
    return pd.read_parquet("data/processed/dados_gerais_estudantes.parquet")

st.title("🌈 Diversidade, Inclusão e Desigualdade")
st.markdown("""
Nesta seção, investigamos como fatores sociais e econômicos se entrelaçam com o ensino superior.
Focamos no **Requisito 3** do desafio: testar uma hipótese de regressão.
""")

tab1, tab2 = st.tabs(["📉 Hipótese: IDH x Desempenho", "🌍 Geografia Racial"])

# --- ABA 1: O TESTE DE HIPÓTESE (REGRESSÃO) ---
with tab1:
    st.header("Laboratório de Hipóteses")
    st.info("🧪 **Hipótese:** O desenvolvimento humano (IDH) do estado influencia a nota média dos estudantes?")
    
    df_reg = load_idh_data()
    
    if df_reg is not None and 'IDHM 2021' in df_reg.columns and 'NT_GER' in df_reg.columns:
        
        # 1. Agrupamento (Transformar Alunos em Estados)
        df_estado = df_reg.groupby('Territorialidades').agg({
            'IDHM 2021': 'mean',
            'NT_GER': 'mean',
            'Territorialidades': 'count'
        }).rename(columns={'Territorialidades': 'Qtd_Inscritos'}).reset_index()
        
        # 2. Modelo Estatístico
        X = df_estado['IDHM 2021']
        Y = df_estado['NT_GER']
        X_sm = sm.add_constant(X)
        modelo = sm.OLS(Y, X_sm).fit()
        
        # Métricas
        r2 = modelo.rsquared
        p_valor = modelo.pvalues['IDHM 2021']
        
        # 3. Visualização
        col_graf, col_stats = st.columns([2, 1])
        
        with col_graf:
            fig = px.scatter(
                df_estado, x='IDHM 2021', y='NT_GER',
                text='Territorialidades', size='Qtd_Inscritos',
                trendline='ols',
                title="Regressão Linear: IDH vs. Nota Média",
                labels={'IDHM 2021': 'IDH do Estado', 'NT_GER': 'Nota Média'},
                hover_data=['Qtd_Inscritos']
            )
            fig.update_traces(textposition='top center', marker=dict(color='#8e44ad'))
            fig.update_layout(height=500, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_stats:
            st.subheader("Resultados Estatísticos")
            st.metric("R² (Correlação)", f"{r2:.2%}", help="Quanto o IDH explica a nota.")
            st.metric("P-Valor", f"{p_valor:.4f}", help="Se < 0.05, a relação é real.")
            
            st.markdown("---")
            if p_valor < 0.05:
                st.success("✅ **Hipótese Confirmada!**\nHá correlação significativa: estados mais desenvolvidos tendem a ter notas maiores.")
            else:
                st.warning("⚠️ **Hipótese Não Confirmada**\nNão há evidência estatística suficiente nesta amostra.")
    else:
        st.error("Dados para regressão não encontrados. Execute o ETL 'relacionar_idh_estados_nota'.")

# --- ABA 2: GEOGRAFIA RACIAL ---
with tab2:
    df_geral = load_general_data()
    st.header("Distribuição Racial por Região")
    
    if df_geral is not None:
        # Gráfico Sunburst (Solar)
        df_sun = df_geral.groupby(['Desc_Regiao_Curso', 'Desc_Raca']).size().reset_index(name='Total')
        
        fig_sun = px.sunburst(
            df_sun, path=['Desc_Regiao_Curso', 'Desc_Raca'], values='Total',
            color='Total', color_continuous_scale='RdBu',
            title="Clique na Região para ver a proporção racial"
        )
        st.plotly_chart(fig_sun, use_container_width=True)
    else:
        st.warning("Dados gerais não carregados.")