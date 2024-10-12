# Importação das bibliotecas necessárias
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Definindo uma nova paleta de cores
colors = ['#FF6347', '#FFD700', '#90EE90', '#1E90FF']  # Tomate, Dourado, Verde Claro, Azul

# Configuração da página do Streamlit para tela inteira
st.set_page_config(layout="wide")
st.title('Análise de Custos e Características de Imóveis por Cidade')

# Função para carregar os dados com cache para melhorar a performance
@st.cache_data
def load_data(nrows):
    DATA_URL = "houses_to_rent_v2.csv"
    data = pd.read_csv(DATA_URL, nrows=nrows)
    # Renomeia as colunas para letras minúsculas
    data.columns = data.columns.str.lower()
    return data

# Carregando os dados e informando o usuário
data_load_state = st.text('Carregando dados...')
data = load_data(10000)
data_load_state.text("")

# Carregando o dataframe completo para operações subsequentes
df = data.copy()

# Opção para mostrar os dados brutos
if st.checkbox('Mostrar Dados Brutos'):
    st.subheader('Dados Brutos')
    st.write(df)

# Verificação e ordenação dos dados pela coluna 'total (R$)'
if 'total (r$)' in df.columns:
    df = df.sort_values(by="total (r$)")
else:
    st.error("A coluna 'total (R$)' não foi encontrada no DataFrame.")

# Layout das colunas para disposição dos elementos na tela
col1, col2, col3, col4, col5 = st.columns(5)
col6, col7 = st.columns(2)
col8, col9, col10 = st.columns(3)
col11 = st.columns(1)[0]

# --- Cálculo e Exibição das Métricas ---

# Criando a coluna 'custo_total' somando as principais despesas
df['custo_total'] = df[['hoa (r$)', 'rent amount (r$)', 'property tax (r$)', 'fire insurance (r$)']].sum(axis=1)

# Função para formatar números no padrão brasileiro (R$ e substituição de pontos por vírgulas)
def formatar_numero(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Cálculo e exibição do Custo Total Médio
custo_total_medio = df['custo_total'].mean().round(2)
col1.metric(label="Custo Total Médio", value=formatar_numero(custo_total_medio))

# Cálculo e exibição da Média de Aluguel por m²
df['aluguel_m2'] = df['rent amount (r$)'] / df['area']
media_aluguel_m2 = df['aluguel_m2'].mean().round(2)
col2.metric(label="Média de Aluguel por m²", value=f"{formatar_numero(media_aluguel_m2)}/m²")

# Cálculo e exibição do Percentual de Imóveis que Aceitam Animais
imoveis_aceitam_animais = df[df['animal'] == 'acept'].shape[0]
total_imoveis = df.shape[0]
percentual_aceitam_animais = (imoveis_aceitam_animais / total_imoveis) * 100
col3.metric(label="Imóveis que Aceitam Animais (%)", value=f"{percentual_aceitam_animais:.2f}%")

# Cálculo e exibição do Percentual de Imposto sobre o Aluguel Total
imposto_medio_aluguel = (df['property tax (r$)'] / df['rent amount (r$)']).mean() * 100
col4.metric(label="% Imposto / Aluguel Total", value=f"{imposto_medio_aluguel:.2f}%")

# Exibição da Quantidade Total de Imóveis
col5.metric(label="Quantidade Total de Imóveis", value=f"{total_imoveis}")

# --- Visualizações Gráficas ---

# Gráfico 1: Gráfico de Pizza - Composição do Custo Total por Componente
# Mapeamento dos componentes para nomes mais amigáveis
componentes_portugues = {
    'hoa (r$)': 'Condomínio',
    'rent amount (r$)': 'Aluguel',
    'property tax (r$)': 'Imposto',
    'fire insurance (r$)': 'Seguro Incêndio'
}

# Cálculo da média dos componentes do custo
custo_composicao = df[['hoa (r$)', 'rent amount (r$)', 'property tax (r$)', 'fire insurance (r$)']].mean().reset_index()
custo_composicao.columns = ['Componente', 'Valor']
custo_composicao['Componente'] = custo_composicao['Componente'].map(componentes_portugues)

# Criação do Gráfico de Pizza para mostrar a porcentagem de cada componente no custo total
fig_pizza_custo = px.pie(
    custo_composicao,
    names='Componente',
    values='Valor',
    title='Composição Média do Custo Total',
    color_discrete_sequence=colors
)
col6.plotly_chart(fig_pizza_custo, use_container_width=True)

# Gráfico 2: Gráfico de Linha - Evolução do Aluguel Médio por Cidade
# Cálculo da média de aluguel por cidade
city_stats = df.groupby("city")['rent amount (r$)'].mean().reset_index()
city_stats.columns = ["Cidade", "Média de Aluguel"]
city_stats = city_stats.sort_values("Média de Aluguel", ascending=False)

# Criação do Gráfico de Linha para visualizar a comparação de aluguel entre as cidades
fig_linha_aluguel = px.line(
    city_stats,
    x="Cidade",
    y="Média de Aluguel",
    title="Média de Aluguel por Cidade",
    markers=True,
    color_discrete_sequence=[colors[1]]
)
col7.plotly_chart(fig_linha_aluguel, use_container_width=True)

# Gráfico 3: Gráfico de Donut - Percentual de Imóveis que Aceitam Animais
# Cálculo dos percentuais de imóveis que aceitam e não aceitam animais
animais_contagem = df['animal'].value_counts().reset_index()
animais_contagem.columns = ['Aceita Animais', 'Quantidade']
animais_contagem['Aceita Animais'] = animais_contagem['Aceita Animais'].replace(
    {'acept': 'Aceita', 'not acept': 'Não Aceita'}
)

# Criação do Gráfico de Donut para representar a proporção de imóveis pet-friendly
fig_donut_animais = px.pie(
    animais_contagem,
    names='Aceita Animais',
    values='Quantidade',
    hole=0.5,
    title='Distribuição de Imóveis que Aceitam Animais',
    color_discrete_sequence=colors[2:4]
)
col8.plotly_chart(fig_donut_animais, use_container_width=True)

# Gráfico 4: Gráfico de Área - R$/m² por Cluster de Tamanho
# Definindo clusters de tamanho dos imóveis
bins = [0, 50, 100, 150, 200, df['area'].max()]
labels = ['0-50m²', '51-100m²', '101-150m²', '151-200m²', '200m²+']
df['tamanho_cluster'] = pd.cut(df['area'], bins=bins, labels=labels)

# Cálculo da média de aluguel por m² para cada cluster de tamanho
aluguel_m2_cluster = df.groupby('tamanho_cluster')['aluguel_m2'].mean().reset_index()

# Criação do Gráfico de Área para visualizar a variação do preço do aluguel por m² conforme o tamanho do imóvel
fig_area_aluguel = px.area(
    aluguel_m2_cluster,
    x='tamanho_cluster',
    y='aluguel_m2',
    title='Média do Aluguel por m² por Tamanho de Imóvel',
    color_discrete_sequence=[colors[0]]
)
col9.plotly_chart(fig_area_aluguel, use_container_width=True)

# Gráfico 5: Gráfico de Barras Horizontais - Imposto Médio por Cidade
# Cálculo do imposto médio por cidade
imposto_medio_cidade = df.groupby('city')['property tax (r$)'].mean().reset_index()
imposto_medio_cidade.columns = ['Cidade', 'Imposto Médio']
imposto_medio_cidade = imposto_medio_cidade.sort_values('Imposto Médio')

# Criação do Gráfico de Barras Horizontais para comparar o imposto médio entre as cidades
fig_bar_imposto = px.bar(
    imposto_medio_cidade,
    x='Imposto Médio',
    y='Cidade',
    orientation='h',
    title='Imposto Médio por Cidade',
    color_discrete_sequence=[colors[3]]
)
col10.plotly_chart(fig_bar_imposto, use_container_width=True)

# Gráfico 6: Gráfico de Boxplot - Distribuição do Aluguel por Cidade
# Criação do Gráfico de Boxplot para visualizar a distribuição dos valores de aluguel em cada cidade
fig_boxplot_aluguel = px.box(
    df,
    x='city',
    y='rent amount (r$)',
    title='Distribuição do Aluguel por Cidade',
    color='city',
    color_discrete_sequence=colors
)
col11.plotly_chart(fig_boxplot_aluguel, use_container_width=True)

# --- Mapa Interativo ---

# Função para adicionar coordenadas de latitude e longitude com base na cidade
def add_coordinates(df):
    coordinates = {
        "belo horizonte": (-19.9191, -43.9386),
        "rio de janeiro": (-22.9068, -43.1729),
        "são paulo": (-23.5505, -46.6333),
        "porto alegre": (-30.0346, -51.2177),
        "campinas": (-22.9056, -47.0608),
    }
    
    df['latitude'] = np.nan
    df['longitude'] = np.nan
    
    # Atribuição das coordenadas a cada cidade
    for city, (lat, lon) in coordinates.items():
        df.loc[df['city'].str.lower() == city, ['latitude', 'longitude']] = lat, lon

    return df

# Adicionando as coordenadas ao dataframe
df = add_coordinates(df)

# Cálculo da média de aluguel por cidade para fins de filtragem
city_stats = df.groupby("city").agg(media_aluguel=('rent amount (r$)', 'mean')).reset_index()
min_media_aluguel = int(city_stats["media_aluguel"].min())
max_media_aluguel = int(city_stats["media_aluguel"].max())

# Criação de um slider para o usuário filtrar as cidades pela média de aluguel
min_slider, max_slider = st.slider(
    "Selecione o intervalo de média de aluguel (R$):",
    min_value=min_media_aluguel,
    max_value=max_media_aluguel,
    value=(min_media_aluguel, max_media_aluguel)
)

# Filtrando as cidades com base no intervalo selecionado
filtered_cities = city_stats[
    (city_stats["media_aluguel"] >= min_slider) & 
    (city_stats["media_aluguel"] <= max_slider)
]
filtered_data = df[df["city"].isin(filtered_cities["city"])]

# Exibição do mapa com os imóveis das cidades filtradas
if 'latitude' in filtered_data.columns and 'longitude' in filtered_data.columns:
    st.subheader('Mapa de Imóveis por Média de Aluguel')
    st.map(filtered_data[['latitude', 'longitude']])
else:
    st.error("O DataFrame deve conter colunas de latitude e longitude nomeadas 'latitude' e 'longitude'.")