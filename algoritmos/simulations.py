"""Simulações de desempenho de roteamento em diferentes cenários.

Gera métrricas de tempo/distância/modos usadas para combinações de:
- Dias: segunda, quarta, sexta, domingo
- Horários: morning, midday, evening
- Clima: dia ensolarado, chuva, alagamentos

Salva resultados em `dados_coletados/simulations_results.json`.
"""
import os
import json
import math
from collections import Counter

import pickle
import networkx as nx

DATA_DIR = "dados_coletados"
GRAPH_FILE = "transport_graph.gpickle"

# Origem / destino (mesmos do `main.py`)
ORIGIN = {"lat": -8.0631, "lon": -34.8771, "name": "Cinema São Luiz"}
DEST = {"lat": -8.1197, "lon": -34.9014, "name": "Faculdade Nova Roma"}


def load_graph(path=GRAPH_FILE):
    with open(path, "rb") as f:
        return pickle.load(f)


def find_nearest_node(G, lat, lon):
    best = None
    best_d = float("inf")
    for n, d in G.nodes(data=True):
        if d.get("lat") is None:
            continue
        # simples distância euclidiana em graus (apenas para busca)
        dist = math.hypot(lat - d["lat"], lon - d["lon"])
        if dist < best_d:
            best_d = dist
            best = n
    return best


def build_scenario_graph(G, day, weather, time_of_day):
    """Retorna um grafo direcionado (não multi) com tempos ajustados por cenário.

    Estratégia: iterar sobre arestas de G (MultiDiGraph) e adicionar ao Gs
    um único arco com `time_s_adj` calculado a partir de multiplicadores.
    """
    Gs = nx.DiGraph()

    # Base multipliers
    weather = weather.lower()
    day_low = day.lower()
    tod = time_of_day.lower()

    # weather multipliers per mode
    weather_map = {
        "dia ensolarado": {"walk": 1.0, "bus": 1.0, "rail": 1.0},
        "chuva": {"walk": 1.5, "bus": 1.1, "rail": 1.05},
        "alagamentos": {"walk": 10.0, "bus": 1.3, "rail": 1.2},
    }

    # day/time multipliers (peak effects)
    def day_time_multiplier(day, tod, mode):
        # weekdays heavier in morning/evening for buses
        weekdays = {"segunda", "quarta", "sexta"}
        if mode in ("bus", "rail"):
            if day in weekdays and tod in ("morning", "evening"):
                return 1.25
            if day == "domingo":
                return 0.9
        # walking somewhat unaffected except floods handled in weather_map
        return 1.0

    wmap = weather_map.get(weather, weather_map["dia ensolarado"])

    # iterate nodes to copy attributes
    for n, d in G.nodes(data=True):
        Gs.add_node(n, **d)

    for u, v, key, attrs in G.edges(keys=True, data=True):
        base_time = attrs.get("time_s", None)
        dist = attrs.get("distance_m", attrs.get("distance", 0))
        mode = attrs.get("mode", "unknown")
        if base_time is None:
            # fallback: estimate by speed by mode
            if mode == "walk":
                speed = 1.4
            elif mode == "bus":
                speed = 8.0
            elif mode == "rail":
                speed = 15.0
            else:
                speed = 5.0
            base_time = max(1.0, dist / speed)

        # select mode key for multipliers
        mkey = "walk" if mode == "walk" else ("bus" if mode == "bus" else ("rail" if mode == "rail" else mode))

        weather_mul = wmap.get(mkey, 1.0)
        dt_mul = day_time_multiplier(day_low, tod, mkey)

        time_adj = base_time * weather_mul * dt_mul

        # For alagamentos we consider some walking edges effectively unusable by setting huge time
        if weather == "alagamentos" and mkey == "walk":
            time_adj = base_time * weather_mul * dt_mul

        # Add / keep minimal edge if multiple edges collapse to same (u,v)
        if Gs.has_edge(u, v):
            if Gs[u][v]["time_s_adj"] > time_adj:
                Gs[u][v]["time_s_adj"] = time_adj
                Gs[u][v]["distance_m"] = dist
                Gs[u][v]["mode"] = mode
        else:
            Gs.add_edge(u, v, time_s_adj=time_adj, distance_m=dist, mode=mode)

    return Gs


def extract_path_metrics(Gs, path):
    total_time = 0.0
    total_dist = 0.0
    modes = []
    for a, b in zip(path, path[1:]):
        if not Gs.has_edge(a, b):
            continue
        e = Gs[a][b]
        total_time += e.get("time_s_adj", 0)
        total_dist += e.get("distance_m", 0)
        modes.append(e.get("mode", "unknown"))
    return total_time, total_dist, dict(Counter(modes))


def run_all(sim_output_path=None):
    G = load_graph(GRAPH_FILE)

    days = ["segunda", "quarta", "sexta", "domingo"]
    weathers = ["dia ensolarado", "chuva", "alagamentos"]
    times = ["morning", "midday", "evening"]

    origin_node = find_nearest_node(G, ORIGIN["lat"], ORIGIN["lon"])
    dest_node = find_nearest_node(G, DEST["lat"], DEST["lon"])

    if sim_output_path is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        sim_output_path = os.path.join(DATA_DIR, "simulations_results.json")

    results = []

    for day in days:
        for weather in weathers:
            for tod in times:
                scenario = {"day": day, "weather": weather, "time_of_day": tod}
                Gs = build_scenario_graph(G, day, weather, tod)
                try:
                    path = nx.shortest_path(Gs, origin_node, dest_node, weight="time_s_adj")
                    n_nodes = len(path)
                    t_s, d_m, modes = extract_path_metrics(Gs, path)
                    result = {
                        "scenario": scenario,
                        "found": True,
                        "n_nodes": n_nodes,
                        "time_s": t_s,
                        "distance_m": d_m,
                        "modes": modes,
                    }
                except nx.NetworkXNoPath:
                    result = {
                        "scenario": scenario,
                        "found": False,
                        "n_nodes": 0,
                        "time_s": None,
                        "distance_m": None,
                        "modes": {},
                    }
                results.append(result)

    with open(sim_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # quick summary print
    total = len(results)
    found = sum(1 for r in results if r["found"])
    print(f"Simulações concluídas: {total} cenários (rotas encontradas: {found})")
    print(f"Resultados salvos em: {sim_output_path}")

    return results


if __name__ == "__main__":
    run_all()
