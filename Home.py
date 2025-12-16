import streamlit as st
import pandas as pd
import plotly.express as px
import json
from urllib.request import urlopen
from mapeamentos import CODIGO_UF_PARA_SIGLA

st.set_page_config(
    page_title="Prova Prática CAEd - ENADE 2023",
    page_icon="🎓",
    layout="wide"
)

@st.cache_data
def load_data():
    arquivo_parquet = "data/processed/dados_gerais_estudantes.parquet"
    return pd.read_parquet(arquivo_parquet)

@st.cache_data
def get_geojson():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    with urlopen(url) as response:
        return json.load(response)


with st.sidebar:
    st.header("⚙️ Filtros e Info")
    st.info("Visualizando dados nacionais consolidados.")
    st.caption("Dados de Gênero, Raça, Idade, Presença e Localidade.")


st.title("🎓 Panorama ENADE 2023")
st.markdown("Análise demográfica e geográfica dos estudantes inscritos.")

try:
    df = load_data()
    # =================================================================
    # BLOCO 3: PERFIL DEMOGRÁFICO (MANTIDO)
    # =================================================================
    st.header("👥 Perfil do Estudante")

    col_g, col_r = st.columns([1, 2])

    with col_g:
        st.subheader("Gênero")
        sexo_counts = df['Desc_Genero'].value_counts().reset_index()
        sexo_counts.columns = ['Gênero', 'Total']
        fig_sexo = px.pie(sexo_counts, names='Gênero', values='Total', hole=0.5, 
                          color_discrete_sequence=['#3498db', '#e74c3c'])
        st.plotly_chart(fig_sexo, use_container_width=True)

    with col_r:
        st.subheader("Raça/Cor")
        raca_counts = df['Desc_Raca'].value_counts().reset_index()
        raca_counts.columns = ['Raça', 'Total']
        fig_raca = px.bar(raca_counts, x='Raça', y='Total', color='Raça', text='Total')
        fig_raca.update_traces(textposition='outside')
        fig_raca.update_layout(showlegend=False)
        st.plotly_chart(fig_raca, use_container_width=True)

    # Faixa Etária
    st.subheader("Distribuição Etária")
    idade_counts = df['Faixa_Idade'].value_counts().sort_index().reset_index()
    idade_counts.columns = ['Faixa', 'Total']
    fig_idade = px.bar(idade_counts, x='Faixa', y='Total', color='Total', color_continuous_scale='Blues')
    st.plotly_chart(fig_idade, use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ Arquivo 'dados_gerais_estudantes.parquet' não encontrado. Rode o script de ETL.")
except Exception as e:
    st.error(f"Erro inesperado: {e}")