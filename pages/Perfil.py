import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from pywaffle import Waffle
import numpy as np
from tratamento_dados import tratar_dados_gerais, relacionar_idh_estados_nota

st.set_page_config(
    page_title="Prova Prática CAEd - ENADE 2023",
    page_icon="🎓",
    layout="wide"
)

try:
   
    df = tratar_dados_gerais() 

    st.title("Breve análise do perfil de gênero e raça dos inscritos no ENADE 2023")
    st.markdown("""
    Esta seção vai além da demografia básica. Aqui, investigamos hipóteses sobre **quem são** os estudantes e **como o contexto regional** (IDH) pode influenciar o desempenho acadêmico.
    """)
    
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    col_k1.metric("Total Estudantes", f"{len(df):,.0f}".replace(",", "."))
    col_k2.metric("Média de Idade", f"{df['NU_IDADE'].mean():.0f} anos")
    perc_fem = (len(df[df['Desc_Genero'] == 'Feminino']) / len(df)) * 100
    raca_predominante = df['Desc_Raca'].mode()[0]
    col_k3.metric("Mulheres", f"{perc_fem:.1f}%")
    col_k4.metric("Raça predominante:", f"{raca_predominante}")
    

    st.divider()


    st.header("Um mosaico racial")
    st.markdown("""
    """)

    raca_counts = df['Desc_Raca'].value_counts().reset_index()
    raca_counts.columns = ['Raça', 'Total']
    total_geral = raca_counts['Total'].sum()
    raca_counts['Porcentagem'] = (raca_counts['Total'] / total_geral) * 100
    
    cores_map = {
        'Branca': '#468996', 'Parda': '#00B050', 'Preta': '#FF555E', 
        'Amarela': '#FFC000', 'Indígena': '#C65911'
    }
    
    data_waffle = dict(zip(raca_counts['Raça'], raca_counts['Porcentagem']))
    colors_list = [cores_map.get(r, '#999999') for r in data_waffle.keys()]

    fig_waffle = plt.figure(
        FigureClass=Waffle,
        rows=5, columns=20,
        values=data_waffle, colors=colors_list,
        rounding_rule='nearest',
        legend={'loc': 'upper right', 'bbox_to_anchor': (1, 1), 'framealpha': 0},
        figsize=(12, 5),
        block_arranging_style='snake'
    )
    plt.legend().remove() 
    st.pyplot(fig_waffle)

    cols_leg = st.columns(len(raca_counts))
    for idx, (index, row) in enumerate(raca_counts.iterrows()):
        cor = cores_map.get(row['Raça'], '#333333')
        with cols_leg[idx]:
            st.markdown(f"<span style='color:{cor}'>■</span> **{row['Raça']}**: {row['Porcentagem']:.1f}%", unsafe_allow_html=True)

    st.divider()


    st.header("Distribuição de gênero por região")
    st.markdown("""
    **Hipótese:** A distribuição de gênero é uniforme pelo país, ou certas regiões (como Norte ou Nordeste) 
    possuem maior predominância feminina no ensino superior?
    """)

    df_regiao_sexo = df.groupby(['Desc_Regiao_Curso', 'Desc_Genero']).size().reset_index(name='Contagem')
    
    fig_regiao = px.bar(
        df_regiao_sexo,
        x="Desc_Regiao_Curso",
        y="Contagem",
        color="Desc_Genero",
        barmode="group",
        title="Comparativo Regional: Homens vs. Mulheres",
        color_discrete_map={'Feminino': '#E74C3C', 'Masculino': '#3498DB'},
        text_auto='.2s'
    )
    fig_regiao.update_layout(height=500, xaxis_title="Região", yaxis_title="Número de Estudantes")
    st.plotly_chart(fig_regiao, use_container_width=True)
    

    st.divider()
    st.header("5. O 'Gender Gap': Quais cursos são dominados por homens ou mulheres?")
    st.markdown("""
    **Análise de Segregação:** Historicamente, áreas de **Saúde e Educação** atraem mais mulheres, 
    enquanto **Engenharias e Tecnologia** atraem mais homens. Os dados confirmam esse padrão no Brasil?
    """)

    df_curso_sexo = df.groupby(['NOME_CURSO', 'Desc_Genero']).size().reset_index(name='Contagem')
    
    df_total_curso = df_curso_sexo.groupby('NOME_CURSO')['Contagem'].transform('sum')
    df_curso_sexo['Percentual'] = (df_curso_sexo['Contagem'] / df_total_curso) * 100
    
    cursos_relevantes = df['NOME_CURSO'].value_counts()
    cursos_relevantes = cursos_relevantes[cursos_relevantes > 1].index.tolist()
    
    df_gap = df_curso_sexo[df_curso_sexo['NOME_CURSO'].isin(cursos_relevantes)].copy()

    pivo = df_gap.pivot(index='NOME_CURSO', columns='Desc_Genero', values='Percentual').fillna(0)
    
    if 'Feminino' in pivo.columns:
        ordem_cursos = pivo.sort_values('Feminino', ascending=True).index.tolist()
    else:
        ordem_cursos = pivo.index.tolist()

    fig_gap = px.bar(
        df_gap,
        y="NOME_CURSO",
        x="Percentual",
        color="Desc_Genero",
        orientation='h', 
        title="Divisão de Gênero por Curso (Ordenado por Presença Feminina)",
        color_discrete_map={'Feminino': '#E74C3C', 'Masculino': '#3498DB'},
        text_auto='.1f',
        category_orders={"NOME_CURSO": ordem_cursos} 
    )

    fig_gap.update_layout(
        height=800,
        xaxis_title="% do Curso",
        yaxis_title="",
        barmode='relative', 
        xaxis_range=[0, 100]
    )
    
    fig_gap.add_vline(x=50, line_dash="dash", line_color="gray", annotation_text="Equilíbrio (50%)")

    st.plotly_chart(fig_gap, use_container_width=True)

    try:
        top_fem = ordem_cursos[-1] # 
        perc_top_fem = pivo.loc[top_fem, 'Feminino']
        
        top_masc = ordem_cursos[0]
        perc_top_masc = pivo.loc[top_masc, 'Masculino'] if 'Masculino' in pivo.columns else 0

        st.info(f"""
        💡 **Extremos do Gráfico:**
        * O curso com maior presença feminina é **{top_fem}** ({perc_top_fem:.1f}% mulheres).
        * O curso com maior presença masculina é **{top_masc}** ({perc_top_masc:.1f}% homens).
        * A linha tracejada no centro marca o equilíbrio perfeito. Quanto mais longe dela, maior a segregação.
        """)
    except:
        pass

except Exception as e:
    st.error(f"Erro ao carregar os dados ou gerar gráficos. Verifique se as funções estão retornando os DataFrames corretamente: {e}")