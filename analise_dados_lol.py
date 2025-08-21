#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da página
st.set_page_config(
    page_title="Dashboard LoL",
    page_icon="🎮",
    layout="wide"
)

# Título do dashboard
st.title("🎮 Análise de League of Legends")

# Carregar dados
@st.cache_data
def carregar_dados():
    dados = pd.read_csv('LeaguePlayerStats.csv', sep=",")
    
    # dicionário de tradução
    traducao_colunas = {
        "summonerName": "nomeInvocador",
        "summonerLevel": "nivelInvocador",
        "rank": "classificacao",
        "wins": "vitorias",
        "losses": "derrotas",
        "winRate": "taxaVitoria",
        "kills": "abates",
        "deaths": "mortes",
        "assists": "assistencias",
        "prefLane": "rotaPreferida",
        "campsKilled": "monstrosSelvaMortos",
        "minionsKilled": "tropasAbatidas",
        "goldEarned": "ouroObtido",
        "turretTakedowns": "torresDestruidas",
        "visionScore": "pontuacaoVisao",
        "dragonKills": "dragoesAbatidos",
        "longestTimeSpentLiving": "tempoMaximoVivo",
        "totalDamageDealt": "danoTotalCausado",
        "totalDamageTaken": "danoTotalRecebido",
        "gameDuration": "duracaoPartida",
        "gameStart": "inicioPartida"
    }
    
    dados = dados.rename(columns=traducao_colunas)
    
    # Retirando duplicadas de nomes de invocadores
    contagem_nomes = dados['nomeInvocador'].value_counts()
    nomes_duplicados = contagem_nomes[contagem_nomes > 1].index.tolist()
    dados = dados.query("nomeInvocador not in @nomes_duplicados")
    
    # Removendo as rotas preferidas que são NONE
    dados = dados.query("rotaPreferida != 'NONE'")
    
    # Calcular KDA
    dados['KDA'] = (dados['abates'] + dados['assistencias']) / dados['mortes'].replace(0, 1)
    
    return dados

dados = carregar_dados()

# Sidebar com filtros
st.sidebar.header("🔧 Filtros")
rotas_selecionadas = st.sidebar.multiselect(
    "Selecione as Rotas:",
    options=dados['rotaPreferida'].unique(),
    default=dados['rotaPreferida'].unique()
)

ranks_selecionados = st.sidebar.multiselect(
    "Selecione os Ranks:",
    options=dados['classificacao'].unique(),
    default=dados['classificacao'].unique()
)

# Filtrar dados
dados_filtrados = dados[
    (dados['rotaPreferida'].isin(rotas_selecionadas)) & 
    (dados['classificacao'].isin(ranks_selecionados))
]

# Métricas principais
col1, col2, col3= st.columns(3)
with col1:
    st.metric("Total de Jogadores", len(dados_filtrados))
with col2:
    st.metric("Win Rate Médio", f"{dados_filtrados['taxaVitoria'].mean():.2%}")
with col3:
    st.metric("KDA Médio", f"{dados_filtrados['KDA'].mean():.2f}")

# Abas para organização
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Win Rate", "👥 Distribuição", "⚔️ Dano", 
    "👀 Visão", "🎯 Farm"
])

with tab1:
    st.header("Análise de Taxa de Vitória")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Boxplot Win Rate por Rank
        
        media_por_rank = dados.groupby('rotaPreferida')['taxaVitoria'].mean().sort_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        media_por_rank.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Média da Taxa de Vitória por Rota Preferida')
        ax.set_xlabel('Rota Preferida')
        ax.set_ylabel('Média da Taxa de Vitória')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

        
    
    with col2:
        # Média Win Rate por Rank
        ordem_ranks = ['IRON','BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER']
        dados_filtrados['classificacao'] = pd.Categorical(
            dados_filtrados['classificacao'],
            categories=ordem_ranks,
            ordered=True
        )
        
        media_por_rank = dados_filtrados.groupby('classificacao')['taxaVitoria'].mean().sort_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        media_por_rank.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Média da Taxa de Vitória por Classificação')
        ax.set_xlabel('Classificação')
        ax.set_ylabel('Média da Taxa de Vitória')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
    
    # Top 100 vitórias e derrotas
    col1, col2 = st.columns(2)
    
    with col1:
        top_100_vitoria = dados_filtrados.nlargest(100, 'taxaVitoria')
        st.write("**Top 100 - Maior Win Rate:**")
        st.write(f"Rank mais comum: {top_100_vitoria['classificacao'].value_counts().idxmax()}")
        st.write(f"Rota mais comum: {top_100_vitoria['rotaPreferida'].value_counts().idxmax()}")
    
    with col2:
        top_100_derrota = dados_filtrados.nsmallest(100, 'taxaVitoria')
        st.write("**Top 100 - Menor Win Rate:**")
        st.write(f"Rank mais comum: {top_100_derrota['classificacao'].value_counts().idxmax()}")
        st.write(f"Rota mais comum: {top_100_derrota['rotaPreferida'].value_counts().idxmax()}")

with tab2:
    st.header("Distribuição de Jogadores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Contagem por Rank
        contagem_por_rank = dados_filtrados['classificacao'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(contagem_por_rank.index, contagem_por_rank.values, color='lightblue')
        ax.set_title('Contagem de Jogadores por Classificação')
        ax.set_xlabel('Classificação')
        ax.set_ylabel('Número de Jogadores')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
    
    with col2:
        # Contagem por Rota
        contagem_por_rota = dados_filtrados['rotaPreferida'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(contagem_por_rota.index, contagem_por_rota.values, color='lightgreen')
        ax.set_title('Contagem de Jogadores por Rota Preferida')
        ax.set_xlabel('Rota Preferida')
        ax.set_ylabel('Número de Jogadores')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

with tab3:
    st.header("Análise de Dano")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Dano por Rota
        media_por_rota = dados_filtrados.groupby('rotaPreferida')['danoTotalCausado'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        media_por_rota.plot(kind='bar', color='lightgreen', ax=ax)
        ax.set_title('Média do Dano Total Causado por Rota')
        ax.set_xlabel('Rota de Jogo')
        ax.set_ylabel('Média do Dano Total Causado')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
    
    with col2:
        # Heatmap Dano por Rota e Rank
        tabela_media = dados_filtrados.groupby(['rotaPreferida', 'classificacao'])['danoTotalCausado'].mean().unstack()
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(tabela_media.round(2), 
                    annot=True, 
                    fmt='.0f', 
                    cmap='Reds', 
                    linewidths=0.5,
                    cbar_kws={'label': 'Dano Médio Causado'},
                    ax=ax)
        ax.set_title('Dano Médio por Rota e Rank', fontsize=16, pad=20)
        ax.set_xlabel('Rank', fontsize=12)
        ax.set_ylabel('Rota Preferida', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

with tab4:
    st.header("Análise de Visão")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visão por Rota
        media_visao_por_rota = dados_filtrados.groupby('rotaPreferida')['pontuacaoVisao'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        media_visao_por_rota.plot(kind='bar', color='lightcoral', ax=ax)
        ax.set_title('Média da Pontuação de Visão por Rota')
        ax.set_xlabel('Rota de Jogo')
        ax.set_ylabel('Média da Pontuação de Visão')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        st.write("**Observação:** Aqui vemos um valor na pontuação de visão muito maior na rota de suporte em relação as demais lanes, o que já é esperado, visto que no League of Legends os suportes são os que mais limpam as wards "
        "(sentinelas que dão visão em uma determinada área do mapa), já que é o principal responsável do jogo por isso.")
    
    with col2:
        # Visão por Rank
        media_visao_por_rank = dados_filtrados.groupby('classificacao')['pontuacaoVisao'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        media_visao_por_rank.plot(kind='bar', color='lightcoral', ax=ax)
        ax.set_title('Média da Pontuação de Visão por Rank')
        ax.set_xlabel('Rank')
        ax.set_ylabel('Média da Pontuação de Visão')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

with tab5:
    st.header("Análise de Farm (Tropas Abatidas)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Farm por Rota
        media_por_rota = dados_filtrados.groupby('rotaPreferida')['tropasAbatidas'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        media_por_rota.plot(kind='bar', color='lightcoral', ax=ax)
        ax.set_title('Média de Minions Abatidos por Rota')
        ax.set_xlabel('Rota Preferida')
        ax.set_ylabel('Média de Minions Abatidos')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        st.write("**Observação:** O farm é uma métrica importante para medir a eficiência do jogador em coletar recursos durante a partida.")
    
    with col2:
        # Farm por Rank
        media_por_classificacao = dados_filtrados.groupby('classificacao')['tropasAbatidas'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        media_por_classificacao.plot(kind='bar', color='lightcoral', ax=ax)
        ax.set_title('Média de Tropas Abatidas por Classificação')
        ax.set_xlabel('Classificação')
        ax.set_ylabel('Média de Tropas Abatidas')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        st.write(" **Observação:** Aqui, é possivel notar que o rank Iron é o que possui menor pontuação de visão, por ser o menor rank do jogo e muitas vezes os jogadores se preocupam pouco com essa questão, é comum que nesse rank a limpeza de sentinelas seja menor do que no rank mais elevados, então algo para que " \
        "jogadores de ranks inferiores poderiam fazer para melhorar seu rank é se preocupar com a pontuação de visão dentro das partidas")

# Rodapé
st.markdown("---")
st.caption("Dashboard criado com Streamlit - Análise de dados de League of Legends")