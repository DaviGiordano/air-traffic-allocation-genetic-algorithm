# Documentação da Solução: Algoritmo Genético para Planejamento de Rotas do Tráfego Aéreo Brasileiro

## 1. Introdução

### 1.1. Contexto do Problema

O planejamento eficiente de rotas aéreas é um problema complexo de otimização combinatória que envolve múltiplas restrições operacionais e objetivos conflitantes. No contexto do tráfego aéreo brasileiro, o desafio consiste em alocar 250 aeronaves para atender a demanda diária de aproximadamente 180 mil passageiros distribuídos entre 14 aeroportos principais, respeitando janelas temporais operacionais e restrições de capacidade.

### 1.2. Parâmetros do Problema

Para este projeto, foram considerados os seguintes parâmetros:

| Parâmetro                         | Valor para análise |
| --------------------------------- | ------------------ |
| Aeroportos                        | 14                 |
| Aeronaves                         | 250                |
| Capacidade por aeronave           | 200 passageiros    |
| Voos/dia (entre os 14 aeroportos) | ~1000              |
| Passageiros/dia                   | ~94 mil            |
| Horário operacional               | 06:00–22:00        |
| Média de voos/aeronave            | 4                  |

### 1.3. Restrições Operacionais

- **Janela temporal**: Operações entre 06:00 e 22:00 (16 horas)
- **Cooldown**: 60 minutos de espera após cada voo (exceto o último)
- **Tempo máximo de percurso**: 18 horas incluindo cooldowns
- **Capacidade**: 200 passageiros por aeronave
- **Partidas**: Voos devem partir em horas cheias
- **Conexões**: Mínimo de 60 minutos entre conexões
- **Chegadas**: Todas as chegadas devem ocorrer até 22:00

### 1.4. Objetivos

1. **Maximizar** o atendimento à demanda de passageiros
2. **Minimizar** o número de passageiros não atendidos
3. **Minimizar** o número de escalas realizadas pelos passageiros
4. **Otimizar** a utilização das aeronaves

---

## 2. Método: Modelagem da Solução por Algoritmo Genético

### 2.1. Representação da Solução (Cromossomo)

A solução do problema é modelada através de um **Algoritmo Genético** (GA), onde cada indivíduo da população representa uma possível configuração de rotas para todas as aeronaves.

#### 2.1.1. Estrutura do Cromossomo

Um **cromossomo** é definido como um conjunto de 250 rotas de aeronaves:

$$C = \{A_1, A_2, ..., A_{250}\}$$

onde cada $A_i$ representa a rota de uma aeronave específica.

#### 2.1.2. Representação do Gene (Rota de Aeronave)

Cada gene $A_i$ é uma lista ordenada de códigos de aeroportos que define a sequência de voos realizados pela aeronave durante o dia:

$$A_i = [U_1, U_2, ..., U_N]$$

onde:
- $U_j$ é o código do aeroporto na posição $j$ da rota
- $N$ é o número de aeroportos visitados (mínimo 4, máximo 15)
- A sequência define os voos diretos: $U_1 \rightarrow U_2 \rightarrow ... \rightarrow U_N$

**Exemplo de rota:**
```
A_i = ['MA', 'BE', 'FO', 'NA']
```

Esta rota representa três voos consecutivos:
- MA → BE (partida às 6h, duração 120 min + cooldown 60 min)
- BE → FO (partida às 9h, duração 120 min + cooldown 60 min)  
- FO → NA (partida às 12h, duração 60 min)

### 2.2. Inicialização da População

#### 2.2.1. Geração de Rotas Aleatórias

Para cada cromossomo na população inicial, são geradas 250 rotas aleatórias respeitando as seguintes regras:

1. **Início**: Todas as aeronaves iniciam suas rotas às 06:00
2. **Geração incremental**: 
   - Seleciona aleatoriamente um aeroporto inicial
   - Adiciona aeroportos subsequentes aleatoriamente entre os aeroportos válidos (conexões existentes)
   - Calcula horário de partida e chegada para cada voo
3. **Validação temporal**:
   - Verifica se cada voo pode ser completado antes das 22:00
   - Remove aeroportos da rota se necessário para garantir chegada antes do limite
4. **Comprimento mínimo**: Garante que cada rota tenha pelo menos 4 aeroportos

**Pseudocódigo da inicialização:**

```
FUNÇÃO criar_rota_aleatória():
    rota = []
    tempo_atual = 360  // 6:00 em minutos
    aeroporto_atual = escolher_aleatoriamente(aeroportos)
    rota.adicionar(aeroporto_atual)
    
    ENQUANTO tempo_atual < 1320 E comprimento(rota) < 15:
        aeroportos_válidos = obter_conexões(aeroporto_atual)
        SE aeroportos_válidos está vazio:
            PARAR
        
        próximo_aeroporto = escolher_aleatoriamente(aeroportos_válidos)
        duração = obter_duração(aeroporto_atual, próximo_aeroporto)
        tempo_chegada = tempo_atual + duração
        
        SE tempo_chegada <= 1320:
            rota.adicionar(próximo_aeroporto)
            SE não é último_voo:
                tempo_atual = tempo_chegada + 60  // cooldown
            SENÃO:
                tempo_atual = tempo_chegada
        SENÃO:
            PARAR
    
    GARANTIR comprimento_mínimo(rota, 4)
    RETORNAR rota
```

#### 2.2.2. Estrutura de Dados para Rotas Disponíveis

Após gerar as rotas, o sistema constrói uma estrutura de dados otimizada para acesso rápido durante a alocação de passageiros. Esta estrutura mapeia pares origem-destino para todas as rotas disponíveis que podem atendê-los:

```
route_map = {
    (origem, destino): [
        (id_aeronave, escalas, tempo_total, capacidade, idx_inicio, idx_fim),
        ...
    ]
}
```

**Características importantes:**

1. **Ordenação**: As rotas são ordenadas por:
   - Número de escalas (menor primeiro)
   - Tempo total de viagem (menor primeiro)
   - Índices de segmento

2. **Extração de rotas**: Para cada rota de aeronave, são extraídos todos os possíveis pares origem-destino:
   - Voos diretos: MA → BE
   - Voos com escala: MA → BE → FO (permite MA → FO)
   - Voos com múltiplas escalas: MA → BE → FO → NA (permite MA → FO, MA → NA, BE → NA, etc.)

3. **Cálculo de horários**: Cada rota extraída inclui:
   - Horário de partida do primeiro voo
   - Tempo total de viagem (incluindo cooldowns)
   - Número de escalas (stops)

4. **Capacidade por perna**: O sistema rastreia a capacidade disponível para cada perna de voo individual, permitindo alocação parcial quando necessário.

### 2.3. Função de Avaliação (Fitness)

A função de fitness avalia a qualidade de cada cromossomo através de uma simulação completa de alocação de passageiros. O score é calculado como uma função de minimização:

$$\text{fitness} = w_1 \cdot P_{\text{não atendidos}} + w_2 \cdot E_{\text{total}} + w_3 \cdot V_{\text{total}}$$

onde:
- $P_{\text{não atendidos}}$: Número de passageiros não atendidos
- $E_{\text{total}}$: Total de escalas realizadas (ponderado pelo número de passageiros)
- $V_{\text{total}}$: Número total de voos únicos operados
- $w_1 = 100$: Peso para passageiros não atendidos (prioridade máxima)
- $w_2 = 2$: Peso para escalas
- $w_3 = 0.0$: Peso para voos (não penaliza número de voos)

**Objetivo**: Minimizar o valor do fitness (menor é melhor).

### 2.4. Operadores Evolutivos

#### 2.4.1. Seleção

A seleção utiliza **seleção por truncamento** (truncation selection):

- Seleciona os **50% melhores** cromossomos da população
- Ordenação baseada no fitness score (menor é melhor)
- Os cromossomos selecionados tornam-se pais para reprodução

**Implementação:**
```python
def selecionar_pais(população):
    população_ordenada = ordenar_por_fitness(população)
    num_selecionados = int(len(população) * 0.5)
    return população_ordenada[:num_selecionados]
```

#### 2.4.2. Crossover (Recombinação)

O crossover troca rotas entre dois cromossomos pais:

1. Seleciona aleatoriamente **50% das aeronaves** (125 aeronaves)
2. Troca as rotas correspondentes entre os dois pais
3. Gera dois filhos com combinações das rotas dos pais

**Exemplo:**
```
Pai1: [A1, A2, A3, ..., A250]
Pai2: [B1, B2, B3, ..., B250]

Índices selecionados: [1, 3, 5, ..., 249]  // 50% aleatório

Filho1: [A1, B2, A3, B4, A5, ..., B250]
Filho2: [B1, A2, B3, A4, B5, ..., A250]
```

**Implementação:**
```python
def crossover(pai1, pai2, taxa_crossover=0.5):
    num_trocar = int(len(pai1) * taxa_crossover)
    índices_trocar = escolher_aleatoriamente(range(len(pai1)), num_trocar)
    
    filho1_rotas = []
    filho2_rotas = []
    
    PARA cada índice i:
        SE i em índices_trocar:
            filho1_rotas[i] = pai2.rotas[i].copiar()
            filho2_rotas[i] = pai1.rotas[i].copiar()
        SENÃO:
            filho1_rotas[i] = pai1.rotas[i].copiar()
            filho2_rotas[i] = pai2.rotas[i].copiar()
    
    RETORNAR (Cromossomo(filho1_rotas), Cromossomo(filho2_rotas))
```

#### 2.4.3. Mutação

A mutação modifica rotas individuais dentro de um cromossomo. A estratégia implementada utiliza duas abordagens:

1. **Extensão de rota** (60% de probabilidade):
   - Estende uma rota existente adicionando mais aeroportos
   - Respeita restrições temporais e conexões válidas
   - Incentiva rotas mais longas que podem atender mais pares origem-destino

2. **Reinicialização** (40% de probabilidade):
   - Substitui completamente a rota por uma nova rota aleatória
   - Promove exploração de novas configurações

**Taxa de mutação com annealing:**

A taxa de mutação decai exponencialmente ao longo das gerações:

$$\text{mut_rate}(t) = \max(0.05, \text{mut_inicial} \cdot 0.5^{2 \cdot t/T})$$

onde:
- $t$: geração atual
- $T$: número total de gerações
- $\text{mut_inicial} = 0.3$
- Taxa mínima: $0.05$

**Implementação:**
```python
def mutar(cromossomo, taxa_mutação):
    cromossomo_mutado = cromossomo.copiar()
    
    PARA cada rota i no cromossomo:
        SE random() < taxa_mutação:
            SE random() < 0.6 E comprimento(rota[i]) >= 2:
                rota[i] = estender_rota(rota[i])
            SENÃO:
                rota[i] = criar_rota_aleatória()
    
    RETORNAR cromossomo_mutado
```

#### 2.4.4. Elitismo

O algoritmo preserva os **melhores indivíduos** de cada geração:

- Mantém o melhor cromossomo (ou N melhores, configurável)
- Substitui os piores indivíduos da nova geração pelos melhores da geração anterior
- Garante que a qualidade da solução nunca degrade entre gerações

### 2.5. Critério de Parada

O algoritmo evolutivo continua até uma das condições:

1. **Convergência**: Melhoria do fitness menor que um threshold ($\Delta < 50$) nas últimas 200 gerações
2. **Máximo de iterações**: Atinge 100 gerações (configurável)

**Detecção de convergência:**
```python
def convergiu(histórico_fitness, janela=200, threshold=50.0):
    SE len(histórico_fitness) < janela:
        RETORNAR False
    
    melhoria_recente = histórico_fitness[-janela] - histórico_fitness[-1]
    RETORNAR melhoria_recente < threshold
```

### 2.6. Parâmetros do Algoritmo Genético

| Parâmetro                | Valor | Descrição                                    |
| ------------------------- | ----- | -------------------------------------------- |
| `NUM_CHROMOSOMES`         | 100   | Tamanho da população                         |
| `MAX_ITERATIONS`          | 100   | Número máximo de gerações                     |
| `INITIAL_MUTATION_RATE`   | 0.3   | Taxa inicial de mutação                      |
| `SELECTION_RATIO`         | 0.5   | Fração da população selecionada como pais    |
| `CROSSOVER_RATIO`         | 0.5   | Fração de aeronaves trocadas no crossover    |
| `ELITISM_SIZE`            | 1     | Número de melhores indivíduos preservados    |
| `CONVERGENCE_WINDOW`      | 200   | Janela para verificar convergência           |
| `CONVERGENCE_THRESHOLD`   | 50.0  | Melhoria mínima para continuar               |

---

## 3. Método: Algoritmo de Alocação de Passageiros

### 3.1. Visão Geral

O algoritmo de alocação de passageiros simula o processo de atribuição de passageiros às rotas disponíveis, considerando capacidade das aeronaves, preferência por rotas diretas e otimização do atendimento à demanda.

### 3.2. Processo de Alocação

#### 3.2.1. Inicialização

1. **Inicialização de capacidades**: Para cada aeronave, inicializa-se a capacidade disponível para cada perna de voo (180 passageiros por perna)

2. **Construção do mapa de rotas**: Constrói-se a estrutura `route_map` que mapeia cada par origem-destino para todas as rotas disponíveis, ordenadas por qualidade

3. **Embaralhamento da demanda**: A lista de demanda é embaralhada aleatoriamente para evitar viés na ordem de processamento

#### 3.2.2. Loop Principal de Alocação

O algoritmo processa cada demanda na lista embaralhada:

**Pseudocódigo completo:**

```
FUNÇÃO alocar_passageiros(cromossomo, demanda):
    // Inicialização
    capacidades_perna = inicializar_capacidades(cromossomo, 180)
    demanda_embaralhada = embaralhar(demanda)
    alocações = []
    demanda_não_atendida = []
    mapa_rotas = construir_mapa_rotas(cromossomo, capacidades_perna)
    
    // Processamento
    fila_demanda = copiar(demanda_embaralhada)
    tentativas_od = {}  // Rastreia tentativas por par OD
    
    ENQUANTO fila_demanda não está vazia:
        (origem, destino, passageiros) = remover_primeiro(fila_demanda)
        chave_od = (origem, destino)
        
        // Verificar tentativas excessivas
        tentativas_od[chave_od] = tentativas_od.get(chave_od, 0) + 1
        SE tentativas_od[chave_od] > num_aeronaves * 2:
            adicionar(demanda_não_atendida, (origem, destino, passageiros))
            CONTINUAR
        
        // Verificar rotas disponíveis
        SE chave_od não está em mapa_rotas OU mapa_rotas[chave_od] está vazio:
            adicionar(demanda_não_atendida, (origem, destino, passageiros))
            CONTINUAR
        
        // Selecionar melhor rota (primeira na lista ordenada)
        melhor_rota = mapa_rotas[chave_od][0]
        (id_aeronave, escalas, tempo_total, capacidade, idx_inicio, idx_fim) = melhor_rota
        
        // Verificar capacidade disponível no segmento
        capacidade_segmento = calcular_capacidade_segmento(
            capacidades_perna, id_aeronave, idx_inicio, idx_fim
        )
        
        SE capacidade_segmento > 0:
            // Alocar passageiros (pode ser parcial)
            passageiros_alocar = mínimo(passageiros, capacidade_segmento)
            
            // Registrar alocação
            adicionar(alocações, (origem, destino, passageiros_alocar, 
                                  id_aeronave, escalas))
            
            // Atualizar capacidades
            PARA cada perna no segmento [idx_inicio, idx_fim):
                capacidades_perna[id_aeronave][perna] -= passageiros_alocar
            
            // Atualizar mapa de rotas com novas capacidades
            atualizar_capacidade_no_mapa(mapa_rotas, id_aeronave, capacidades_perna)
            
            // Se demanda parcialmente atendida, recolocar na fila
            passageiros_restantes = passageiros - passageiros_alocar
            SE passageiros_restantes > 0:
                inserir_início(fila_demanda, (origem, destino, passageiros_restantes))
            
            // Resetar contador de tentativas (houve progresso)
            tentativas_od[chave_od] = 0
        SENÃO:
            // Sem capacidade, recolocar no início da fila
            inserir_início(fila_demanda, (origem, destino, passageiros))
    
    RETORNAR (capacidades_perna, alocações, demanda_não_atendida)
```

#### 3.2.3. Seleção da Melhor Rota

Para cada par origem-destino, o algoritmo seleciona a melhor rota disponível baseado em:

1. **Menor número de escalas**: Prefere voos diretos sobre conexões
2. **Menor tempo total**: Entre rotas com mesmo número de escalas, escolhe a mais rápida
3. **Capacidade disponível**: Considera apenas rotas com capacidade suficiente

A ordenação é feita durante a construção do `route_map`, garantindo que a primeira rota na lista seja sempre a melhor opção.

#### 3.2.4. Alocação Parcial

O algoritmo suporta **alocação parcial** de passageiros:

- Se a capacidade disponível é menor que a demanda, aloca o máximo possível
- A demanda restante é recolocada no início da fila para nova tentativa
- Permite melhor utilização da capacidade disponível

#### 3.2.5. Atualização Dinâmica de Capacidades

Após cada alocação:

1. **Atualização por perna**: Reduz a capacidade disponível em cada perna de voo utilizada
2. **Atualização do mapa**: Recalcula capacidades de todas as rotas envolvendo a aeronave afetada
3. **Remoção de rotas sem capacidade**: Remove rotas que ficaram sem capacidade disponível

#### 3.2.6. Tratamento de Demanda Não Atendida

Uma demanda é marcada como não atendida quando:

1. Não existe nenhuma rota disponível para o par origem-destino
2. O número de tentativas excede um limite (2 × número de aeronaves)
3. Todas as rotas disponíveis estão sem capacidade

### 3.3. Cálculo de Estatísticas

Após a alocação, são calculadas as seguintes estatísticas:

1. **Passageiros não atendidos**: Soma de todos os passageiros em demandas não atendidas
2. **Total de escalas**: Soma ponderada de escalas × número de passageiros alocados
3. **Total de voos únicos**: Número de pernas de voo distintas utilizadas nas alocações

---

## 4. Resultados

### 4.1. Saídas do Sistema

O sistema gera os seguintes resultados:

#### 4.1.1. Solução Otimizada

- **Melhor cromossomo**: Conjunto de 250 rotas de aeronaves otimizadas
- **Fitness score**: Valor final da função objetivo
- **Estatísticas detalhadas**:
  - Número de passageiros atendidos
  - Número de passageiros não atendidos
  - Total de escalas realizadas
  - Número de voos únicos operados
  - Taxa de ocupação das aeronaves

#### 4.1.2. Visualizações

O sistema gera três tipos de visualizações:

1. **Dashboard de estatísticas** (`statistics.png`):
   - Top 10 pares origem-destino por passageiros alocados
   - Utilização das aeronaves (top 50)
   - Métricas principais (passageiros não atendidos, escalas, voos, fitness)
   - Taxa de atendimento (gráfico de pizza)

2. **Rede de rotas** (`routes_network.png`):
   - Visualização da rede de aeroportos
   - Rotas utilizadas destacadas por intensidade de uso
   - Rotas não utilizadas em cinza claro

3. **Rotas individuais de aeronaves** (`aircraft_routes.png`):
   - Visualização das rotas das top 20 aeronaves mais utilizadas
   - Destaque das alocações de passageiros em cada rota

#### 4.1.3. Arquivos de Dados

- **`best_chromosome.pkl`**: Cromossomo otimizado serializado
- **`stats.pkl`**: Estatísticas detalhadas da simulação
- **`genetic_algorithm.pkl`**: Estado completo do algoritmo genético

### 4.2. Estruturas de Dados Equivalentes às Tabelas Solicitadas

Embora o sistema não gere exatamente as tabelas no formato especificado, as informações equivalentes estão disponíveis:

#### 4.2.1. TAB_AV - Alocação de Voos por Aeronave

**Equivalente**: Lista de rotas no cromossomo + schedule calculado

```python
# Para cada aeronave i:
rota = cromossomo.get_routes()[i]
schedule = RouteScheduler.compute_schedule(rota, route_durations)
# schedule contém: [(departure_time, airport, arrival_time), ...]
```

**Formato equivalente**:
```
Aeronave | Rota                    | Partidas          | Chegadas         | #Pernas
---------|-------------------------|-------------------|-------------------|--------
0        | [MA, BE, FO, NA]        | [360, 540, 840]  | [480, 660, 900]  | 3
1        | [SP, RJ, BH, BR]        | [360, 420, 480]  | [420, 480, 540]  | 3
...
```

#### 4.2.2. TAB_AP - Atribuição de Passageiros aos Voos

**Equivalente**: Lista de alocações em `stats['allocations']`

```python
# Formato: (origin, dest, passengers, aircraft_id, stops)
allocations = stats['allocations']
```

**Formato equivalente**:
```
Origem | Destino | Passageiros | Aeronave | Escalas | Rotas Utilizadas
-------|---------|-------------|----------|---------|------------------
MA     | BE      | 180         | 0        | 0       | [MA→BE]
MA     | FO      | 150         | 0        | 1       | [MA→BE→FO]
SP     | RJ      | 180         | 1        | 0       | [SP→RJ]
...
```

#### 4.2.3. TAB_PV - Plano Diário Completo de Voos

**Equivalente**: Combinação de rotas + schedule + alocações

Pode ser construído combinando:
- Rotas de todas as aeronaves
- Schedules calculados
- Alocações de passageiros

**Formato equivalente**:
```
Voo | Aeronave | Origem | Destino | Partida | Chegada | Passageiros | Capacidade
----|----------|-------|---------|---------|---------|-------------|------------
1   | 0        | MA    | BE      | 06:00   | 08:00   | 180         | 180
2   | 0        | BE    | FO      | 09:00   | 11:00   | 150         | 180
3   | 1        | SP    | RJ      | 06:00   | 07:00   | 180         | 180
...
```

#### 4.2.4. TAB_MV - Mapa Horário-Rotas Espaço/Tempo

**Equivalente**: Schedule completo de todas as aeronaves

Pode ser construído a partir dos schedules individuais:

**Formato equivalente**:
```
Hora  | MA | BE | FO | NA | RE | SA | BR | BH | CI | RJ | SP | CR | FL | PA
------|----|----|----|----|----|----|----|----|----|----|----|----|----|----
06:00 | 5D | 3D | 2D | 1D | 2D | 4D | 3D | 2D | 1D | 8D | 12D| 2D | 1D | 1D
07:00 | 2A | 5A | 3A | 2A | 1A | 2A | 1A | 3A | 2A | 4A | 5A | 1A | 2A | 1A
...
```

Onde: `D` = partidas, `A` = chegadas, número = quantidade de aeronaves

### 4.3. Métricas de Performance

O sistema rastreia as seguintes métricas durante a execução:

- **Fitness score**: Evolução ao longo das gerações
- **Passageiros atendidos**: Percentual da demanda total
- **Utilização de aeronaves**: Distribuição de passageiros por aeronave
- **Eficiência de rotas**: Número médio de escalas por passageiro
- **Tempo de execução**: Performance do algoritmo

### 4.4. Uso do Sistema

#### 4.4.1. Execução Básica

```bash
python run.py
```

ou

```bash
python -m src.main
```

#### 4.4.2. Uso Programático

```python
from src.data_loader import load_all_data
from src.models.problem_data import ProblemData
from src.core.genetic_algorithm import GeneticAlgorithm

# Carregar dados
airport_codes, route_durations, demand_list = load_all_data("data")
problem_data = ProblemData(airport_codes, route_durations, demand_list)

# Criar e executar algoritmo genético
ga = GeneticAlgorithm(problem_data)
best_chromosome, stats = ga.run(verbose=True)

# Acessar resultados
print(f"Fitness: {best_chromosome.get_fitness()}")
print(f"Passageiros não atendidos: {stats['unserved_passengers']}")
print(f"Total de escalas: {stats['total_stops']}")
print(f"Total de voos: {stats['total_flights']}")
```

---

## 5. Conclusão

A solução implementada utiliza um **Algoritmo Genético** para otimizar o planejamento de rotas aéreas, modelando o problema através de:

1. **Cromossomos** representando configurações completas de 250 rotas
2. **Genes** representando rotas individuais de aeronaves
3. **Operadores evolutivos** (seleção, crossover, mutação) para explorar o espaço de soluções
4. **Função de fitness** baseada em simulação realista de alocação de passageiros
5. **Algoritmo de alocação** que simula o processo de atribuição considerando capacidade e preferências

O sistema é capaz de gerar soluções otimizadas que maximizam o atendimento à demanda enquanto minimizam escalas e passageiros não atendidos, respeitando todas as restrições operacionais do problema.

---

## Referências de Implementação

- **Modelos**: `src/models/` (Chromosome, AircraftRoute, ProblemData)
- **Algoritmo Genético**: `src/core/genetic_algorithm.py`
- **Alocação de Passageiros**: `src/core/passenger_allocator.py`
- **Extração de Rotas**: `src/core/route_extractor.py`
- **Inicialização**: `src/core/route_initializer.py`
- **Avaliação**: `src/core/fitness_evaluator.py`
- **Evolução**: `src/core/evolution_operator.py`
- **Configuração**: `src/config.py`

