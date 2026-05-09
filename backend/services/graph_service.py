import pickle
from uuid import uuid4
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import networkx as nx
import json

from backend.config import GRAPHS_STORE
from backend.storage import repository
from backend.utils.serialize import graph_to_d3

# Ensure DB initialized
repository.ensure_init()


def _save_graph_to_file(G: nx.Graph, graph_id: str) -> Path:
    GRAPHS_STORE.mkdir(parents=True, exist_ok=True)
    file_path = GRAPHS_STORE / f"{graph_id}.gpickle"
    with open(file_path, 'wb') as f:
        pickle.dump(G, f)
    return file_path


def _load_graph_from_file(file_path: Path) -> nx.Graph:
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def generate_graph(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a graph using existing build_graph logic from repo root.
    """
    # Import here to avoid circulars and heavy imports at module load
    from build_graph import build_graph

    walk_threshold = int(params.get('walk_threshold_m', 200))
    # generate graph in-memory
    G = build_graph(save=False, walk_threshold_m=walk_threshold)

    graph_id = uuid4().hex
    file_path = _save_graph_to_file(G, graph_id)

    # store metadata
    repository.create_graph_entry(graph_id, str(file_path), params, G.number_of_nodes(), G.number_of_edges())

    return {
        'id': graph_id,
        'filename': str(file_path),
        'nodes_count': G.number_of_nodes(),
        'edges_count': G.number_of_edges(),
    }


def list_graphs(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    total = repository.count_graph_entries()
    offset = (page - 1) * per_page
    rows = repository.list_graph_entries(offset=offset, limit=per_page)
    items = []
    for r in rows:
        items.append({
            'id': r['id'],
            'filename': r['filename'],
            'params': json_or_empty(r.get('params')),
            'created_at': r['created_at'],
            'nodes_count': r['nodes_count'],
            'edges_count': r['edges_count'],
        })
    return {'total': total, 'page': page, 'per_page': per_page, 'items': items}


def get_graph_entry(graph_id: str) -> Optional[Dict[str, Any]]:
    r = repository.get_graph_entry(graph_id)
    if not r:
        return None
    return {
        'id': r['id'],
        'filename': r['filename'],
        'params': json_or_empty(r.get('params')),
        'created_at': r['created_at'],
        'nodes_count': r['nodes_count'],
        'edges_count': r['edges_count'],
    }


def load_graph(graph_id: str) -> Optional[nx.Graph]:
    r = repository.get_graph_entry(graph_id)
    if not r:
        return None
    path = Path(r['filename'])
    if not path.exists():
        return None
    return _load_graph_from_file(path)


def delete_graph(graph_id: str) -> bool:
    return repository.delete_graph_entry(graph_id)


def graph_to_json(graph_id: str, max_nodes: int = 5000) -> Optional[Dict[str, Any]]:
    G = load_graph(graph_id)
    if G is None:
        return None
    return graph_to_d3(G, max_nodes=max_nodes)


def json_or_empty(s: Optional[str]):
    try:
        if not s:
            return {}
        return json.loads(s)
    except Exception:
        return {}
