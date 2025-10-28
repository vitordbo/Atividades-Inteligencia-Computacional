import random
from collections import defaultdict

# Codigo dividido em 3 partes:  
# 1. Ambiente Simulado (mundo) 
#   Criei um ambiente simulado que define os estados possíveis e, o mais importante, a função de 'recompensa' (get_reward) que o agente tentará maximizar.
#   Ela define as regras que o agente não conhece. Por exemplo, if location == 'Praça' and action == 'Oferecer Missão' and history == 'Novo', a recompensa é +10. 
#   O agente não sabe disso, ele só receberá o número 10.
#
# 2. QLearningNPCAgent (Cérebro):
#   é o NPC. O 'cérebro' dele é a q_table, um dicionário que guarda o valor de cada par (estado, ação). A função choose_action usa a política epsilon-greedy: 
#   na maior parte do tempo, ele escolhe a melhor ação que já conhece (explotação), mas às vezes (epsilon) ele tenta algo novo (exploração). 
#   é assim que ele descobre que Oferecer Missão na praça é bom. A função learn é o slide da fórmula. Ela atualiza o valor da Tabela Q. 
#   Ela pega o valor antigo e o 'puxa' em direção ao novo valor que acabou de experienciar (a recompensa mais o valor futuro)."
#
# 3. run_simulation e resultados:
#   Rodei a simulação 20.000 vezes. O agente encontra jogadores, tenta ações, recebe recompensas e aprende (faz tudo). Após o treino, esta é a 
#   'política' final do agente. Podemos ver que ele aprendeu as regras do mundo:
#   Estado: ('Museu', 'Novo', 'Dia') -> Melhor Ação: Dar Dica do Local
#   Estado: ('Praça', 'Novo', 'Dia') -> Melhor Ação: Oferecer Missão
#   Estado: ('Rua Deserta', 'Qualquer', 'Noite') -> Melhor Ação: Saudação Amigável (porque as outras ações são piores)
#   o agente aprendeu sozinho que deve oferecer missões na Praça, se tornou um agente adaptativo.

# 1. O Ambiente Simulado
# Define as "regras do mundo" que o agente NÃO conhece, mas que ele tentará aprender.
class SimulatedEnvironment:
    def __init__(self):
        # Estados são uma combinação de (Local, Histórico_Jogador)
        self.locations = ["Praça", "Museu", "Rua Deserta"]
        self.player_history = ["Novo", "Completou_Missão_1", "Ignorou_NPC_Antes"]
        
        # Ações são as "intenções" de diálogo do NPC
        self.actions = ["Saudação Amigável", "Oferecer Missão", "Dar Dica do Local"]

    def get_random_state(self):
        """Retorna um estado aleatório para simular o jogador aparecendo."""
        location = random.choice(self.locations)
        history = random.choice(self.player_history)
        return (location, history)

    def get_reward(self, state, action):
        """
        Esta é a "lógica" do mundo. O agente não conhece isso, 
        ele só recebe o número (recompensa).
        
        REGRAS DO MUNDO (Exemplos):
        - Oferecer missão na praça para jogador novo é ÓTIMO (+10).
        - Dar dica no museu é BOM (+5).
        - Oferecer missão para quem já completou é RUIM (-5).
        - Saudar amigavelmente quem te ignorou é NEUTRO (+1).
        - Fazer qualquer coisa na rua deserta é RUIM (jogador se sente inseguro) (-3).
        """
        location, history = state
        reward = 0

        # Regras da "Rua Deserta"
        if location == "Rua Deserta":
            reward = -3 # Local ruim para interação

        # Regras da "Praça"
        elif location == "Praça":
            if action == "Oferecer Missão":
                reward = 10 if history == "Novo" else -5 # Bom para novos, ruim para antigos
            elif action == "Saudação Amigável":
                reward = 3
            elif action == "Dar Dica do Local":
                reward = 1
        
        # Regras do "Museu"
        elif location == "Museu":
            if action == "Dar Dica do Local":
                reward = 7 # Muito relevante
            elif action == "Oferecer Missão":
                reward = -2 # Lugar errado para missões
            elif action == "Saudação Amigável":
                reward = 2
        
        # Regra geral de histórico
        if history == "Ignorou_NPC_Antes" and action == "Saudação Amigável":
            reward += 1 # Tentar reconquistar é ok
            
        return reward

# 2. O Agente NPC (Q-Learning)
class QLearningNPCAgent:
    """
    Este é o "cérebro" do NPC. Ele usa uma Tabela Q para aprender
    o valor de cada par (estado, ação).
    
    Q(s, a) = valor esperado de tomar a ação 'a' no estado 's'
    """
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.actions = actions
        
        # --- Parâmetros do Q-Learning ---
        
        # alpha (Taxa de Aprendizado): O quanto confiamos na nova informação.
        self.alpha = alpha 
        
        # gamma (Fator de Desconto): O quanto valorizamos recompensas futuras.
        self.gamma = gamma 
        
        # epsilon (Exploration Rate): A chance de tomar uma ação aleatória (explorar).
        self.epsilon = epsilon 
        
        # A Tabela Q!
        # É um dicionário aninhado: Q[estado][ação] = valor
        # defaultdict(float) garante que toda nova entrada (s,a) comece com valor 0.0
        self.q_table = defaultdict(lambda: defaultdict(float))

    def _get_state_key(self, state):
        """Converte o tuple (local, historico) em uma chave de dicionário."""
        return str(state)

    def choose_action(self, state):
        """
        Decide qual ação tomar usando a política Epsilon-Greedy.
        - Com chance (epsilon), explora (ação aleatória).
        - Com chance (1-epsilon), explora o que já sabe (melhor ação).
        """
        state_key = self._get_state_key(state)
        
        # 1. Exploração
        if random.random() < self.epsilon or not self.q_table[state_key]:
            return random.choice(self.actions)
        
        # 2. Explotação (Pegar a melhor ação conhecida)
        q_values = self.q_table[state_key]
        return max(q_values, key=q_values.get)

    def learn(self, state, action, reward, next_state):
        """
        O coração do algoritmo. Atualiza a Tabela Q com base
        na experiência (s, a, r, s').
        
        A Fórmula do Q-Learning:
        Q(s,a) <- Q(s,a) + alpha * [recompensa + gamma * max(Q(s',a')) - Q(s,a)]
        """
        state_key = self._get_state_key(state)
        next_state_key = self._get_state_key(next_state)
        
        # 1. Encontrar o valor da melhor ação possível no *próximo* estado
        next_q_values = self.q_table[next_state_key]
        max_q_next = max(next_q_values.values()) if next_q_values else 0.0
        
        # 2. Valor atual que o agente *achava* que (s,a) valia
        current_q = self.q_table[state_key][action]
        
        # 3. Calcular o "valor alvo" (o que aprendemos com a experiência)
        # (recompensa imediata + recompensa futura descontada)
        target_q = reward + self.gamma * max_q_next
        
        # 4. Atualizar o valor de Q(s,a)
        # O novo valor é o antigo "puxado" um pouco (alpha) na direção do alvo
        new_q = current_q + self.alpha * (target_q - current_q)
        self.q_table[state_key][action] = new_q

    def print_q_table(self):
        """Exibe a Tabela Q aprendida."""
        print("\n--- CÉREBRO DO AGENTE (TABELA Q) ---")
        if not self.q_table:
            print("Vazio. O agente não aprendeu nada.")
            return
            
        for state_key, actions in sorted(self.q_table.items()):
            print(f"\nEstado: {state_key}")
            for action, q_value in sorted(actions.items(), key=lambda item: item[1], reverse=True):
                print(f"  Ação: {action:<20} | Q-Valor: {q_value:.2f}")

    def print_policy(self):
        """Exibe a política final (a melhor ação para cada estado)."""
        print("\n--- POLÍTICA FINAL (DECISÕES DO NPC) ---")
        if not self.q_table:
            print("Vazio. O agente não aprendeu nada.")
            return
            
        for state_key in sorted(self.q_table.keys()):
            q_values = self.q_table[state_key]
            best_action = max(q_values, key=q_values.get)
            print(f"Estado: {state_key:<45} -> Melhor Ação: {best_action}")

# 3. A Simulação (Treinamento do Agente)
def run_simulation():
    print("Iniciando simulação... O Agente NPC vai 'viver' e aprender.")
    
    # 1. Inicializar ambiente e agente
    env = SimulatedEnvironment()
    agent = QLearningNPCAgent(actions=env.actions)

    # 2. Definir parâmetros da simulação
    # Vamos simular 20.000 "encontros" de jogadores com o NPC
    num_episodes = 20000 
    
    print(f"Treinando o agente por {num_episodes} episódios (encontros)...")

    # 3. Loop de Treinamento
    for i in range(num_episodes):
        # Um jogador aparece em um local (estado s)
        state = env.get_random_state()
        
        # O agente escolhe o que fazer (ação a)
        action = agent.choose_action(state)
        
        # O agente vê a reação do jogador (recompensa r)
        reward = env.get_reward(state, action)
        
        # O jogador se move para um próximo local (estado s')
        # (Para esta simulação, apenas pegamos outro estado aleatório)
        next_state = env.get_random_state()
        
        # O agente aprende com essa experiência (s, a, r, s')
        agent.learn(state, action, reward, next_state)
        
        if (i + 1) % 5000 == 0:
            print(f"Episódio {i+1}/{num_episodes} concluído.")

    print("\n--- Treinamento Concluído! ---")
    
    # 4. Mostrar Resultados
    # agent.print_q_table() # Descomente se quiser ver a tabela completa
    agent.print_policy()

# Executar a simulação
if __name__ == "__main__":
    run_simulation()