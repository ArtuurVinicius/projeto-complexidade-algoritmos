import json
import pickle
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Usar backend não-interativo
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import Patch

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from best_routes import build_road_graph, generate_three_best_routes

GRAPH_PATH = BASE_DIR / 'transport_graph.gpickle'
BEST_ROUTES_PATH = BASE_DIR / 'dados_coletados' / 'best_routes.json'

def load_graph():
    """Carrega o grafo multimodal salvo em transport_graph.gpickle."""
    with open(GRAPH_PATH, 'rb') as f:
        return pickle.load(f)


def load_best_routes(force_regenerate=False):
    """Carrega as 3 melhores rotas e gera o arquivo se necessario."""
    if force_regenerate or not BEST_ROUTES_PATH.exists():
        return generate_three_best_routes(output_path=str(BEST_ROUTES_PATH))

    with open(BEST_ROUTES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _extract_positions(G):
    pos = {}
    for node, data in G.nodes(data=True):
        lat = data.get('lat')
        lon = data.get('lon')
        if lat is not None and lon is not None:
            pos[node] = (lon, lat)
    return pos

def plot_graph_basic():
    """Visualização básica do grafo usando matplotlib."""
    G = load_graph()
    
    # Extrair coordenadas para posicionamento
    pos = _extract_positions(G)
    
    plt.figure(figsize=(15, 12))
    
    # Separar nós por tipo
    bus_stops = [n for n, d in G.nodes(data=True) if d.get('type') == 'bus_stop']
    rail_stations = [n for n, d in G.nodes(data=True) if d.get('type') == 'rail_station']
    
    # Separar arestas por modo
    walk_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('mode') == 'walk']
    bus_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('mode') == 'bus']
    rail_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('mode') == 'rail']
    
    # Desenhar arestas (primeiro, para ficarem atrás dos nós)
    nx.draw_networkx_edges(G, pos, edgelist=walk_edges, 
                          edge_color='lightgray', width=0.5, alpha=0.6, label='Caminhada')
    nx.draw_networkx_edges(G, pos, edgelist=bus_edges,
                          edge_color='blue', width=1.0, alpha=0.7, label='Ônibus')
    nx.draw_networkx_edges(G, pos, edgelist=rail_edges,
                          edge_color='red', width=2.0, alpha=0.8, label='Metrô')
    
    # Desenhar nós
    nx.draw_networkx_nodes(G, pos, nodelist=bus_stops,
                          node_color='lightblue', node_size=20, alpha=0.8, label='Paradas de Ônibus')
    nx.draw_networkx_nodes(G, pos, nodelist=rail_stations,
                          node_color='orange', node_size=80, alpha=0.9, label='Estações de Metrô')
    
    # Destacar origem e destino
    origin_lat, origin_lon = -8.0631, -34.8771  # Cinema São Luiz
    dest_lat, dest_lon = -8.1197, -34.9014      # Faculdade Nova Roma
    
    plt.scatter([origin_lon], [origin_lat], c='green', s=200, marker='*', 
               label='Origem (Cinema São Luiz)', zorder=5)
    plt.scatter([dest_lon], [dest_lat], c='red', s=200, marker='*', 
               label='Destino (Faculdade Nova Roma)', zorder=5)
    
    plt.title('Grafo Multimodal de Transporte - Recife/PE\n(Cinema São Luiz → Faculdade Nova Roma)', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # Legenda
    legend_elements = [
        Patch(facecolor='lightblue', alpha=0.8, label=f'Paradas de Ônibus ({len(bus_stops)})'),
        Patch(facecolor='orange', alpha=0.9, label=f'Estações de Metrô ({len(rail_stations)})'),
        plt.Line2D([0], [0], color='lightgray', linewidth=2, alpha=0.6, label=f'Caminhada ({len(walk_edges)})'),
        plt.Line2D([0], [0], color='blue', linewidth=2, alpha=0.7, label=f'Ônibus ({len(bus_edges)})'),
        plt.Line2D([0], [0], color='red', linewidth=3, alpha=0.8, label=f'Metrô ({len(rail_edges)})'),
        plt.Line2D([0], [0], marker='*', color='green', linestyle='None', 
                  markersize=10, label='Origem'),
        plt.Line2D([0], [0], marker='*', color='red', linestyle='None', 
                  markersize=10, label='Destino')
    ]
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(BASE_DIR / 'transport_graph_viz.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('Visualização salva: transport_graph_viz.png')


def _plot_public_route(best_routes):
    """Plota a melhor rota de transporte publico sobre o grafo multimodal."""
    G = load_graph()
    route = next((r for r in best_routes['routes'] if r['modal'] == 'transporte_publico'), None)
    if route is None:
        raise ValueError('Rota de transporte publico nao encontrada em best_routes.json')

    path = route.get('path', [])
    if len(path) < 2:
        raise ValueError('Rota de transporte publico invalida (menos de 2 nos)')

    pos = _extract_positions(G)
    plt.figure(figsize=(12, 10))

    # Background do grafo completo
    nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=0.25, alpha=0.25)
    nx.draw_networkx_nodes(G, pos, node_color='lightgray', node_size=8, alpha=0.25)

    # Arestas da rota com cor por modal
    for u, v in zip(path, path[1:]):
        if not G.has_edge(u, v):
            continue
        edge_attrs = min(G[u][v].values(), key=lambda x: x.get('time_s', float('inf')))
        mode = edge_attrs.get('mode', 'unknown')
        if mode == 'walk':
            color = 'green'
            width = 2.0
        elif mode == 'bus':
            color = 'blue'
            width = 3.2
        elif mode == 'rail':
            color = 'red'
            width = 3.6
        else:
            color = 'black'
            width = 2.0
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=color, width=width, alpha=0.9)

    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='yellow', node_size=35, alpha=0.9)
    nx.draw_networkx_nodes(G, pos, nodelist=[path[0]], node_color='green', node_size=140, alpha=1.0)
    nx.draw_networkx_nodes(G, pos, nodelist=[path[-1]], node_color='red', node_size=140, alpha=1.0)

    plt.title(
        'Melhor Rota - Transporte Público\n'
        f"Tempo: {route['time_s'] / 60:.1f} min | Distância: {route['distance_m'] / 1000:.2f} km",
        fontsize=14,
        fontweight='bold',
    )
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, alpha=0.3)

    legend_elements = [
        plt.Line2D([0], [0], color='green', linewidth=2, label='Caminhada'),
        plt.Line2D([0], [0], color='blue', linewidth=3, label='Ônibus'),
        plt.Line2D([0], [0], color='red', linewidth=3, label='Metrô'),
        plt.Line2D([0], [0], marker='o', color='green', linestyle='None', markersize=8, label='Origem'),
        plt.Line2D([0], [0], marker='o', color='red', linestyle='None', markersize=8, label='Destino'),
    ]
    plt.legend(handles=legend_elements, loc='best')

    out = BASE_DIR / 'best_route_transporte_publico.png'
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Visualização salva: {out.name}')


def _plot_road_route(best_routes, modal):
    """Plota a melhor rota de carro ou moto sobre o grafo viario."""
    route = next((r for r in best_routes['routes'] if r['modal'] == modal), None)
    if route is None:
        raise ValueError(f'Rota de {modal} nao encontrada em best_routes.json')

    path = route.get('path', [])
    if len(path) < 2:
        raise ValueError(f'Rota de {modal} invalida (menos de 2 nos)')

    road_modal = 'car' if modal == 'carro_proprio' else 'moto'
    G = build_road_graph(road_modal)
    pos = _extract_positions(G)

    plt.figure(figsize=(12, 10))

    # Limita o fundo ao entorno da rota para evitar renderizacao muito pesada
    route_lats = [G.nodes[n]['lat'] for n in path if n in G.nodes]
    route_lons = [G.nodes[n]['lon'] for n in path if n in G.nodes]
    margin = 0.01
    min_lat = min(route_lats) - margin
    max_lat = max(route_lats) + margin
    min_lon = min(route_lons) - margin
    max_lon = max(route_lons) + margin

    def _inside_bbox(node_id):
        nd = G.nodes[node_id]
        return min_lat <= nd['lat'] <= max_lat and min_lon <= nd['lon'] <= max_lon

    bg_edges = [(u, v) for u, v in G.edges() if _inside_bbox(u) and _inside_bbox(v)]

    # Background viario (recorte local)
    nx.draw_networkx_edges(G, pos, edgelist=bg_edges, edge_color='lightgray', width=0.2, alpha=0.22)

    # Rota destacada
    route_edges = [(u, v) for u, v in zip(path, path[1:]) if G.has_edge(u, v)]
    route_color = 'darkorange' if modal == 'carro_proprio' else 'purple'
    nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color=route_color, width=2.8, alpha=0.95)
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='yellow', node_size=15, alpha=0.8)
    nx.draw_networkx_nodes(G, pos, nodelist=[path[0]], node_color='green', node_size=120, alpha=1.0)
    nx.draw_networkx_nodes(G, pos, nodelist=[path[-1]], node_color='red', node_size=120, alpha=1.0)

    titulo_modal = 'Carro Próprio' if modal == 'carro_proprio' else 'Moto'
    plt.title(
        f'Melhor Rota - {titulo_modal}\n'
        f"Tempo: {route['time_s'] / 60:.1f} min | Distância: {route['distance_m'] / 1000:.2f} km",
        fontsize=14,
        fontweight='bold',
    )
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, alpha=0.3)
    plt.xlim(min_lon, max_lon)
    plt.ylim(min_lat, max_lat)

    legend_elements = [
        plt.Line2D([0], [0], color='lightgray', linewidth=2, alpha=0.5, label='Rede viária'),
        plt.Line2D([0], [0], color=route_color, linewidth=3, label='Melhor rota'),
        plt.Line2D([0], [0], marker='o', color='green', linestyle='None', markersize=8, label='Origem'),
        plt.Line2D([0], [0], marker='o', color='red', linestyle='None', markersize=8, label='Destino'),
    ]
    plt.legend(handles=legend_elements, loc='upper right')

    suffix = 'carro' if modal == 'carro_proprio' else 'moto'
    out = BASE_DIR / f'best_route_{suffix}.png'
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Visualização salva: {out.name}')


def plot_best_routes(force_regenerate=False):
    """Gera os 3 grafos das melhores rotas: publico, carro e moto."""
    best_routes = load_best_routes(force_regenerate=force_regenerate)
    _plot_public_route(best_routes)
    _plot_road_route(best_routes, modal='carro_proprio')
    _plot_road_route(best_routes, modal='moto')

def plot_route_example():
    """Compatibilidade: plota a rota otima de transporte publico."""
    best_routes = load_best_routes(force_regenerate=False)
    _plot_public_route(best_routes)

def analyze_graph_stats():
    """Analisar estatísticas do grafo."""
    G = load_graph()
    
    print("=== ESTATÍSTICAS DO GRAFO ===")
    print(f"Nós: {G.number_of_nodes():,}")
    print(f"Arestas: {G.number_of_edges():,}")
    print(f"É direcionado: {G.is_directed()}")
    print(f"É multigraph: {G.is_multigraph()}")
    
    # Contar por tipo de nó
    node_types = {}
    for _, data in G.nodes(data=True):
        ntype = data.get('type', 'unknown')
        node_types[ntype] = node_types.get(ntype, 0) + 1
    
    print("\n=== TIPOS DE NÓS ===")
    for ntype, count in node_types.items():
        print(f"{ntype}: {count:,}")
    
    # Contar por modo de transporte
    edge_modes = {}
    for _, _, data in G.edges(data=True):
        mode = data.get('mode', 'unknown')
        edge_modes[mode] = edge_modes.get(mode, 0) + 1
    
    print("\n=== MODOS DE TRANSPORTE ===")
    for mode, count in edge_modes.items():
        print(f"{mode}: {count:,}")
    
    # Estatísticas de conectividade
    if G.is_directed():
        print(f"\nComponentes fortemente conectados: {nx.number_strongly_connected_components(G)}")
        print(f"Componentes fracamente conectados: {nx.number_weakly_connected_components(G)}")
    else:
        print(f"\nComponentes conectados: {nx.number_connected_components(G)}")
    
    # Grau dos nós
    degrees = [d for n, d in G.degree()]
    print(f"\nGrau médio: {np.mean(degrees):.2f}")
    print(f"Grau máximo: {np.max(degrees)}")
    print(f"Grau mínimo: {np.min(degrees)}")

if __name__ == "__main__":
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "stats":
            analyze_graph_stats()
        elif action == "basic":
            plot_graph_basic()
        elif action == "route":
            plot_route_example()
        elif action == "route_public":
            best_routes = load_best_routes(force_regenerate=False)
            _plot_public_route(best_routes)
        elif action == "route_car":
            best_routes = load_best_routes(force_regenerate=False)
            _plot_road_route(best_routes, modal='carro_proprio')
        elif action == "route_moto":
            best_routes = load_best_routes(force_regenerate=False)
            _plot_road_route(best_routes, modal='moto')
        elif action == "routes":
            plot_best_routes(force_regenerate=False)
        elif action == "routes_refresh":
            plot_best_routes(force_regenerate=True)
        elif action == "all":
            print("Analisando grafo...")
            analyze_graph_stats()
            print("\nGerando visualização completa...")
            plot_graph_basic()
            print("\nGerando visualizações das melhores rotas...")
            plot_best_routes(force_regenerate=False)
        else:
            print("Uso: python graph.py [stats|basic|route|route_public|route_car|route_moto|routes|routes_refresh|all]")
    else:
        # Executar tudo por padrão
        print("Analisando grafo...")
        analyze_graph_stats()
        
        print("\nGerando visualização completa...")
        plot_graph_basic()
        
        print("\nGerando visualizações das melhores rotas...")
        plot_best_routes(force_regenerate=False)
        
        print("\n=== ARQUIVOS GERADOS ===")
        print("- transport_graph_viz.png: Visualização completa do grafo")
        print("- best_route_transporte_publico.png: Melhor rota de transporte público")
        print("- best_route_carro.png: Melhor rota de carro próprio")
        print("- best_route_moto.png: Melhor rota de moto")
        print("\nPara executar partes específicas:")
        print("  python graph.py stats  - Apenas estatísticas")
        print("  python graph.py basic  - Visualização completa")
        print("  python graph.py routes - Todas as 3 melhores rotas")
