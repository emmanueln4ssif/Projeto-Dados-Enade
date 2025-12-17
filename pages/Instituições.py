import streamlit as st
import pandas as pd
import plotly.express as px
import json
from urllib.request import urlopen

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Demografia - ENADE 2023",
    page_icon="👥",
    layout="wide"
)

# --- CARGA DE DADOS ---
@st.cache_data
def load_data():
    arquivo_parquet = "data/processed/dados_gerais_estudantes.parquet"
    return pd.read_parquet(arquivo_parquet)

try:
    df = load_data()

    # --- CABEÇALHO ---
    st.title("👥 Perfil Demográfico Detalhado")
    st.markdown("Quem são os estudantes por trás dos números? Análise de idade, gênero, raça e interseccionalidade.")

    # --- KPIs GERAIS (Topo) ---
    total_alunos = len(df)
    media_idade = df['NU_IDADE'].mean()
    mulheres = df[df['Desc_Genero'] == 'Feminino'].shape[0]
    perc_mulheres = (mulheres / total_alunos) * 100
    
    # Moda da Raça (a mais comum)
    raca_predominante = df['Desc_Raca'].mode()[0]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Estudantes", f"{total_alunos:,.0f}".replace(",", "."))
    kpi2.metric("Presença Feminina", f"{perc_mulheres:.1f}%")
    kpi3.metric("Média de Idade", f"{media_idade:.0f} anos")
    kpi4.metric("Raça Predominante", raca_predominante)

    st.divider()

    # --- ABAS PARA ORGANIZAR O LAYOUT ---
    tab_geral, tab_cruzada, tab_geo = st.tabs(["📊 Visão Geral", "🔗 Interseccionalidade", "🌍 Geografia da Diversidade"])

    # =================================================================
    # ABA 1: VISÃO GERAL (O Básico bem feito)
    # =================================================================
    with tab_geral:
        col_g, col_r = st.columns([1, 1])

        with col_g:
            st.subheader("Distribuição por Gênero")
            fig_sexo = px.pie(
                df, 
                names='Desc_Genero', 
                hole=0.6, # Donut chart é mais moderno
                color='Desc_Genero',
                color_discrete_map={'Feminino': '#E74C3C', 'Masculino': '#3498DB'}
            )
            st.plotly_chart(fig_sexo, use_container_width=True)

        with col_r:
            st.subheader("Autodeclaração de Raça/Cor")
            # Ordenar do maior para o menor
            raca_counts = df['Desc_Raca'].value_counts().reset_index()
            raca_counts.columns = ['Raça', 'Total']
            
            fig_raca = px.bar(
                raca_counts, 
                x='Total', 
                y='Raça', 
                orientation='h', # Barra horizontal facilita ler os nomes
                text='Total',
                color='Total',
                color_continuous_scale='Blues'
            )
            fig_raca.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_raca, use_container_width=True)

        # Histograma Melhorado
        st.subheader("Curva de Idade por Gênero")
        st.caption("A sobreposição permite ver se há diferença na faixa etária entre homens e mulheres.")
        
        fig_hist = px.histogram(
            df,
            x="NU_IDADE",
            color="Desc_Genero", # <--- AQUI ESTÁ O TRUQUE
            nbins=40,
            barmode="overlay", # Sobrepõe as cores em vez de empilhar
            opacity=0.7,       # Transparência para ver onde cruza
            color_discrete_map={'Feminino': '#E74C3C', 'Masculino': '#3498DB'},
            labels={'NU_IDADE': 'Idade', 'count': 'Estudantes'}
        )
        fig_hist.update_layout(bargap=0.1, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)

    # =================================================================
    # ABA 2: CRUZAMENTO DE DADOS (Insights novos)
    # =================================================================
    with tab_cruzada:
        st.subheader("Matriz de Gênero x Raça")
        st.markdown("Quantos estudantes existem em cada intersecção?")
        
        # Mapa de Calor (Heatmap)
        # Agrupa e conta
        df_heatmap = df.groupby(['Desc_Raca', 'Desc_Genero']).size().reset_index(name='Quantidade')
        
        fig_heat = px.density_heatmap(
            df_heatmap, 
            x="Desc_Genero", 
            y="Desc_Raca", 
            z="Quantidade", 
            text_auto=True, # Mostra o número no quadrado
            color_continuous_scale="Viridis",
            title="Distribuição Cruzada"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
        st.info("💡 **Análise:** Este gráfico ajuda a identificar grupos minoritários específicos (ex: mulheres indígenas) que podem precisar de políticas de inclusão focadas.")

    # =================================================================
    # ABA 3: GEOGRAFIA DA DIVERSIDADE (Sunburst)
    # =================================================================
    with tab_geo:
        st.subheader("Como a diversidade se distribui pelo Brasil?")
        
        # Gráfico Solar (Sunburst)
        # Camada 1: Região -> Camada 2: Raça
        # (Precisa tratar nulos para o gráfico não quebrar)
        df_sun = df.dropna(subset=['Desc_Regiao_Curso', 'Desc_Raca'])
        
        # Agrupamento para ficar leve (não travar o navegador)
        df_sun_grouped = df_sun.groupby(['Desc_Regiao_Curso', 'Desc_Raca']).size().reset_index(name='Total')
        
        fig_sun = px.sunburst(
            df_sun_grouped,
            path=['Desc_Regiao_Curso', 'Desc_Raca'],
            values='Total',
            color='Total',
            color_continuous_scale='RdBu',
            title="Raça por Região (Clique para expandir)"
        )
        st.plotly_chart(fig_sun, use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ Arquivo parquet não encontrado.")
except Exception as e:
    st.error(f"Erro: {e}")