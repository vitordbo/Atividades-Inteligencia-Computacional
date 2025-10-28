import random
import time
from constraint import Problem, AllDifferentConstraint

# O Agente RL recebe o estado (Praça, Nível 5, Novo) e, com base na sua política pré-treinada, decide que a melhor intenção é Oferecer_Missão_Fácil.
# O sistema recebe a intenção 'Missão Fácil'. Ele usa o python-constraint para gerar uma missão que obedeça às regras. 
# planejador recebe a intenção 'Missão Fácil' e os detalhes da missão do CSP. Ele então monta o roteiro de diálogo.
# O NPC executa o plano, apresentando ao jogador uma missão dinâmica, relevante e coerente, tudo graças à orquestração dessas três técnicas de IA

# DADOS DO MUNDO (Simulação) - O "conhecimento" que o CSP usará
ENEMY_DB = {
    # 'nome': (nível_min, recompensa_base)
    'Lobo': (2, 20),
    'Goblin': (1, 15),
    'Bandido': (5, 50),
    'Orc': (8, 100),
    'Dragão Bebê': (10, 250)
}

LOCATION_DB = ['Bosque Sombrio', 'Caverna Ecoante', 'Ruínas Antigas', 'Torre do Mago']

# CAMADA 1: AGENTE RL (O DECISOR DE INTENÇÃO)
class AgenteRLTreinado:
    """
    Simula um agente de Q-Learning JÁ TREINADO.
    Em vez de uma Tabela Q, se mostra a *política* resultante
    (o melhor 'Q' para cada estado).
    """
    
    def get_intention(self, state):
        """Recebe o estado e retorna a melhor intenção."""
        print(f"[CAMADA 1: RL] Estado recebido: {state}")
        
        local = state['local']
        nivel = state['nivel']
        historico = state['historico']
        
        # --- Regras aprendidas pelo RL (Política) ---
        if local == 'Praça' and historico == 'Novo' and nivel < 10:
            # A Tabela Q aprendeu que esta é a melhor ação
            return 'Oferecer_Missão_Fácil'
        
        elif local == 'Praça' and historico == 'Novo' and nivel >= 10:
            return 'Oferecer_Missão_Média'

        elif local == 'Praça' and historico == 'Veterano':
            # Já fez missões, só saudar
            return 'Saudação_Amigável'
            
        elif local == 'Museu':
            # RL aprendeu que no Museu, dar dicas é melhor
            return 'Dar_Dica_Local'
            
        else:
            return 'Saudação_Padrão'

# CAMADA 2: GERADOR DE MISSÕES (CSP)
class GeradorMissoesCSP:
    """
    Usa a biblioteca 'constraint' para gerar dinamicamente
    o conteúdo da missão, garantindo que seja coerente.
    """
    
    def generate_quest(self, state, intention):
        """Gera uma missão válida com base nas restrições."""
        print("\n[CAMADA 2: CSP] Gerador de Missões ativado.")
        
        if not 'Missão' in intention:
            print("[CAMADA 2: CSP] Intenção não requer geração de missão.")
            return None

        # 1. Definir o problema
        problem = Problem()
        
        # 2. Definir Variáveis e Domínios
        problem.addVariable("local_alvo", [loc for loc in LOCATION_DB])
        problem.addVariable("inimigo", [enemy for enemy in ENEMY_DB.keys()])
        problem.addVariable("quantidade", range(3, 11)) # De 3 a 10 inimigos
        
        # 3. Definir Restrições
        
        # Restrição 1: O local da missão NÃO PODE ser o local atual.
        current_local = state['local']
        problem.addConstraint(
            lambda local: local != current_local,
            ["local_alvo"]
        )

        # Restrição 2: O nível do inimigo deve ser compatível.
        player_level = state['nivel']
        
        if intention == 'Oferecer_Missão_Fácil':
            # Missão fácil: inimigo com nível <= nível do jogador + 1
            problem.addConstraint(
                lambda inimigo: ENEMY_DB[inimigo][0] <= player_level + 1,
                ["inimigo"]
            )
        elif intention == 'Oferecer_Missão_Média':
            # Missão média: inimigo com nível > nível do jogador + 1, mas <= nível + 4
            problem.addConstraint(
                lambda inimigo: (ENEMY_DB[inimigo][0] > player_level + 1) and \
                                (ENEMY_DB[inimigo][0] <= player_level + 4),
                ["inimigo"]
            )
        
        # Restrição 3: (Opcional) Lugares perigosos só para níveis altos
        problem.addConstraint(
            lambda local, inimigo: not (local == 'Torre do Mago' and ENEMY_DB[inimigo][0] < 8),
            ["local_alvo", "inimigo"]
        )

        # 4. Encontrar uma solução
        solution = problem.getSolution()
        
        if not solution:
            print("[CAMADA 2: CSP] Não foi possível gerar uma missão com as restrições.")
            return None
            
        # 5. Calcular a Recompensa (fora do CSP, mas baseado nele)
        base_reward = ENEMY_DB[solution['inimigo']][1]
        solution['recompensa'] = base_reward * solution['quantidade']
        
        print(f"[CAMADA 2: CSP] Missão gerada: {solution}")
        return solution

# CAMADA 3: PLANEJADOR DE DIÁLOGO
class PlanejadorDialogo:
    """
    Seleciona um "plano" de diálogo (um roteiro)
    com base na intenção do RL e nos dados do CSP.
    """
    
    def get_dialogue_plan(self, intention, quest, state):
        """Retorna uma lista de falas (o plano de diálogo)."""
        print("\n[CAMADA 3: PLANO] Gerando roteiro de diálogo...")
        plan = []

        if intention == 'Oferecer_Missão_Fácil':
            plan.append(f"Olá, aventureiro! Bem-vindo à {state['local']}.")
            plan.append(f"Vejo que você é novo por aqui... Sabe, o {quest['local_alvo']} está infestado de {quest['inimigo']}s ultimamente.")
            plan.append(f"Eu preciso que alguém derrote {quest['quantidade']} deles.")
            plan.append(f"Se você fizer isso por mim, eu te darei {quest['recompensa']}g de ouro!")
            plan.append("(Você aceita a missão? [S/N])")
            
        elif intention == 'Oferecer_Missão_Média':
            plan.append(f"Ah, {state['nome']}! Que bom te ver.")
            plan.append(f"Você já provou seu valor, então tenho um desafio maior.")
            plan.append(f"O {quest['local_alvo']} está sendo dominado por {quest['inimigo']}s.")
            plan.append(f"É perigoso, mas a recompensa é alta: {quest['recompensa']}g para derrotar {quest['quantidade']} deles.")
            plan.append("(Você encara o desafio? [S/N])")
            
        elif intention == 'Dar_Dica_Local':
            plan.append(f"Bem-vindo ao {state['local']}, {state['nome']}.")
            plan.append("Você sabia? Dizem que este museu foi construído sobre as ruínas de uma antiga civilização.")
            plan.append("Muitos exploradores vêm aqui buscar pistas...")

        elif intention == 'Saudação_Amigável':
            plan.append(f"E aí, {state['nome']}! Bom te ver de novo.")
            plan.append("Os negócios estão parados... nenhuma missão por agora.")

        else: # Saudação_Padrão
            plan.append("Olá. O dia está calmo.")
            
        print("[CAMADA 3: PLANO] Roteiro de diálogo criado.")
        return plan

# FUNÇÃO PRINCIPAL: SIMULAÇÃO DO EVENTO
def run_demo():
    
    print("--- INICIANDO DEMONSTRAÇÃO DA ARQUITETURA DE IA DO NPC ---")
    
    # 1. Instanciar as camadas
    agente_rl = AgenteRLTreinado()
    gerador_csp = GeradorMissoesCSP()
    planejador = PlanejadorDialogo()
    
    # 2. O EVENTO: Jogador entra na Geofence
    current_state = {
        'nome': 'JogadorX',
        'local': 'Praça',
        'nivel': 5,
        'historico': 'Novo'
    }
    print(f"\nEVENTO: {current_state['nome']} (Nível {current_state['nivel']}) entrou na '{current_state['local']}'.")
    print("-" * 60)
    time.sleep(1) # Pausa para leitura
       
    # 3. CAMADA 1 (RL) decide O QUE fazer
    intention = agente_rl.get_intention(current_state)
    print(f"[CAMADA 1: RL] Decisão: {intention}")
    time.sleep(1)
    
    # 4. CAMADA 2 (CSP) gera COMO fazer (o conteúdo)
    quest = gerador_csp.generate_quest(current_state, intention)
    time.sleep(1)

    # 5. CAMADA 3 (PLANO) monta o diálogo
    dialogue_plan = planejador.get_dialogue_plan(intention, quest, current_state)
    time.sleep(1)

    # 6. EXECUÇÃO: O NPC fala com o jogador
    print("\n--- INÍCIO DA INTERAÇÃO (NPC FALANDO) ---")
    for line in dialogue_plan:
        print(f"NPC: {line}")
        time.sleep(1.5) # Simula o tempo de leitura
    print("--- FIM DA INTERAÇÃO ---")

# Rodar a simulação
if __name__ == "__main__":
    run_demo()