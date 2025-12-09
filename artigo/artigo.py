import random
import pandas as pd
import numpy as np
from collections import defaultdict
from datetime import datetime

# arquivo do dataset. 
NOME_DO_ARQUIVO_CSV = '/content/dataset_TSMC2014_NYC.csv' 

# Mapeamento
COLUNAS_CSV = {
    'CATEGORIA': 'venueCategory',  # Nome da coluna de categoria no CSV
    'TEMPO': 'utcTimestamp',       # Nome da coluna de data/hora no CSV
    'USUARIO': 'userId'            # Nome da coluna de ID do usuário
}

# 1. CARREGAMENTO E PROCESSAMENTO REAL DOS DADOS
def processar_timestamp(data_string):
    """
    Converte datas reais (ex: 'Tue Apr 03 18:00:09 +0000 2012') 
    para 'Manhã', 'Tarde' ou 'Noite'.
    """
    try:
        # Tenta converter string para objeto de data. 
        dt = pd.to_datetime(data_string)
        hora = dt.hour
        
        if 5 <= hora < 12:
            return 'Manhã'
        elif 12 <= hora < 18:
            return 'Tarde'
        else:
            return 'Noite'
    except:
        # Se falhar, retorna um aleatório para não quebrar o código
        return random.choice(['Manhã', 'Tarde', 'Noite'])

def carregar_dados_reais(caminho_arquivo):
    print(f"--- 1. CARREGANDO ARQUIVO: {caminho_arquivo} ---")
    
    try:
        # Carrega o CSV 
        df = pd.read_csv(caminho_arquivo)
        print(f"Sucesso! Arquivo carregado com {len(df)} linhas.")
        
        # Seleciona e renomeia apenas as colunas que importam
        df_limpo = pd.DataFrame()
        df_limpo['User_ID'] = df[COLUNAS_CSV['USUARIO']]
        df_limpo['Venue_Category'] = df[COLUNAS_CSV['CATEGORIA']]
        
        print("Processando horários (convertendo datas para Manhã/Tarde/Noite)...")
        # Aplica a conversão de tempo na coluna original
        df_limpo['Time_OfDay'] = df[COLUNAS_CSV['TEMPO']].apply(processar_timestamp)
        
        # Remove linhas vazias (limpeza básica)
        df_limpo = df_limpo.dropna()
        
        print("\n--- AMOSTRA DOS DADOS PROCESSADOS ---")
        print(df_limpo.head())
        print("-------------------------------------\n")
        
        return df_limpo

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{caminho_arquivo}' não foi encontrado.")
        print("Certifique-se de que o nome está correto e o arquivo está na mesma pasta.")
        exit()
    except KeyError as e:
        print(f"ERRO DE COLUNA: O código não achou a coluna {e} no CSV.")
        print("Verifique a variável 'COLUNAS_CSV' no início do código.")
        exit()

# 2. O AMBIENTE BASEADO EM DADOS
class DataDrivenEnvironment:
    def __init__(self, dataframe):
        self.df = dataframe
        # Pega as categorias únicas (ex: 200 tipos de locais diferentes)
        self.locations = list(dataframe['Venue_Category'].unique())
        
        # Ações possíveis do NPC
        self.actions = ["Oferecer Missão de Combate", "Oferecer Tour Histórico", "Oferecer Item de Energia"]
        
        # CÁLCULO DE HOTSPOTS (CLUSTERING SIMPLIFICADO)
        print("--- 2. ANALISANDO O AMBIENTE (HOTSPOTS) ---")
        counts = dataframe['Venue_Category'].value_counts(normalize=True)
        self.popularity = counts.to_dict()
        
        # Mostrar os 5 locais mais populares (Top 5 Hotspots)
        print("Top 5 Locais Mais Populares (Hotspots) identificados nos dados:")
        for loc, score in counts.head(5).items():
            print(f"   -> {loc}: {score*100:.2f}% dos check-ins")
        print("-------------------------------------------\n")

    def get_random_sample(self):
        sample = self.df.sample(1).iloc[0]
        return {
            'User_ID': sample['User_ID'],
            'Location': sample['Venue_Category'],
            'Time': sample['Time_OfDay']
        }

    def get_reward(self, state, action):
        location = state['Location']
        reward = -1 

        # --- Lógica Semântica (Simplificada para Categorias Comuns) ---
        # MUITAS categorias => palavras-chave
        loc_lower = str(location).lower()

        # 1. Cultura/História (Museum, Art, History, Monument)
        if any(x in loc_lower for x in ['museum', 'art', 'history', 'library', 'monument', 'park']):
            if action == "Oferecer Tour Histórico":
                reward += 10
            elif action == "Oferecer Missão de Combate":
                reward -= 5
        
        # 2. Esporte/Ação (Gym, Stadium, Field, Fitness)
        elif any(x in loc_lower for x in ['gym', 'stadium', 'fitness', 'sport', 'soccer']):
            if action == "Oferecer Missão de Combate":
                reward += 10
            elif action == "Oferecer Tour Histórico":
                reward -= 5

        # 3. Comida/Descanso (Cafe, Restaurant, Coffee, Shop, Store)
        elif any(x in loc_lower for x in ['cafe', 'coffee', 'food', 'restaurant', 'shop', 'store']):
            if action == "Oferecer Item de Energia":
                reward += 8
            else:
                reward += 0

        # Bônus de Hotspot
        if self.popularity.get(location, 0) > 0.01: # Se tiver > 1% dos checkins totais
            reward += 2

        return reward

# 3. O AGENTE Q-LEARNING
class QLearningAgent:
    def __init__(self, actions):
        self.actions = actions
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1

    def get_state_key(self, state):
        return f"{state['Location']}_{state['Time']}"

    def choose_action(self, state):
        state_key = self.get_state_key(state)
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        if not self.q_table[state_key]:
            return random.choice(self.actions)
        return max(self.q_table[state_key], key=self.q_table[state_key].get)

    def learn(self, state, action, reward, next_state):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state_key][action] = new_q

# 4. EXECUÇÃO
def run_real_data_simulation():
    # 1. Carregar dados REAIS
    df_foursquare = carregar_dados_reais(NOME_DO_ARQUIVO_CSV)
    
    # 2. Inicializar ambiente
    env = DataDrivenEnvironment(df_foursquare)
    agent = QLearningAgent(env.actions)
    
    print("--- 3. INICIANDO TREINAMENTO DO AGENTE ---")
    
    # CSV muito grande, deixei só 2 epocas.
    if len(df_foursquare) > 50000:
        epochs = 2
    else:
        epochs = 30
        
    total_interations = len(df_foursquare) * epochs
    print(f"Treinando por {epochs} épocas (Total de interações: {total_interations})")
    
    # Loop de Treinamento com Barra de Progresso visual
    for i in range(total_interations):
        state = env.get_random_sample()
        action = agent.choose_action(state)
        reward = env.get_reward(state, action)
        next_state = env.get_random_sample()
        agent.learn(state, action, reward, next_state)
        
        # Print de progresso a cada 10%
        if i > 0 and i % (total_interations // 10) == 0:
            progresso = (i / total_interations) * 100
            print(f"   Progresso: {progresso:.0f}% concluído... (Última recompensa: {reward})")

    print("--- TREINAMENTO CONCLUÍDO ---\n")
    
    print("--- 4. RESULTADOS FINAIS: POLÍTICA APRENDIDA ---")
    print("(Amostrando 10 locais aleatórios do dataset para ver o que o NPC fará)")
    
    locais_teste = random.sample(env.locations, min(10, len(env.locations)))
    
    for loc in locais_teste:
        test_state = {'Location': loc, 'Time': 'Tarde'}
        state_key = agent.get_state_key(test_state)
        
        if agent.q_table[state_key]:
            best_action = max(agent.q_table[state_key], key=agent.q_table[state_key].get)
            valor = agent.q_table[state_key][best_action]
            print(f"Local: '{loc[:25]:<25}' -> NPC Escolhe: {best_action:<25} (Confiança Q: {valor:.2f})")
        else:
            print(f"Local: '{loc[:25]:<25}' -> (Dados insuficientes para aprender)")

if __name__ == "__main__":
    run_real_data_simulation()