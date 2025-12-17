# Atividades Inteligencia Computacional
Atividades da materia de inteligencia computacional semestre 2025.2 do mestrado em Ciências da computação - UFERSA/UERN
Retiradas do livro: Russel & Norvig. Artificial Intelligence. 3a Ed.

# Geração Adaptativa de Diálogos para NPCs em Jogos Geolocalizados: Uma Abordagem Data-Driven

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Research-orange)

Este repositório contém a implementação do algoritmo de **Aprendizado por Reforço (Q-Learning)** utilizado no artigo *"Geração Adaptativa de Diálogos para NPCs 
em Jogos Geolocalizados: Uma Abordagem 
Data-Driven baseada em Aprendizado por 
Reforço"*.

O projeto propõe uma arquitetura onde Agentes Inteligentes (NPCs) aprendem a melhor estratégia de diálogo baseando-se no contexto semântico do local e em dados reais de comportamento humano extraídos de Redes Sociais Baseadas em Localização (LBSN).

## 📋 Sobre o Projeto

Em Jogos Geolocalizados (JGs), a imersão é frequentemente quebrada por NPCs estáticos que não reagem ao ambiente. Este código implementa um agente que utiliza dados históricos de **Nova York (Foursquare NYC)** para aprender políticas de interação contextuais.

### Principais Características
* **Abordagem Data-Driven:** Utiliza dados reais de LBSN como *proxy* para comportamento de jogadores.
* **Aprendizado Offline:** O agente é treinado sobre um histórico de check-ins, não necessitando de interação em tempo real durante a fase de aprendizado.
* **Contexto Semântico:** O algoritmo considera a categoria do local (ex: Museu, Ginásio) e o horário do dia.
* **Detecção de Hotspots:** O sistema identifica e bonifica interações em locais de alta popularidade.

## ⚙️ Metodologia Técnica

O problema foi modelado como um Processo de Decisão de Markov (MDP):

1.  **Estado ($S$):** Tupla composta por `{Categoria do Local, Período do Dia}`.
2.  **Ações ($A$):** O agente escolhe entre intenções de diálogo, como:
    * *Oferecer Missão de Combate* (Foco em Ação)
    * *Oferecer Tour Histórico* (Foco em Cultura)
    * *Oferecer Item de Energia* (Foco em Suporte)
    * *Socializar (Foco em amizades/social)
    * *Negociar itens (Foco em comércio)
3.  **Recompensa ($R$):** Calculada baseada na **Coerência Semântica** (compatibilidade entre ação e local) e na **Popularidade** do local (bônus para Hotspots).

## 🚀 Como Executar

### Pré-requisitos

O código foi desenvolvido em Python. As bibliotecas necessárias são:

```bash
pip install pandas numpy
```

### 📂 Configuração do Dataset

Este projeto utiliza o dataset **Foursquare NYC (TSMC2014)**, que contém check-ins reais de usuários em Nova York. Devido ao tamanho do arquivo e licenças de uso, ele não está incluído diretamente neste repositório.

1.  **Baixe o Dataset:** O dataset está disponível publicamente no Kaggle ou em repositórios de computação urbana.
    * *Sugestão de fonte:* [Foursquare Dataset - NYC (Kaggle)](https://www.kaggle.com/datasets/chetanism/foursquare-nyc-and-tokyo-checkin-dataset) ou procure por "dataset_TSMC2014_NYC.csv".
2.  **Posicionamento:** Baixe o arquivo `.csv` e coloque-o na **raiz** deste projeto (na mesma pasta do script Python).
3.  **Nome do Arquivo:** Certifique-se de que o arquivo se chame `dataset_TSMC2014_NYC.csv`.
    * *Nota:* Se o seu arquivo tiver outro nome, altere a variável `NOME_DO_ARQUIVO_CSV` no início do código `main.py`.

### ▶️ Executando a Simulação

Com as dependências instaladas e o dataset configurado, execute o script principal:

```bash
python main.py