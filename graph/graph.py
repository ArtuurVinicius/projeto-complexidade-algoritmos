import pickle
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Usar backend não-interativo
import networkx as nx
import numpy as np
from matplotlib.patches import Patch

# Carregar o grafo
def load_graph():
    with open('../transport_graph.gpickle', 'rb') as f:
        return pickle.load(f)

def plot_graph_basic():
    """Visualização básica do grafo usando matplotlib."""
    G = load_graph()
    
    # Extrair coordenadas para posicionamento
    pos = {}
    for node, data in G.nodes(data=True):
        if data.get('lat') is not None and data.get('lon') is not None:
            # Inverter lon/lat para x/y e ajustar escala
            pos[node] = (data['lon'], data['lat'])
    
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
    plt.savefig('transport_graph_viz.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('Visualização salva: transport_graph_viz.png')

def plot_route_example():
    """Visualizar uma rota específica encontrada pelos algoritmos."""
    G = load_graph()
    
    # Encontrar nós mais próximos da origem e destino
    def find_nearest_node(lat, lon):
        best = None
        best_d = float('inf')
        for n, d in G.nodes(data=True):
            if d.get('lat') is None:
                continue
            dist = ((lat - d['lat'])**2 + (lon - d['lon'])**2)**0.5
            if dist < best_d:
                best_d = dist
                best = n
        return best
    
    origin_node = find_nearest_node(-8.0631, -34.8771)  # Cinema São Luiz
    dest_node = find_nearest_node(-8.1197, -34.9014)    # Faculdade Nova Roma
    
    # Calcular rota usando Dijkstra
    try:
        path = nx.shortest_path(G, origin_node, dest_node, weight='time_s')
        print(f"Rota encontrada: {len(path)} nós")
        
        # Extrair coordenadas
        pos = {}
        for node, data in G.nodes(data=True):
            if data.get('lat') is not None and data.get('lon') is not None:
                pos[node] = (data['lon'], data['lat'])
        
        plt.figure(figsize=(12, 10))
        
        # Desenhar todo o grafo (background)
        nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=0.3, alpha=0.3)
        nx.draw_networkx_nodes(G, pos, node_color='lightgray', node_size=10, alpha=0.5)
        
        # Destacar a rota
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        path_nodes = path
        
        # Colorir arestas da rota por modo
        for u, v in path_edges:
            edge_data = G[u][v]
            # Pegar primeira aresta se houver múltiplas
            edge_attrs = list(edge_data.values())[0] if edge_data else {}
            mode = edge_attrs.get('mode', 'unknown')
            
            if mode == 'walk':
                color = 'green'
                width = 3
            elif mode == 'bus':
                color = 'blue'
                width = 4
            elif mode == 'rail':
                color = 'red'
                width = 5
            else:
                color = 'black'
                width = 3
                
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], 
                                 edge_color=color, width=width, alpha=0.8)
        
        # Destacar nós da rota
        nx.draw_networkx_nodes(G, pos, nodelist=path_nodes,
                             node_color='yellow', node_size=50, alpha=0.9)
        
        # Marcar origem e destino
        nx.draw_networkx_nodes(G, pos, nodelist=[origin_node],
                             node_color='green', node_size=150, alpha=1.0)
        nx.draw_networkx_nodes(G, pos, nodelist=[dest_node],
                             node_color='red', node_size=150, alpha=1.0)
        
        plt.title(f'Rota Ótima: Cinema São Luiz → Faculdade Nova Roma\n({len(path)} paradas)', 
                  fontsize=14, fontweight='bold')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        
        # Legenda para a rota
        legend_elements = [
            plt.Line2D([0], [0], color='green', linewidth=3, label='Caminhada'),
            plt.Line2D([0], [0], color='blue', linewidth=4, label='Ônibus'),
            plt.Line2D([0], [0], color='red', linewidth=5, label='Metrô'),
            plt.Line2D([0], [0], marker='o', color='green', linestyle='None', 
                      markersize=8, label='Origem'),
            plt.Line2D([0], [0], marker='o', color='red', linestyle='None', 
                      markersize=8, label='Destino'),
            plt.Line2D([0], [0], marker='o', color='yellow', linestyle='None', 
                      markersize=6, label='Rota')
        ]
        plt.legend(handles=legend_elements, loc='best')
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('route_visualization.png', dpi=300, bbox_inches='tight')
        plt.close()
        print('Visualização da rota salva: route_visualization.png')
        
        # Imprimir detalhes da rota
        print("\nDetalhes da rota:")
        total_time = 0
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            edge_data = G[u][v]
            edge_attrs = list(edge_data.values())[0] if edge_data else {}
            
            mode = edge_attrs.get('mode', 'unknown')
            time_s = edge_attrs.get('time_s', 0)
            distance_m = edge_attrs.get('distance_m', 0)
            total_time += time_s
            
            print(f"  {i+1:2d}. {mode:8s} - {time_s/60:5.1f} min, {distance_m:6.0f} m")
        
        print(f"\nTempo total: {total_time/60:.1f} minutos")
        
    except nx.NetworkXNoPath:
        print("Nenhuma rota encontrada entre origem e destino!")

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
    import sys
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "stats":
            analyze_graph_stats()
        elif action == "basic":
            plot_graph_basic()
        elif action == "route":
            plot_route_example()
        elif action == "all":
            print("Analisando grafo...")
            analyze_graph_stats()
            print("\nGerando visualização completa...")
            plot_graph_basic()
            print("\nGerando visualização da rota...")
            plot_route_example()
        else:
            print("Uso: python graph.py [stats|basic|route|all]")
    else:
        # Executar tudo por padrão
        print("Analisando grafo...")
        analyze_graph_stats()
        
        print("\nGerando visualização completa...")
        plot_graph_basic()
        
        print("\nGerando visualização da rota...")
        plot_route_example()
        
        print("\n=== ARQUIVOS GERADOS ===")
        print("- transport_graph_viz.png: Visualização completa do grafo")
        print("- route_visualization.png: Rota ótima Cinema São Luiz → Faculdade Nova Roma")
        print("\nPara executar partes específicas:")
        print("  python graph.py stats  - Apenas estatísticas")
        print("  python graph.py basic  - Visualização completa")
        print("  python graph.py route  - Visualização da rota")
