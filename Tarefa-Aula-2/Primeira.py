# Tarefa 1 => Estudar e implementar o algoritmo da Fig. 5.3

# Figura 5.3 Um algoritmo para calcular decisões minimax. Ele retorna a ação correspondente ao
# melhor movimento possível, isto é, o movimento que leva ao resultado com a melhor utilidade, sob a
# suposição de que o oponente joga para minimizar a utilidade. As funções VALOR-MAX e VALOR
# MIN passam por toda a árvore de jogo, até chegar às folhas, a fim de determinar o valor de
# propagação de volta de um estado. A notação argmaxa∊s f(a) calcula o elemento a do conjunto S que
# possui o valor máximo de f(a).

import math

class No: # nó na árvore do jogo
    def __init__(self, nome, utilidade=None, filhos=None):
        self.nome = nome
        self.utilidade = utilidade  # Valor de utilidade se for um nó terminal (folha)
        self.filhos = filhos if filhos is not None else []

    def is_terminal(self): # verifica se o nó ainda tem filhos
        return not self.filhos
    
# maximizar a pontuação
def valor_max(estado):
    if estado.is_terminal():
        return estado.utilidade

    v = -math.inf  # Inicializa com menos infinito
    for proximo_estado in estado.filhos:
        v = max(v, valor_min(proximo_estado))
    return v

# minimizar a pontuação
def valor_min(estado):
    if estado.is_terminal():
        return estado.utilidade

    v = math.inf  # Inicializa com mais infinito
    for proximo_estado in estado.filhos:
        v = min(v, valor_max(proximo_estado))
    return v

# escolhe a melhor ação
def decisao_minimax(estado):
    melhor_acao = None
    max_valor = -math.inf

    # Itera sobre todas as ações (filhos) possíveis
    for acao in estado.filhos:
        # Calcula o valor do estado resultante da perspectiva do min
        v = valor_min(acao)
        if v > max_valor:
            max_valor = v
            melhor_acao = acao
            
    return melhor_acao

# teste com uma arvore menor
# O jogador max na raiz 'A' pode escolher entre ir para 'B' ou 'C'.
no_raiz_a = No("A", filhos=[
    # Se max for para 'B', min escolherá o menor valor entre 5 e 3.
    No("B", filhos=[
        No("Folha_B1", utilidade=5),
        No("Folha_B2", utilidade=3)
    ]),
    # Se max for para 'C', min escolherá o menor valor entre 10 e 1.
    No("C", filhos=[
        No("Folha_C1", utilidade=10),
        No("Folha_C2", utilidade=1)
    ])
])


print("Analisando a melhor jogada a partir do nó 'A':")

# valores minimos possiveis
valor_da_jogada_b = valor_min(no_raiz_a.filhos[0])
print(f"-> Valor garantido ao escolher 'B': min(5, 3) = {valor_da_jogada_b}")

valor_da_jogada_c = valor_min(no_raiz_a.filhos[1])
print(f"-> Valor garantido ao escolher 'C': min(10, 1) = {valor_da_jogada_c}")

# mlehor jogada pra max
melhor_jogada = decisao_minimax(no_raiz_a)
print("\n" + "-"*30)
print(f"Decisão do MAX: escolher o caminho com o maior valor garantido: max(3, 1)")
print(f"A melhor jogada é ir para o nó '{melhor_jogada.nome}'")