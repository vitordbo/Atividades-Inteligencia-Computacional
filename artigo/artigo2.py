import random
import pandas as pd
import numpy as np
from collections import defaultdict
from datetime import datetime

NOME_DO_ARQUIVO_CSV = 'dataset_TSMC2014_NYC.csv' 

# --- CONFIGURAÇÃO DE VELOCIDADE ---
# True = Carrega só 10.000 linhas 
# False = Carrega tudo 
MODO_TESTE_RAPIDO = False 

COLUNAS_CSV = {
    'CATEGORIA': 'venueCategory', 
    'TEMPO': 'utcTimestamp',     
    'USUARIO': 'userId'         
}

# 1. CARREGAMENTO DOS DADOS 
def processar_timestamp(data_string):
    try:
        dt = pd.to_datetime(data_string)
        hora = dt.hour
        if 5 <= hora < 12: return 'Manhã'
        elif 12 <= hora < 18: return 'Tarde'
        else: return 'Noite'
    except:
        return random.choice(['Manhã', 'Tarde', 'Noite'])

def carregar_dados_reais(caminho_arquivo):
    print(f"--- 1. CARREGANDO ARQUIVO: {caminho_arquivo} ---")
    
    try:
        if MODO_TESTE_RAPIDO:
            print(">>> MODO RÁPIDO ATIVADO: Carregando apenas 10.000 linhas para teste <<<")
            df = pd.read_csv(caminho_arquivo, nrows=10000) # LÊ SÓ O COMEÇO
        else:
            print(">>> MODO COMPLETO: Carregando base inteira <<<")
            df = pd.read_csv(caminho_arquivo)
            
        print(f"Sucesso! Carregado: {len(df)} linhas.")
        
        df_limpo = pd.DataFrame()
        df_limpo['User_ID'] = df[COLUNAS_CSV['USUARIO']]
        df_limpo['Venue_Category'] = df[COLUNAS_CSV['CATEGORIA']]
        
        print("Processando horários...")
        df_limpo['Time_OfDay'] = df[COLUNAS_CSV['TEMPO']].apply(processar_timestamp)
        df_limpo = df_limpo.dropna()
        
        return df_limpo

    except FileNotFoundError:
        print("ERRO: Arquivo não encontrado."); exit()
    except KeyError as e:
        print(f"ERRO DE COLUNA: {e}"); exit()

# 2. O AMBIENTE (COM 5 AÇÕES AGORA)
class DataDrivenEnvironment:
    def __init__(self, dataframe):
        self.df = dataframe
        self.locations = list(dataframe['Venue_Category'].unique())
        
        # --- NOVAS AÇÕES ADICIONADAS ---
        self.actions = [
            "Oferecer Missão de Combate", # Ação 1: Esporte/Ação
            "Oferecer Tour Histórico",    # Ação 2: Cultura
            "Oferecer Item de Energia",   # Ação 3: Descanso/Comida
            "Negociar Itens",             # Ação 4: Comércio 
            "Trocar Fofoca/Socializar"    # Ação 5: Social/Bares 
        ]
        
        counts = dataframe['Venue_Category'].value_counts(normalize=True)
        self.popularity = counts.to_dict()

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
        loc_lower = str(location).lower()

        # 1. CULTURA (Museu, Parque, Arte)
        if any(x in loc_lower for x in ['museum', 'art', 'history', 'monument', 'park', 'library']):
            if action == "Oferecer Tour Histórico": reward += 10
            elif action == "Oferecer Missão de Combate": reward -= 5 # Inadequado
        
        # 2. ESPORTE/AÇÃO (Academia, Estádio)
        elif any(x in loc_lower for x in ['gym', 'stadium', 'fitness', 'sport', 'soccer']):
            if action == "Oferecer Missão de Combate": reward += 10
            elif action == "Trocar Fofoca/Socializar": reward -= 2 # Foco no treino
            
        # 3. COMIDA/DESCANSO (Café, Restaurante)
        elif any(x in loc_lower for x in ['cafe', 'coffee', 'food', 'restaurant', 'bakery']):
            if action == "Oferecer Item de Energia": reward += 10
            elif action == "Trocar Fofoca/Socializar": reward += 5 # Também é bom socializar comendo
            
        # 4. COMÉRCIO (Loja, Shopping, Mall) -> REGRA NOVA
        elif any(x in loc_lower for x in ['shop', 'store', 'mall', 'market', 'plaza']):
            if action == "Negociar Itens": reward += 10
            elif action == "Oferecer Item de Energia": reward += 2
            
        # 5. VIDA NOTURNA/SOCIAL (Bar, Club, Nightlife) -> REGRA NOVA
        elif any(x in loc_lower for x in ['bar', 'club', 'pub', 'lounge', 'night']):
            if action == "Trocar Fofoca/Socializar": reward += 10
            elif action == "Negociar Itens": reward -= 2 # Chato vender coisa em balada

        # Bônus de Hotspot
        if self.popularity.get(location, 0) > 0.01: 
            reward += 2

        return reward

# 3. O AGENTE Q-LEARNING (MESMO CÓDIGO)
class QLearningAgent:
    def __init__(self, actions):
        self.actions = actions
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.alpha = 0.1; self.gamma = 0.9; self.epsilon = 0.1

    def get_state_key(self, state):
        return f"{state['Location']}_{state['Time']}"

    def choose_action(self, state):
        state_key = self.get_state_key(state)
        if random.random() < self.epsilon or not self.q_table[state_key]:
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
    df_foursquare = carregar_dados_reais(NOME_DO_ARQUIVO_CSV)
    env = DataDrivenEnvironment(df_foursquare)
    agent = QLearningAgent(env.actions)
    
    print("\n--- 3. INICIANDO TREINAMENTO DO AGENTE ---")
    
    # Se for modo rápido, mais épocas são treinadas sobre os poucos dados
    # para garantir que ele aprenda algo
    epochs = 10 if MODO_TESTE_RAPIDO else 2
        
    total_interations = len(df_foursquare) * epochs
    print(f"Modo: {'RÁPIDO' if MODO_TESTE_RAPIDO else 'COMPLETO'}")
    print(f"Total de interações: {total_interations}")
    
    for i in range(total_interations):
        state = env.get_random_sample()
        action = agent.choose_action(state)
        reward = env.get_reward(state, action)
        next_state = env.get_random_sample()
        agent.learn(state, action, reward, next_state)
        
        if i > 0 and i % (total_interations // 10) == 0:
            progresso = (i / total_interations) * 100
            print(f"   Progresso: {progresso:.0f}%...")

    print("--- TREINAMENTO CONCLUÍDO ---\n")
    print("--- 4. RESULTADOS (AMOSTRA) ---")
    
    locais_teste = random.sample(env.locations, min(10, len(env.locations)))
    for loc in locais_teste:
        test_state = {'Location': loc, 'Time': 'Tarde'}
        state_key = agent.get_state_key(test_state)
        if agent.q_table[state_key]:
            best_action = max(agent.q_table[state_key], key=agent.q_table[state_key].get)
            print(f"Local: '{loc[:20]:<20}' -> {best_action}")
        else:
            print(f"Local: '{loc[:20]:<20}' -> (Sem dados)")

if __name__ == "__main__":
    run_real_data_simulation()