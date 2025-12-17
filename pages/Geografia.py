import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
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
def load_idh_notes_data():
    arquivo_parquet = "data/processed/idh_notas_estudos.parquet"
    return pd.read_parquet(arquivo_parquet)

@st.cache_data
def get_geojson():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    with urlopen(url) as response:
        return json.load(response)

with st.sidebar:
    st.caption("Dados do IDHM 2021 são oriundos do portal oficial do Atlas Brasil (www.atlasbrasil.com.br)")

st.title("Panorama ENADE 2023 - Geografia")
st.markdown("Análise geográfica dos estudantes inscritos no exame.")

try:
    df = load_data()
    geojson_brasil = get_geojson()
    
    total_alunos = len(df)
    total_presentes = df[df['Presenca'].astype(str).str.contains('Presente', case=False, na=False)].shape[0]
    perc_presenca = (total_presentes / total_alunos) * 100
    media_idade = df['NU_IDADE'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Inscritos", f"{total_alunos:,.0f}".replace(",", "."))
    col2.metric("Taxa de Presença", f"{perc_presenca:.1f}%")
    col3.metric("Média de Idade", f"{media_idade:.0f} anos")
    col4.metric("Região Predominante", df['Desc_Regiao_Curso'].mode()[0])

    st.divider()

    
    st.subheader("Distribuição de inscritos pelo território nacional")

    dados_uf = df['Desc_UF_Curso'].value_counts().reset_index()
    dados_uf.columns = ['UF', 'Total']
    
    dados_regiao = df['Desc_Regiao_Curso'].value_counts().reset_index()
    dados_regiao.columns = ['Regiao', 'Total']

    if 'CO_UF_CURSO' in df.columns:
        df['UF_SIGLA_MAPA'] = df['CO_UF_CURSO'].map(CODIGO_UF_PARA_SIGLA)
        dados_mapa = df['UF_SIGLA_MAPA'].value_counts().reset_index()
        dados_mapa.columns = ['UF', 'Total']

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
                labels={'Total': 'Inscritos'}
            )
            fig_mapa.update_geos(fitbounds="locations", visible=False)
            fig_mapa.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                paper_bgcolor="white",
                plot_bgcolor="white",
                height=400
            )
            st.plotly_chart(fig_mapa, use_container_width=True)

    with col_regiao:
        fig_reg = px.bar(
            dados_regiao,
            x='Regiao', y='Total',
            color='Regiao', text='Total',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_reg.update_traces(textposition='outside')
        fig_reg.update_layout(
            showlegend=False, xaxis_title="", yaxis_title="",
            margin=dict(t=30, b=0), height=400,
            title="Inscritos por Região"
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    st.markdown("---")

    st.markdown("**Estados com mais inscritos**")
    st.markdown("Os estados com mais estudantes inscritos no exame se concentram no Centro-Sul do país. Conforme esperado, São Paulo e Minas Gerais figuram nas mesmas posições em relação ao ranking de população absoluta. O Paraná, em terceiro, aparece à frente da Bahia e do Rio de Janeiro, estados com população superior a ele.")
    top3 = dados_uf.head(3)
    c1, c2, c3 = st.columns(3)
    medalhas = ["1º Lugar", "2º Lugar", "3º Lugar"]
    
    for i, col in enumerate([c1, c2, c3]):
        with col:
            st.container(border=True).metric(
                label=f"{medalhas[i]} - {top3.iloc[i]['UF']}", 
                value=f"{top3.iloc[i]['Total']:,.0f}".replace(",", ".")
            )

    st.markdown("**Estados com menos inscritos**")
    st.markdown("Os estados com menos estudantes inscritos repetem o ranking dos 3 estados menos populosos do país, mas Amapá e Acre invertem de posição.")
    bottom3 = dados_uf.tail(3).sort_values('Total', ascending=True)
    c4, c5, c6 = st.columns(3)
    labels_bottom = ["1º Lugar", "2º Lugar", "3º Lugar"]
    
    for i, col in enumerate([c4, c5, c6]):
        with col:
            st.container(border=True).metric(
                label=f"{labels_bottom[i]} - {bottom3.iloc[i]['UF']}", 
                value=f"{bottom3.iloc[i]['Total']:,.0f}".replace(",", "."),
            )

    st.divider()

    st.subheader("O subíndice de Educação do Índice de Desenvolvimento Humano (IDH) e inferências com o desempenho")
    st.markdown("Partindo do pretexto que o IDH é um indicador que leva em conta três pilares: saúde, **educação** e renda. Podemos estabelecer uma relação entre o desenvolvimento educacional de um estado e o desempenho dos estudantes daquele local?")
    st.markdown("O Sub-índice do IDHM relativo à Educação, é obtido a partir da taxa de alfabetização e da taxa bruta de frequência à escola, convertidas em índices por: (valor observado - limite inferior) / (limite superior - limite inferior), com limites inferior e superior de 0% e 100%. O IDH-Educação é a média desses 2 índices, com peso 2 para taxa de alfabetização e peso 1 para o da taxa bruta de frequência. ")

    df_regressao_raw = load_idh_notes_data()

    if df_regressao_raw is not None:
        
        if 'NT_GER' in df_regressao_raw.columns and 'IDHM Educação 2021' in df_regressao_raw.columns:
            
            df_analise = df_regressao_raw.groupby('Territorialidades').agg({
                'IDHM Educação 2021': 'mean',     
                'NT_GER': 'mean',        
                'Territorialidades': 'count' 
            }).rename(columns={'Territorialidades': 'Qtd_Alunos'})
            
            df_analise = df_analise.reset_index()

            X = df_analise['IDHM Educação 2021']
            Y = df_analise['NT_GER']
            X_const = sm.add_constant(X)
            
            modelo = sm.OLS(Y, X_const).fit()
            
            r2 = modelo.rsquared
            p_valor = modelo.pvalues['IDHM Educação 2021']
            coeficiente = modelo.params['IDHM Educação 2021']

            col_graf, col_kpi = st.columns([3, 1], gap="large")


            with col_graf:
                fig_scatter = px.scatter(
                    df_analise,
                    x='IDHM Educação 2021',
                    y='NT_GER',
                    text='Territorialidades', 
                    size='Qtd_Alunos',       
                    trendline='ols',
                    title="Regressão linear: IDHM Educação estadual vs. nota geral média no ENADE 2023",
                    labels={'IDHM 2021': 'IDH (2021)', 'NT_GER': 'Nota geral média (0-99)'},
                    hover_data=['Qtd_Alunos']
                )
                
                fig_scatter.update_traces(
                    textposition='top center',
                    marker=dict(color="#087ac6", line=dict(width=1, color='white'))
                )
                
                fig_scatter.update_layout(
                    height=500,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)


            with col_kpi:
                st.markdown("**Estatísticas do Modelo**")
                
                st.metric(
                    label="R²",
                    value=f"{r2:.2%}",
                    help="Indica o quanto a variação da Nota é explicada pelo IDH. (Ex: 50% significa influência moderada)."
                )
                st.markdown("")

                st.metric(
                    label="Impacto (Coeficiente)",
                    value=f"{coeficiente:.2f}",
                    help="Quanto a nota sobe para cada 1 ponto de IDH."
                )

                st.markdown("---")

                if p_valor < 0.05:
                    st.success("**Relação Significativa!**")
                    st.write(f"Com **p-valor de {p_valor:.4f}**, há evidência estatística de que o IDH afeta a nota.")
                else:
                    st.warning("**Relação Inconclusiva**")
                    st.write(f"Com **p-valor de {p_valor:.4f}**, não podemos afirmar que o IDH afeta a nota.")

            st.markdown("A partir da regressão apresentada, a resposta para o nosso questionamento é **não!** Embora estados da Região Sudeste figurem entre os maiores IDHs do país, a realidade das notas dos candidatos do ENADE 2023 fogem dessa perspectiva. O Espírito Santo, por exemplo, possui o 5º maior IDH do país, porém está entre as menores médias entre os estados. O Maranhão, por sua vez, possui o menor IDH entre as 27 UFs do país, mas tem uma nota acima do Espírito Santo e muito próxima da nota média do estado de São Paulo.")

            with st.expander("Ver tabela de dados agrupados"):
            
                st.dataframe(
                    df_analise[['Territorialidades', 'Qtd_Alunos', 'NT_GER', 'IDHM Educação 2021']]
                    .sort_values('NT_GER', ascending=True)
                    .style.format({'IDHM Educação 2021': '{:.3f}', 'NT_GER': '{:.2f}'})
                )

        else:
            st.error("Colunas não encontradas")
            
    else:
        st.warning("Arquivo de dados não encontrado")

except FileNotFoundError:
    st.error("Arquivo de dados não encontrado")
except Exception as e:
    st.error(f"Erro inesperado: {e}")