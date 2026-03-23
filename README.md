# Projeto de Otimização de Rotas de Transporte - Recife/PE

Este projeto implementa um sistema de otimização de rotas de transporte público multimodal para a cidade do Recife, focando na conexão entre **Cinema São Luiz (Boa Vista)** e **Faculdade Nova Roma (Boa Viagem)**.

Integrantes: Adrian Modesto, Artur Lima, Celso Gabriel, Gustavo dos Santos e Lucas Pereira

## Estrutura do Projeto

### Scripts Principais

- **`main.py`** - Coleta dados de transporte via OpenStreetMap (Overpass API)
- **`build_graph.py`** - Constrói grafo multimodal a partir dos dados coletados
- **`routing_examples.py`** - Exemplos de algoritmos de roteamento (Dijkstra, A*, multiobjetivo)
- **`best_routes.py`** - Gera 3 melhores rotas: transporte público, carro próprio e moto

### Dados Coletados (`dados_coletados/`)

- `paradas_onibus.json` - 673 paradas de ônibus
- `estacoes_metro.json` - 10 estações de metrô/trem
- `linhas_onibus.json` - 54 linhas de ônibus
- `linhas_metro.json` - 6 linhas de metrô
- `ciclovias.json` - 268 ciclovias/ciclofaixas
- `vias_pedestres.json` - 2.112 vias para pedestres
- `rede_viaria.json` - 2.957 ruas/avenidas

**Total: 6.080 elementos de infraestrutura de transporte**

## Como Executar

### 1. Instalar Dependências

```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Coletar Dados (opcional - já feito)

```bash
.\venv\Scripts\python.exe main.py
```

### 3. Construir Grafo Multimodal

```bash
.\venv\Scripts\python.exe build_graph.py
```

**Saída**: Cria `transport_graph.gpickle` com 683 nós e 6.396 arestas

### 4. Executar Exemplos de Roteamento

```bash
.\venv\Scripts\python.exe routing_examples.py
```

**Saída**:
- Dijkstra (tempo mínimo): ~18.6 min, 23 nós
- A* com heurística haversine: 23 nós  
- Peso composto (multiobjetivo): 23 nós

### 5. Gerar as 3 Melhores Rotas (Transporte Público, Carro e Moto)

```bash
.\venv\Scripts\python.exe best_routes.py
```

**Saída**:
- Cria `dados_coletados/best_routes.json`
- Exibe no terminal o resumo das 3 rotas com tempo, distância e número de nós

## Modelagem do Grafo

### Nós (Vertices)
- **Paradas de ônibus**: `bus:<id>` (673 nós)
- **Estações de metrô**: `rail:<id>` (10 nós)
- Atributos: `lat`, `lon`, `name`, `type`

### Arestas (Edges)
- **Caminhada** (`mode='walk'`): conexões entre nós próximos (≤200m)
  - Velocidade: 1.4 m/s
  - Custo: gratuito
- **Ônibus** (`mode='bus'`): sequência de paradas das linhas
  - Velocidade: 8.0 m/s
  - Derivado das relações OSM
- **Metrô** (`mode='rail'`): sequência de estações das linhas
  - Velocidade: 15.0 m/s
  - Deriva das relações OSM

### Atributos das Arestas
- `distance_m`: distância em metros
- `time_s`: tempo estimado em segundos
- `cost`: custo (tarifa)
- `mode`: modal de transporte
- `route`: linha/rota (se aplicável)

## Algoritmos Implementados

### 1. Dijkstra
```python
nx.shortest_path(G, origem, destino, weight='time_s')
```
Caminho ótimo para critério único (tempo, distância, custo).

### 2. A* (A-estrela)
```python
def heuristic(a, b): 
    return haversine_distance(a, b) / walking_speed

nx.astar_path(G, origem, destino, heuristic=heuristic, weight='time_s')
```
Mais eficiente que Dijkstra usando distância euclidiana como heurística.

### 3. Multiobjetivo (Peso Composto)
```python
peso_composto = w_tempo * tempo + w_custo * custo + w_emissoes * emissoes
```
Combina múltiplos critérios com pesos configuráveis.

## Próximos Passos

- [ ] Integrar dados GTFS reais (horários, frequências)
- [ ] Implementar algoritmo Pareto para fronteira ótima multiobjetivo
- [ ] Adicionar visualização em mapa (Folium/Plotly)
- [ ] Incluir dados de trânsito em tempo real
- [ ] Expandir para outros pares origem-destino

## Tecnologias

- **Python 3.x**
- **NetworkX** - manipulação de grafos
- **SciPy** - indexação espacial eficiente
- **OpenStreetMap** - fonte de dados geográficos
- **Requirements**: `networkx`, `scipy`