import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Home - Análise ENADE 2023",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #2C3E50; font-weight: 700; }
    .sub-header { font-size: 1.5rem; color: #34495E; }
    .card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    try:
        return pd.read_parquet("data/processed/dados_gerais_estudantes.parquet")
    except FileNotFoundError:
        return None

df = load_data()


# Cabeçalho
st.header('Análise de dados do ENADE 2023')
st.subheader('Prova prática - Processo seletivo CAEd')
st.markdown('**Candidato:** Emmanuel Gomes Nassif')

st.divider()

c_text, c_img = st.columns([2, 1])

with c_text:
    st.subheader("Sobre o Projeto")
    st.markdown("""
    Este dashboard foi desenvolvido como parte de um processo seletivo para o **CAEd**, com o objetivo de demonstrar competências em **Engenharia de Dados** e **Análise Exploratória**.
    
    **Os principais objetivos desta análise são:**
    1.  **Mapear o perfil sociodemográfico** dos estudantes brasileiros.
    2.  **Identificar correlações** entre fatores socioeconômicos (como IDH) e desempenho acadêmico.
    3.  **Visualizar a distribuição geográfica** e as disparidades regionais no ensino superior.
    """)

with c_img:
    st.markdown("""
    <div class="card">
        <h4>Tecnologias utilizadas</h4>
        <ul>
            <li><b>Linguagem:</b> Python</li>
            <li><b>Processamento:</b> Pandas & NumPy</li>
            <li><b>Visualização:</b> Plotly Express & Streamlit</li>
            <li><b>Estatística:</b> Statsmodels</li>
            <li><b>Armazenamento:</b> Parquet</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


st.info("💡 **Dica de Navegação:** Utilize o menu lateral para acessar as visões detalhadas de Demografia, Geografia e Desempenho.")
st.divider()

st.subheader("Organização do projeto")
st.markdown("O processo de transformação dos dados brutos até este dashboard seguiu o seguinte fluxo:")

st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box, style=filled, fillcolor="#f0f2f6", fontname="Helvetica"];
        
        raw [label="Dados Brutos\n(TXT/CSV)", fillcolor="#ffeebb", shape=folder];
        pandas [label="Script ETL\n(Pandas/Python)", fillcolor="#d9eaf7", shape=component];
        clean [label="Limpeza e\nPadronização", fillcolor="#d9eaf7"];
        parquet [label="Base Otimizada\n(.parquet)", fillcolor="#d4edda", shape=cylinder];
        dash [label="Dashboard\nStreamlit", fillcolor="#ffcccc", shape=rect];

        raw -> pandas;
        pandas -> clean;
        clean -> parquet;
        parquet -> dash;
    }
""")

with st.expander("📂 Ver Dicionário de Variáveis (Estrutura da Base)"):
    st.markdown("""
    A base processada contém as seguintes colunas principais:
    
    | Coluna | Descrição | Tipo |
    | :--- | :--- | :--- |
    | **NU_ANO** | Ano de referência do exame | Numérico |
    | **CO_UF_CURSO** | Código IBGE da UF do curso | Numérico |
    | **Desc_UF_Curso** | Sigla da UF (Ex: MG, SP) | Texto |
    | **TP_SEXO** | Sexo biológico (M/F) | Categórico |
    | **NU_IDADE** | Idade do inscrito na data da prova | Numérico |
    | **TP_COR_RACA** | Código da cor/raça | Numérico |
    | **Desc_Raca** | Descrição da raça (Branca, Parda, etc) | Texto |
    | **NT_GER** | Nota Geral (Bruta) | Numérico |
    | **IDH** | Índice de Desenvolvimento Humano (Cruzamento) | Numérico |
    """)

st.markdown("---")
st.caption("Desenvolvido por **Emmanuel** | Dados: INEP/ENADE 2023")