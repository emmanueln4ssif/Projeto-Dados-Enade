import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Contexto Local: Juiz de Fora", page_icon="🏛️", layout="wide")

@st.cache_data
def load_data():
    return pd.read_parquet("data/processed/dados_gerais_estudantes.parquet")

df = load_data()

st.title("🏛️ Contexto Local: Juiz de Fora (Benchmarking)")
st.markdown("Respondendo ao **Requisito 2**: Perguntas comparativas entre o cenário local e nacional.")


if 'CO_MUNIC_CURSO' in df.columns:
    df_local = df[df['CO_MUNIC_CURSO'] == 3136702] # Código IBGE de JF
    criterio = "Código IBGE (3136702)"
# Se não tiver código, tenta pelo nome (pode precisar ajustar a string exata)
elif 'Desc_Munic_Curso' in df.columns:
    df_local = df[df['Desc_Munic_Curso'].str.upper() == 'JUIZ DE FORA']
    criterio = "Nome do Município"
else:
    df_local = df[df['Desc_UF_Curso'] == 'MG'].sample(frac=0.1) 
    criterio = "Simulação (Amostra MG - Ajuste seu ETL!)"
    st.warning("⚠️ Coluna de município não encontrada. Mostrando dados simulados de MG.")

if len(df_local) > 0:
    st.success(f"Filtro aplicado: {criterio} | {len(df_local)} estudantes encontrados.")
    
    st.divider()

    # --- PERGUNTA 1: DESEMPENHO ---
    st.subheader("1. O estudante de JF tem nota superior à média nacional?")
    
    if 'NT_GER' in df.columns:
        media_br = df['NT_GER'].mean()
        media_jf = df_local['NT_GER'].mean()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Média Brasil", f"{media_br:.2f}")
            st.metric("Média Juiz de Fora", f"{media_jf:.2f}", delta=f"{media_jf - media_br:.2f}")
        
        with col2:
            # Gráfico de Velocímetro
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = media_jf,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Nota Média Local"},
                delta = {'reference': media_br},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#2ecc71" if media_jf > media_br else "#e74c3c"},
                    'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': media_br}
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.info("Dados de nota (NT_GER) não disponíveis para comparação.")

    st.divider()

    # --- PERGUNTA 2: EQUIDADE DE GÊNERO ---
    st.subheader("2. A presença feminina em JF acompanha a tendência nacional?")
    
    perc_mulheres_br = (df[df['Desc_Genero'] == 'Feminino'].shape[0] / len(df)) * 100
    perc_mulheres_jf = (df_local[df_local['Desc_Genero'] == 'Feminino'].shape[0] / len(df_local)) * 100
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f"### 🇧🇷 Brasil: **{perc_mulheres_br:.1f}%** Mulheres")
        fig_br = px.pie(df, names='Desc_Genero', color_discrete_sequence=['#3498db', '#e74c3c'], hole=0.5)
        fig_br.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_br, use_container_width=True)
        
    with c2:
        st.markdown(f"### 🏛️ Juiz de Fora: **{perc_mulheres_jf:.1f}%** Mulheres")
        fig_jf = px.pie(df_local, names='Desc_Genero', color_discrete_sequence=['#3498db', '#e74c3c'], hole=0.5)
        fig_jf.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_jf, use_container_width=True)

else:
    st.error("Não foram encontrados dados para Juiz de Fora. Verifique se o código 3136702 existe na coluna CO_MUNIC_CURSO.")