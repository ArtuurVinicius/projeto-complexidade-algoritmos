import networkx as nx
import math
import os
from build_graph import build_graph, load_graph, GRAPH_FILE
from main import CINEMA_SAO_LUIZ, FACULDADE_NOVA_ROMA


def haversine(a_lat, a_lon, b_lat, b_lon):
    R = 6371000.0
    phi1 = math.radians(a_lat)
    phi2 = math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlambda = math.radians(b_lon - a_lon)
    x = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    return 2 * R * math.atan2(math.sqrt(x), math.sqrt(1-x))


def find_nearest_node(G, lat, lon):
    best = None
    best_d = float('inf')
    for n, d in G.nodes(data=True):
        if d.get('lat') is None:
            continue
        dist = haversine(lat, lon, d['lat'], d['lon'])
        if dist < best_d:
            best_d = dist
            best = n
    return best, best_d


def run_examples():
    # Tentar carregar grafo salvo primeiro
    if os.path.exists(GRAPH_FILE):
        print(f"Carregando grafo salvo de {GRAPH_FILE}...")
        G = load_graph()
    else:
        print("Construindo grafo (arquivo não encontrado)...")
        G = build_graph(save=False)
    
    src_node, src_dist = find_nearest_node(G, CINEMA_SAO_LUIZ['lat'], CINEMA_SAO_LUIZ['lon'])
    dst_node, dst_dist = find_nearest_node(G, FACULDADE_NOVA_ROMA['lat'], FACULDADE_NOVA_ROMA['lon'])
    print(f"Origem nó: {src_node} (dist {src_dist:.1f} m)")
    print(f"Destino nó: {dst_node} (dist {dst_dist:.1f} m)")

    # Dijkstra (menor tempo) usando atributo 'time_s'
    try:
        path = nx.shortest_path(G, src_node, dst_node, weight='time_s')
        total_time = 0.0
        for u, v in zip(path, path[1:]):
            # escolher a aresta com menor time_s entre múltiplas arestas
            times = [d.get('time_s', float('inf')) for d in G[u][v].values()]
            total_time += min(times) if times else 0.0
        print(f"Caminho Dijkstra (tempo) encontrado, nós: {len(path)}, tempo ≈ {total_time/60:.2f} min")
    except Exception as e:
        print(f"Erro Dijkstra: {e}")

    # A* com heurística haversine / walking speed (optimista)
    def heuristic(a, b):
        la = G.nodes[a]
        lb = G.nodes[b]
        return haversine(la['lat'], la['lon'], lb['lat'], lb['lon']) / 1.4

    try:
        path_astar = nx.astar_path(G, src_node, dst_node, heuristic=heuristic, weight='time_s')
        print(f"Caminho A* (tempo) nós: {len(path_astar)}")
    except Exception as e:
        print(f"Erro A*: {e}")

    # Exemplo multiobjetivo: criar grafo simples com peso composto
    W = nx.DiGraph()
    w_time = 1.0
    w_cost = 0.0
    w_emissions = 0.0
    for u, v, data in G.edges(data=True):
        # pegar menor tempo se multiplas arestas
        time_s = data.get('time_s', 0)
        cost = data.get('cost', 0.0)
        emissions = data.get('emissions', 0.0)
        comp = w_time * time_s + w_cost * cost + w_emissions * emissions
        # manter menor comp se já existir
        if W.has_edge(u, v):
            if W[u][v]['weight'] > comp:
                W[u][v]['weight'] = comp
        else:
            W.add_edge(u, v, weight=comp)

    try:
        path_comp = nx.shortest_path(W, src_node, dst_node, weight='weight')
        print(f"Caminho (peso composto) nós: {len(path_comp)}")
    except Exception as e:
        print(f"Erro multiobjetivo (comp.): {e}")


if __name__ == '__main__':
    run_examples()
