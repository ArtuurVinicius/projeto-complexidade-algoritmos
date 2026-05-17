# Projeto de Otimização de Rotas de Transporte - Recife/PE

Este repositório implementa um sistema híbrido de otimização e visualização de rotas para a cidade do Recife. O projeto atualmente contém:

- Um conjunto de scripts Python para coleta e construção de grafos multimodais e rodoviários
- Um backend Node/Express que expõe a API de grafos e rotas
- Um frontend Vue 3/Vite que consome a API e renderiza os mapas com Leaflet

O fluxo de origem e destino usado nas rotas está fixo em:
- `Cinema São Luiz (Boa Vista)`
- `Faculdade Nova Roma (Boa Viagem)`

Integrantes: Adrian Modesto, Artur Lima, Celso Gabriel, Gustavo dos Santos e Lucas Pereira

## Estrutura do Repositório

- `algoritmos/` - scripts Python e dados de transporte
- `backend/` - API REST Node.js
- `frontend/` - app Vue 3 com Vite e Leaflet

## O que mudou neste README

- Incluí a documentação do backend e seus endpoints REST atuais
- Adicionei a descrição do frontend Vue 3 / Leaflet / Vuetify
- Mantive e atualizei a parte de algoritmos Python que já existia
- Explanei o fluxo atual de chamadas entre frontend e backend
- Incluí a configuração de proxy Vite que redireciona `/api` para `http://localhost:3001`

---

## Backend Node.js

### Dependências principais

- `express`
- `node-fetch`
- `swagger-jsdoc`
- `swagger-ui-express`

### Execução

```bash
cd backend
npm install
npm start
```

O servidor inicializa na porta `3001` por padrão. A porta pode ser alterada definindo `PORT` no ambiente.

### Endpoints disponíveis

- `GET /api/health`
  - Healthcheck simples
- `GET /api/graph/transport`
  - Retorna o grafo multimodal de transporte ou rota de origem/destino quando `route=true`
  - Query params:
    - `walkThresholdM` (opcional): distância máxima de caminhada entre nós
    - `route` (opcional): `true` para retornar somente a rota
    - `rebuild` (opcional): `true` para forçar reconstrução do grafo em cache
- `GET /api/graph/road`
  - Retorna o grafo rodoviário para `modal=car` ou `modal=moto`
  - Query params:
    - `modal`: `car` ou `moto` (default `car`)
    - `route`: `true` para rota origem/destino
    - `rebuild`: `true` para forçar rebuild
- `GET /api/graph/route`
  - Retorna geometria OSRM entre dois nós existentes
  - Query params obrigatórios: `from`, `to`
  - `profile` opcional: `driving` por padrão
- `GET /api/graph/transport/edges-geo`
  - Retorna geometrias OSRM para as primeiras `N` arestas de transporte
  - Query params:
    - `limit` (default `100`)
    - `profile` (default `driving`)
- `POST /api/graph/transport/nodes`
  - Cria um nó de transporte em memória
- `POST /api/graph/transport/edges`
  - Cria uma aresta de transporte em memória

### Documentação Swagger

- `GET /api/docs`
  - Interface Swagger gerada automaticamente pelo backend

### Observações do backend

- O backend lê dados do diretório `algoritmos/dados_coletados`
- Se o backend for executado fora do repositório, é possível definir `ALGORITIMOS_DIR` para apontar a pasta `algoritmos`
- As rotas padrão usam os mesmos `origin` e `destination` codificados em `backend/src/services/graphService.js`

---

## Frontend Vue 3

### Dependências principais

- `vue` 3
- `vite`
- `vuetify`
- `leaflet`
- `@mdi/font`

### Execução

```bash
cd frontend
npm install
npm run dev
```

O frontend roda em `http://localhost:5173` e inclui proxy para o backend:
- `/api` → `http://localhost:3001`

### Comportamento atual

- O componente `App.vue` faz chamadas fixas para:
  - `/api/graph/transport?route=true`
  - `/api/graph/road?modal=car&route=true`
  - `/api/graph/road?modal=moto&route=true`
- O `SearchBar.vue` permite entrada de origem e destino, mas esses valores não são enviados ao backend;
  portanto, a rota atual mantém os pontos de origem/destino definidos no backend.
- O `MapArea.vue` desenha as rotas retornadas pelo backend em um mapa Leaflet.
- O `Sidebar.vue` exibe origem e destino na interface.

### Tela principal

- `SearchBar.vue`
  - campos de origem e destino
  - botão para trocar origem/destino
  - filtros de modo (Transporte público / Carro / Moto)
- `MapArea.vue`
  - renderiza rotas como polígonos no mapa
  - usa cores diferentes para transporte, carro e moto
- `Sidebar.vue`
  - mostra origem e destino atuais

---

## Scripts e Dados Python

### Dependências Python

```bash
cd algoritmos
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Scripts existentes

- `main.py` - coleta dados do OpenStreetMap via Overpass API
- `build_graph.py` - constrói grafo multimodal a partir dos dados coletados
- `routing_examples.py` - valida e demonstra roteamento com Dijkstra, A* e multiobjetivo
- `best_routes.py` - gera as 3 melhores rotas e salva em `dados_coletados/best_routes.json`

### Dados de entrada

Os principais arquivos em `algoritmos/dados_coletados/` são:
- `paradas_onibus.json`
- `estacoes_metro.json`
- `linhas_onibus.json`
- `linhas_metro.json`
- `ciclovias.json`
- `vias_pedestres.json`
- `rede_viaria.json`

### Modelagem do grafo

- Nós de transporte são identificados como `bus:<id>` e `rail:<id>`.
- Arestas de caminhada conectam nós com distância ≤ `walkThresholdM` (default 200m).
- Arestas de ônibus (`mode='bus'`) e metrô (`mode='rail'`) seguem a ordem das paradas/estações.
- O grafo rodoviário é montado a partir de `rede_viaria.json` e suporta `car` e `moto`.

---

## Como usar

1. Inicie o backend:

```bash
cd backend
npm install
npm start
```

2. Inicie o frontend:

```bash
cd frontend
npm install
npm run dev
```

3. Acesse `http://localhost:5173`

4. As rotas são carregadas automaticamente pelos endpoints do backend.

---

## Limitações conhecidas

- O backend ainda usa origem/destino fixos definidos no serviço de grafo;
  o frontend apresenta a UI de busca, mas não muda a rota atual no backend.
- A chamada atual do frontend ignora o campo `mode` selecionado no `SearchBar`.
- A API expõe criação de nós/arestas de transporte apenas em memória, sem persistência de disco.

---

## Tecnologias usadas

- Python 3.x (`algoritmos`)
- Node.js + Express (`backend`)
- Vue 3 + Vite + Vuetify + Leaflet (`frontend`)
- OpenStreetMap / OSRM para geometrias de rotas
- Swagger UI para documentação da API
