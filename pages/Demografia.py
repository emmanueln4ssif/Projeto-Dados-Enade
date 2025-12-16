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
    geojson_brasil = get_geojson()

    # =================================================================
    # BLOCO GEOGRÁFICO REDESENHADO
    # =================================================================
    st.subheader("Distribuição de inscritos pelo território nacional")

    # 1. PREPARAÇÃO DOS DADOS
    # Contagem por Estado
    dados_uf = df['Desc_UF_Curso'].value_counts().reset_index()
    dados_uf.columns = ['UF', 'Total']
    
    # Contagem por Região
    dados_regiao = df['Desc_Regiao_Curso'].value_counts().reset_index()
    dados_regiao.columns = ['Regiao', 'Total']

    # Dados para o Mapa (criando a sigla)
    if 'CO_UF_CURSO' in df.columns:
        df['UF_SIGLA_MAPA'] = df['CO_UF_CURSO'].map(CODIGO_UF_PARA_SIGLA)
        dados_mapa = df['UF_SIGLA_MAPA'].value_counts().reset_index()
        dados_mapa.columns = ['UF', 'Total']

    # -----------------------------------------------------------------
    # LINHA 1: MAPA (Esquerda) + GRÁFICO REGIÕES (Direita)
    # -----------------------------------------------------------------
    col_mapa, col_regiao = st.columns([3, 2], gap="medium")
    
    with col_mapa:
        
        if 'CO_UF_CURSO' in df.columns:
            fig_mapa = px.choropleth(
                dados_mapa,
                geojson=geojson_brasil,
                locations='UF',        
                featureidkey='properties.sigla', 
                color='Total',
                color_continuous_scale="Blues",
                hover_name='UF',
                hover_data={'UF': False, 'Total': True},
                labels={'Total': 'Número de Inscritos'},
            )
            fig_mapa.update_geos(fitbounds="locations", visible=False)
            fig_mapa.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400
            )
            st.plotly_chart(fig_mapa, use_container_width=True)

    with col_regiao:
        fig_reg = px.bar(
            dados_regiao,
            x='Regiao',
            y='Total',
            color='Regiao', # Cada região uma cor
            text='Total',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_reg.update_traces(textposition='outside')
        fig_reg.update_layout(
            showlegend=False, 
            xaxis_title="", 
            yaxis_title="",
            margin=dict(t=20, b=0),
            height=400, 
            title="Inscritos por Região"
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    st.markdown("---") # Linha divisória suave

    # -----------------------------------------------------------------
    # LINHA 2: TOP 3 MAIORES INSCRITOS
    # -----------------------------------------------------------------
    st.subheader("🏆 Estados com Maior Participação")
    
    top3 = dados_uf.head(3) # Os 3 primeiros
    c1, c2, c3 = st.columns(3)
    
    medalhas = ["🥇 1º Lugar", "🥈 2º Lugar", "🥉 3º Lugar"]
    
    for i, col in enumerate([c1, c2, c3]):
        with col:
            estado = top3.iloc[i]['UF']
            qtd = top3.iloc[i]['Total']
            st.container(border=True).metric(
                label=f"{medalhas[i]} - {estado}", 
                value=f"{qtd:,.0f}".replace(",", "."),
                help="Estados com maior número absoluto de inscritos"
            )

    # -----------------------------------------------------------------
    # LINHA 3: TOP 3 MENORES INSCRITOS
    # -----------------------------------------------------------------
    st.subheader("🔻 Estados com Menor Participação")
    
    # Pegamos os 3 últimos e ordenamos para mostrar do menor para o maior
    bottom3 = dados_uf.tail(3).sort_values('Total', ascending=True)
    c4, c5, c6 = st.columns(3)
    
    labels_bottom = ["Menor Participação", "2ª Menor", "3ª Menor"]
    
    for i, col in enumerate([c4, c5, c6]):
        with col:
            estado = bottom3.iloc[i]['UF']
            qtd = bottom3.iloc[i]['Total']
            st.container(border=True).metric(
                label=f"{labels_bottom[i]} - {estado}", 
                value=f"{qtd:,.0f}".replace(",", "."),
                delta="- Baixa Adesão", # Mostra setinha vermelha pra baixo
                delta_color="inverse"   # Vermelho indica 'atenção'
            )

    st.divider()
    
    st.subheader(" O Índice de Desenvolvimento Humano (IDH) e inferências com a Participação no ENADE ")

except FileNotFoundError:
    st.error("⚠️ Arquivo 'dados_gerais_estudantes.parquet' não encontrado. Rode o script de ETL.")
except Exception as e:
    st.error(f"Erro inesperado: {e}")