# Questões 2.7 e 2.8

# 2.8 Implemente um simulador de ambiente de medição de desempenho para o mundo de aspirador de pó representado na Figura 2.2 e 
# especificado na página 38. Sua implementação deve ser modular, de forma que os sensores, os atuadores e as características 
# do ambiente (tamanho, forma, localização da sujeira etc.) possam ser alterados com facilidade. 
# (Nota: Para algumas opções de linguagens de programação e sistemas operacionais, já existem implementações no repositório de código on-line.)

# 2.9 Implemente um único agente reflexo para o ambiente de vácuo do Exercício 2.8. Execute o
# ambiente com esse agente para todas as configurações iniciais sujas e localizações do agente
# possíveis. Registre a nota de desempenho de cada configuração e a nota média global.

import random

# ambiente => representa o mundo do aspirador (duas salas: A e B).
class Ambiente:
    def __init__(self, sujeira_A=True, sujeira_B=True, posicao="A"): # sujeira_A e sujeira_B dizem se as salas começam sujas (True) ou limpas (False)
        self.sujeira = {"A": sujeira_A, "B": sujeira_B}
        self.posicao = posicao # é onde o aspirador começa
        self.pontuacao = 0 # nota de desempenho

    def esta_sujo(self): # Verifica se a sala atual onde o agente está está suja
        return self.sujeira[self.posicao]

    def executar_acao(self, acao): # recebe a ação escolhida pelo agente e muda o ambiente
        if acao == "Aspirar": # limpa a sala
            if self.sujeira[self.posicao]:
                self.sujeira[self.posicao] = False
        elif acao == "Esquerda": # vai pra sala A
            self.posicao = "A"
        elif acao == "Direita": # vai pra sala B
            self.posicao = "B"
        # desempenho: +1 ponto por cada sala limpa
        self.pontuacao += sum(1 for v in self.sujeira.values() if v == False)

# Agente reflexo simples
def agente_reflexo(percepcao):
    posicao, sujo = percepcao
    if sujo: # se tá sujo => aspira
        return "Aspirar"
    elif posicao == "A":
        return "Direita"
    else:
        return "Esquerda"

# Simulação => Cria um ambiente inicial (A suja, B suja, agente em A)
# Roda por 5 passos:
    # O agente percebe sua posição e se está sujo
    # Decide a ação com agente_reflexo
    # O ambiente executa a ação e atualiza o estado
    # Mostra no console
amb = Ambiente(sujeira_A=True, sujeira_B=True, posicao="A")
for passo in range(5):  # simula 5 passos => O agente percebe sua posição e se está sujo
    percepcao = (amb.posicao, amb.esta_sujo())
    acao = agente_reflexo(percepcao)
    amb.executar_acao(acao)
    print(f"Passo {passo+1}: Percepção={percepcao}, Ação={acao}, Estado={amb.sujeira}, Pontos={amb.pontuacao}")
