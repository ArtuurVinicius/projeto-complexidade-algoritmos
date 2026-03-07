import os
import json
import random
import copy
from datetime import datetime
import networkx as nx
from build_graph import build_graph, load_graph, GRAPH_FILE
from main import CINEMA_SAO_LUIZ, FACULDADE_NOVA_ROMA

# =============================
# Definição de cenários
# =============================

# Geração automática de cenários variados
def gerar_cenarios(n=20):
    dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    climas = ["sol", "chuva", "nublado"]
    fluxos = ["baixo", "medio", "alto", "muito_alto"]
    segurancas = ["alta", "normal", "baixa"]
    custos = ["baixo", "normal"]
    incidentes_possiveis = [[], ["via_principal"], ["evento_esportivo"], ["via_principal", "evento_esportivo"]]
    cenarios = []
    for i in range(n):
        dia = random.choice(dias)
        hora = random.choice(list(range(6, 23)))
        clima = random.choice(climas)
        fluxo = random.choice(fluxos)
        seguranca = random.choice(segurancas)
        custo = random.choice(custos)
        incidentes = random.choice(incidentes_possiveis)
        nome = f"{dia.title()}, {hora}h, {clima}, fluxo {fluxo}, seg {seguranca}, custo {custo}, inc {','.join(incidentes) if incidentes else 'nenhum'}"
        cenarios.append({
            "nome": nome,
            "dia_semana": dia,
            "hora": hora,
            "clima": clima,
            "incidentes": incidentes,
            "fluxo": fluxo,
            "seguranca": seguranca,
            "custo": custo
        })
    return cenarios

cenarios = gerar_cenarios(30)

# =============================
# Funções para modificar o grafo conforme o cenário
# =============================
def aplicar_cenario(G, cenario):
    G_sim = copy.deepcopy(G)
    for u, v, k, data in G_sim.edges(keys=True, data=True):
        # Variação de tempo por fluxo
        if cenario["fluxo"] == "alto":
            data["time_s"] *= 1.3
        elif cenario["fluxo"] == "muito_alto":
            data["time_s"] *= 1.6
        elif cenario["fluxo"] == "baixo":
            data["time_s"] *= 0.9
        # Clima
        if cenario["clima"] == "chuva":
            if data.get("mode") == "walk":
                data["time_s"] *= 1.5
            if data.get("mode") == "bike":
                data["time_s"] *= 1.3
        # Incidentes
        if "via_principal" in cenario["incidentes"] and data.get("tipo_via") == "primary":
            data["time_s"] *= 2.0
        if "evento_esportivo" in cenario["incidentes"] and data.get("tipo_via") == "secondary":
            data["time_s"] *= 1.5
        # Segurança
        if cenario["seguranca"] == "baixa" and data.get("tipo_via") == "pedestrian":
            data["risk"] = 1.0
        else:
            data["risk"] = 0.0
        # Custos
        if cenario["custo"] == "baixo":
            data["cost"] = 0.0
        else:
            data["cost"] = data.get("cost", 0.0)
    return G_sim

# =============================
# Função de simulação
# =============================
def simular_algoritmos(cenario, origem, destino):
    if os.path.exists(GRAPH_FILE):
        G = load_graph()
    else:
        G = build_graph(save=True)
    G_sim = aplicar_cenario(G, cenario)
    # Encontrar nós mais próximos
    def find_nearest_node(G, lat, lon):
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
    src = find_nearest_node(G_sim, origem['lat'], origem['lon'])
    dst = find_nearest_node(G_sim, destino['lat'], destino['lon'])
    resultados = {}
    # Dijkstra (menor tempo)
    try:
        path = nx.shortest_path(G_sim, src, dst, weight='time_s')
        tempo = sum(
            min([d.get('time_s', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        custo = sum(
            min([d.get('cost', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        risco = sum(
            min([d.get('risk', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        resultados['dijkstra'] = {
            'tempo_min': tempo/60,
            'custo': custo,
            'risco': risco,
            'n_nos': len(path)
        }
    except Exception as e:
        resultados['dijkstra'] = {'erro': str(e)}
    # A* (tempo)
    def heuristic(a, b):
        la = G_sim.nodes[a]
        lb = G_sim.nodes[b]
        return ((la['lat']-lb['lat'])**2 + (la['lon']-lb['lon'])**2)**0.5 / 0.000012
    try:
        path = nx.astar_path(G_sim, src, dst, heuristic=heuristic, weight='time_s')
        tempo = sum(
            min([d.get('time_s', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        custo = sum(
            min([d.get('cost', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        risco = sum(
            min([d.get('risk', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        resultados['astar'] = {
            'tempo_min': tempo/60,
            'custo': custo,
            'risco': risco,
            'n_nos': len(path)
        }
    except Exception as e:
        resultados['astar'] = {'erro': str(e)}
    # Multiobjetivo (tempo + risco + custo) com pesos diferentes
    # Pesos: tempo (0.7), risco (0.2), custo (0.1) - ajustável
    W = nx.DiGraph()
    peso_tempo = 0.7
    peso_risco = 0.2
    peso_custo = 0.1
    for u, v, data in G_sim.edges(data=True):
        comp = (
            peso_tempo * data.get('time_s', 0) +
            peso_risco * data.get('risk', 0) * 600 +  # risco em segundos equivalentes
            peso_custo * data.get('cost', 0) * 60      # custo em segundos equivalentes
        )
        if W.has_edge(u, v):
            if W[u][v]['weight'] > comp:
                W[u][v]['weight'] = comp
        else:
            W.add_edge(u, v, weight=comp)
    try:
        path = nx.shortest_path(W, src, dst, weight='weight')
        tempo = sum(
            min([d.get('time_s', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        custo = sum(
            min([d.get('cost', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        risco = sum(
            min([d.get('risk', 0) for d in G_sim[u][v].values()])
            for u, v in zip(path, path[1:])
        )
        resultados['multiobjetivo'] = {
            'tempo_min': tempo/60,
            'custo': custo,
            'risco': risco,
            'n_nos': len(path)
        }
    except Exception as e:
        resultados['multiobjetivo'] = {'erro': str(e)}
    return resultados

# =============================
# Rodar simulações para todos os cenários
# =============================
def rodar_simulacoes():
    origem = CINEMA_SAO_LUIZ
    destino = FACULDADE_NOVA_ROMA
    resultados = []
    for cenario in cenarios:
        print(f"Simulando: {cenario['nome']}")
        res = simular_algoritmos(cenario, origem, destino)
        resultados.append({"cenario": cenario["nome"], **res})
    # Salvar resultados
    with open("resultados_simulacoes.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print("Resultados salvos em resultados_simulacoes.json")

if __name__ == "__main__":
    rodar_simulacoes()
