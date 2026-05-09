from typing import Dict, Any
import networkx as nx


def graph_to_d3(G: nx.Graph, max_nodes: int = 5000) -> Dict[str, Any]:
    nodes = []
    for i, (n, data) in enumerate(G.nodes(data=True)):
        if i >= max_nodes:
            break
        node = {
            'id': str(n),
            'label': data.get('name') or str(n),
            'type': data.get('type'),
        }
        # include coordinates if present
        if 'lat' in data and 'lon' in data:
            node['lat'] = data.get('lat')
            node['lon'] = data.get('lon')
        node.update({k: v for k, v in data.items() if k not in ('name', 'type', 'lat', 'lon')})
        nodes.append(node)

    edges = []
    for i, (u, v, data) in enumerate(G.edges(data=True)):
        if i >= max_nodes * 5:
            break
        edge = {
            'source': str(u),
            'target': str(v),
            'mode': data.get('mode'),
            'distance_m': data.get('distance_m'),
            'time_s': data.get('time_s'),
        }
        edge.update({k: v for k, v in data.items() if k not in ('mode', 'distance_m', 'time_s')})
        edges.append(edge)

    return {'nodes': nodes, 'links': edges, 'nodes_total': G.number_of_nodes(), 'edges_total': G.number_of_edges()}
