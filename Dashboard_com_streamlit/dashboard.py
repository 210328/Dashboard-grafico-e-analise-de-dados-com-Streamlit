import pandas as pd
import plotly.express as px
import streamlit as st
import pycountry as pc

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📈",
    layout='wide'
)

df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# Barra lateral(filtros)
st.sidebar.header("Filtros")

# Filtro por ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro por Senioridade
senioridade_disponiveis = sorted(df['senioridade'].unique())
senioridade_selecionados = st.sidebar.multiselect("Senioridade", senioridade_disponiveis, default=senioridade_disponiveis)

# Filtro por Tipo de Contrato
contrato_disponiveis = sorted(df['contrato'].unique())
contrato_selecionados = st.sidebar.multiselect("Tipo de Contrato", contrato_disponiveis, default=contrato_disponiveis)

# Filtro por Tamanho da Empresa
tamanho_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanho_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanho_disponiveis, default=tamanho_disponiveis)

# Filtro do DataFrame
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridade_selecionados)) &
    (df['contrato'].isin(contrato_selecionados)) &
    (df['tamanho_empresa'].isin(tamanho_selecionados))
]

st.title("Dashboard de Salários na Área de Dados")
st.markdown("Explore os dados de salários na área de dados com filtros interativos.")

# Métricas Principais
st.subheader("Métricas Principais")

if not df_filtrado.empty:
    salario_medio = df_filtrado["usd"].mean()
    salario_maximo = df_filtrado["usd"].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""
    
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio (USD)", f"${salario_medio:,.2f}")
col2.metric("Salário Máximo (USD)", f"${salario_maximo:,.2f}")
col3.metric("Total de Registros", total_registros)  
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

# Analise Visuais com Plotly
st.subheader("Análise Visual")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')["usd"].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 Cargos com Maior Salário Médio (USD)',
            labels={'usd': 'Salário Médio (USD)', 'cargo': 'Cargo'}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)  
    else:
        st.warning("Nenhum dado disponível para o gráfico de Cargos.")    

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição dos Salários (USD)',
            labels={'usd': 'Salário (USD)', 'count': ''}, 
        )  
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para o gráfico de Distribuição de Salários.")
    
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['Tipo de Trabalho', 'Contagem']
        grafico_remoto = px.pie(
            remoto_contagem, 
            names='Tipo de Trabalho', 
            values='Contagem', 
            title='Distribuição de Trabalho Remoto', 
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para o gráfico de Trabalho Remoto.")
        
# Funçao para converter ISO-2 para ISO-3
def iso2_to_iso3(code):
    try:
        return pc.countries.get(alpha_2=code).alpha_3
    except:
        return None

# Criar coluna com codigo ISO-3 
df_filtrado['residencia_iso3'] = df_filtrado['residencia'].apply(iso2_to_iso3)

with col_graf4:
    if not df_filtrado.empty:  
        # Calcular media salarial por país ISO-3
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        
        # Gerar gráfico de mapa
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale="rdylgn",
            title='Salário Médio de Data Scientists por País',
            labels={'usd': 'Salário Médio (USD)', 'residencia_iso3': 'País'}
        )
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para o gráfico de Salário Médio por País.")
        
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)



        
       
        
