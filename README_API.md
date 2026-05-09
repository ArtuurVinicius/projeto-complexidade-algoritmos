# Transport Graphs Backend (FastAPI)

This backend exposes endpoints to generate, store and retrieve multimodal transport graphs built from the existing data files.

Run locally (recommended in a virtualenv):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Available endpoints (prefix `/grafos`):

- `POST /grafos/gerar` - body: `{ "walk_threshold_m": 200 }` — gera um grafo e retorna metadados com `id`.
- `GET /grafos` - lista grafos (query `page`, `per_page`).
- `GET /grafos/{id}` - retorna o grafo em JSON (D3-like). Use `?format=gpickle` para baixar o arquivo `.gpickle`.
- `DELETE /grafos/{id}` - deleta grafo salvo.

Notes:
- Graphs are stored under `graphs_store/` and metadata in a SQLite DB at `graphs_store/graphs.db`.
- The API serializes graphs to a D3/Cytoscape-friendly JSON (`nodes` and `links`). For very large graphs, use the `max_nodes` query param or download the `.gpickle` and process client-side.
