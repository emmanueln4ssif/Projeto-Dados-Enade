import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from mapeamentos import CO_GRUPO_LABELS

st.set_page_config(page_title="Um enfoque em Juiz de Fora", page_icon="🏛️", layout="wide")

@st.cache_data
def load_data_jf():
    return pd.read_parquet("data/processed/analise_munic_jf.parquet")

df = load_data_jf()

st.title("Panorama do exame em Juiz de Fora")
st.markdown("Reconhecida nacionalmente como uma **cidade universitária**, Juiz de Fora abriga um cenário acadêmico diverso e competitivo. A coexistência de uma Universidade Federal de ponta com grupos da educação privada cria um ótimo ambiente para análise de dados do ENADE.")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("Total de estudantes com nota válida", len(df))
col_kpi2.metric("Média geral da cidade", f"{df['NT_GER'].mean():.2f}")
col_kpi3.metric("Total de cursos avaliados", df['CO_CURSO'].nunique())

st.divider()

st.header("Desempenho por tipo de IES")
st.markdown("O gráfico abaixo apresenta a média geral dos estudantes agrupada pelo tipo de instituição. O destaque fica para a **Rede Pública Federal**, com a maior média do comparativo (**61.2**), seguida pelas instituições **Comunitárias/Confessionais** (**54.5**). As faculdades privadas (com e sem fins lucrativos) aparecem na sequência, com médias próximas a 51 pontos.")  

media_ies = df.groupby('TIPO_IES')['NT_GER'].mean().round(2).reset_index()
    
fig2 = px.bar(
    media_ies,
    x='NT_GER',       
    y='TIPO_IES',     
    orientation='h',  
    text_auto='.1f',  
    color='NT_GER',   
    title="Nota média por tipo de instituição",
    labels={
        'NT_GER': 'Nota Média',      
        'TIPO_IES': 'Tipo de IES'       
    }
)
    
fig2.update_layout(
    xaxis_title="Nota Média",
    yaxis_title="",
    yaxis={'categoryorder':'total ascending'}, 
    showlegend=False
)
    
st.plotly_chart(fig2, use_container_width=True)
st.divider()


st.header("Ranking: melhores áreas em Juiz de Fora")
st.markdown("Cursos com maiores médias (considerando apenas áreas com mais de 10 alunos para relevância estatística).")
st.markdown("""
### Onde estão as melhores notas?
O ranking revela uma forte polarização entre as áreas de **Saúde** e **Engenharias**.

Dos 10 cursos com melhores médias na cidade, 5 pertencem ao eixo de Saúde e Bem-estar, enquanto as Engenharias marcam presença com três representates (Ambiental, Produção e Mecânica). Isso indica que é nestas áreas que se concentra a maior competitividade acadêmica e, possivelmente, as maiores notas de corte da região.
""")

if 'NOME_CURSO' not in df.columns:
    df['NOME_CURSO'] = df['CO_GRUPO'].map(CO_GRUPO_LABELS).fillna(df['CO_GRUPO'].astype(str))

stats_curso = df.groupby('NOME_CURSO')['NT_GER'].agg(['mean', 'count']).round(2).reset_index()

top_cursos = stats_curso[stats_curso['count'] >= 10].sort_values('mean', ascending=True).tail(10)

fig3 = px.bar(
    top_cursos,
    x='mean',          
    y='NOME_CURSO',    
    orientation='h', 
    text_auto='.1f',   
    title="Top 10 áreas com melhor desempenho",
    color='mean',
    labels={
        'mean': 'Nota média',      
        'NOME_CURSO': 'Curso'       
    }     
)

fig3.update_layout(
    xaxis_title="Nota média geral",
    yaxis_title="",
    showlegend=False
)

st.plotly_chart(fig3, use_container_width=True)



st.header("Distribuição das notas")
st.markdown("Como as notas dos alunos estão espalhadas? A maioria tira nota alta ou baixa?")
st.markdown("""
### O Equilíbrio da Curva Normal
A distribuição das notas em Juiz de Fora apresenta um comportamento estatístico semelhante a uma **Curva Gaussiana (Normal)** quase perfeita.

Pela convergência entre a **Média (55.83)** e a **Mediana (56.00)**, podemos perceber que não há distorções significativas nos dados. Ou seja, não houve um grupo excessivo de alunos tirando zero, nem um excesso de notas 100. Isso pode indicar que a prova foi bem desenvolvida para medir o conhecimento médio dos estudantes.
""")

col_d1, col_d2 = st.columns([3, 1])

with col_d1:
    
    media = df['NT_GER'].round(2).mean()
    mediana = df['NT_GER'].round(2).median()

    fig_hist = px.histogram(
        df, 
        x="NT_GER", 
        nbins=30, 
        title=f"Distribuição de Notas em Juiz de Fora (N={len(df)})",
        opacity=0.7,
        color_discrete_sequence=['skyblue'],
        labels={
            'Nota Geral': 'Faixa de nota',      
            'count': 'Quantidade de alunos'       
        } 
    )

    fig_hist.add_vline(
        x=media, 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"Média: {media:.1f}", 
        annotation_position="top right"
    )
    
    fig_hist.add_vline(
        x=mediana, 
        line_dash="solid", 
        line_color="green", 
        annotation_text=f"Mediana: {mediana:.1f}", 
        annotation_position="top left"
    )

    fig_hist.update_layout(
        xaxis_title="Nota geral (0 a 99)",
        yaxis_title="Frequência de alunos",
        bargap=0.1,
        showlegend=False
    )

    st.plotly_chart(fig_hist, use_container_width=True)

with col_d2:
    st.write("### Estatísticas")
    st.metric("Média", f"{media:.2f}")
    st.metric("Mediana", f"{mediana:.2f}")
    st.metric("Desvio Padrão", f"{df['NT_GER'].std():.2f}")
        
st.divider()


st.header("Análise focada na UFJF")
st.markdown("Análise específica do desempenho da **Universidade Federal de Juiz de Fora** em comparação com o restante da cidade.")

df['CATEGORIA_COMPARACAO'] = df['CO_IES'].apply(lambda x: 'UFJF' if x == 586 else 'Outras IES')

df_ufjf = df[df['CO_IES'] == 576].copy()

if len(df_ufjf) > 0:
    col_u1, col_u2, col_u3 = st.columns(3)
    
    media_ufjf = df_ufjf['NT_GER'].round(2).mean()
    media_outras = df[df['CATEGORIA_COMPARACAO'] == 'Outras IES']['NT_GER'].round(2).mean()
    delta = media_ufjf - media_outras
    
    col_u1.metric("Média UFJF", f"{media_ufjf:.2f}", delta=f"{delta:.2f} acima da média da cidade")
    col_u2.metric("Alunos Avaliados (UFJF)", len(df_ufjf))
    col_u3.metric("Cursos Avaliados (UFJF)", df_ufjf['CO_CURSO'].nunique())
    
    st.markdown("""
    A análise específica da Universidade Federal de Juiz de Fora revela um desempenho forte. Responsável por uma fatia significativa da amostra (**964 alunos**), a instituição puxa a nota do município para cima. A média de **61.20** obtida pelos 15 cursos avaliados confirma a UFJF em um patamar de excelência na região.
    """)

    
    st.subheader("Ranking interno da UFJF")
    st.markdown("""
        O ranking interno da UFJF revela uma disputa acirrada no topo. O curso de **Fisioterapia** assume a liderança com média **74.8**, seguido de perto pela **Medicina** (**74.6**). É notável o domínio da área de Saúde, que ocupa 4 das 5 primeiras posições. A única exceção neste grupo é a **Engenharia Ambiental** (**70.7**), descolando-se das demais engenharias.
    """)
    
    if 'NOME_CURSO' not in df_ufjf.columns:
         df_ufjf['NOME_CURSO'] = df_ufjf['CO_GRUPO'].map(CO_GRUPO_LABELS).fillna(df_ufjf['CO_GRUPO'].astype(str))

    ranking_ufjf = df_ufjf.groupby('NOME_CURSO')['NT_GER'].agg(['mean', 'count']).round(2).reset_index()
    ranking_ufjf = ranking_ufjf.sort_values('mean', ascending=True) 

    fig_rank = px.bar(
        ranking_ufjf,
        x='mean',
        y='NOME_CURSO',
        orientation='h',
        text_auto='.1f',
        title="Média Geral dos Cursos da UFJF (ENADE 2023)",
        color='mean',
        color_continuous_scale='Reds',
        labels={
            'mean': 'Nota média',      
            'NOME_CURSO': 'Curso'       
        } 
    )
    
    fig_rank.update_layout(xaxis_title="Nota Média", yaxis_title="", height=600)
    st.plotly_chart(fig_rank, use_container_width=True)

    melhor_curso = ranking_ufjf.iloc[-1]['NOME_CURSO']
    nota_melhor = ranking_ufjf.iloc[-1]['mean']
    


    st.subheader("Raio-X da UFJF: Distribuição por Curso")
    st.markdown("""
        **A média pode causar impressões equivocadas sobre as notas.** Dizer que um curso tem média 50 pode significar que todos tiraram 50, ou que metade tirou 100 e a outra metade zero.

        Para entender a realidade das notas do exame, o gráfico abaixo trata a nota de **cada estudante da UFJF como um ponto**. Isso nos permite ver a **dispersão**: os alunos têm notas parecidas ou existe uma diferença significativa entre elas?
    """)

    ordem_cursos = df_ufjf.groupby('NOME_CURSO')['NT_GER'].median().sort_values(ascending=False).index

    fig_strip_ufjf = px.strip(
        df_ufjf,
        x="NOME_CURSO",     
        y="NT_GER",      
        color="NOME_CURSO", 
        stripmode="overlay", 
        title="Distribuição Individual de Notas por Curso (UFJF)",
        hover_data=["NT_GER"],
        labels={
            'NOME_CURSO': 'Curso do aluno',      
            'NT_GER': 'Nota do aluno'       
        }
    )

    fig_strip_ufjf.update_layout(
        xaxis_title="",
        yaxis_title="Nota Geral",
        showlegend=False, 
        height=600,       
        xaxis_tickangle=-45 
    )

    fig_strip_ufjf.update_traces(
        marker=dict(size=5, opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey')),
        jitter=0.5 
    )

    st.plotly_chart(fig_strip_ufjf, use_container_width=True)

    st.markdown("""
        A visualização expõe dois perfis de turmas muito distintos dentro da federal:

        1.  **A consistência da Saúde:**
            Cursos como **Medicina**, **Fisioterapia** e **Enfermagem** apresentam "nuvens" de pontos densas e situadas no topo do gráfico. A baixa dispersão indica turmas de performance mais homogênea, com poucos outliers. Isso pode sugerir um bom acompanhamento dentro do curso de graduação.

        2.  **A Heterogeneidade das Engenharias:**
            Em cursos como **Engenharia Elétrica** e **Controle e Automação**, vemos uma dispersão vertical maior. Embora existam alunos com notas acima da média, há uma cauda longa de alunos com notas baixas. Isso puxa a média geral para baixo e indica um desafio pedagógico maior para nivelar o conhecimento do curso.

        **Destaque:** A **Engenharia Ambiental**, diferente das outras exatas, se comporta quase como um curso de saúde: notas mais altas e consistentes neste ciclo do ENADE.
    """)