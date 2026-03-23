"""Gera as 3 melhores rotas: transporte publico, carro e moto.

Saida:
- dados_coletados/best_routes.json
"""

import json
import math
import pickle
from collections import Counter
from pathlib import Path

import networkx as nx

from main import CINEMA_SAO_LUIZ, FACULDADE_NOVA_ROMA

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dados_coletados"
TRANSPORT_GRAPH_FILE = BASE_DIR / "transport_graph.gpickle"
ROAD_FILE = DATA_DIR / "rede_viaria.json"
OUTPUT_FILE = DATA_DIR / "best_routes.json"


def haversine(a_lat, a_lon, b_lat, b_lon):
    """Distancia em metros entre duas coordenadas."""
    r = 6371000.0
    phi1 = math.radians(a_lat)
    phi2 = math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlambda = math.radians(b_lon - a_lon)
    x = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2 * r * math.atan2(math.sqrt(x), math.sqrt(1 - x))


def load_transport_graph(path=TRANSPORT_GRAPH_FILE):
    with open(path, "rb") as f:
        return pickle.load(f)


def load_road_data(path=ROAD_FILE):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_maxspeed_kmh(value, fallback_kmh):
    if not value:
        return fallback_kmh
    text = str(value).strip().lower()

    for part in text.replace(";", " ").replace(",", " ").split():
        cleaned = "".join(ch for ch in part if ch.isdigit() or ch == ".")
        if not cleaned:
            continue
        try:
            speed = float(cleaned)
            if speed > 0:
                return speed
        except ValueError:
            continue
    return fallback_kmh


def find_nearest_node(G, lat, lon):
    best = None
    best_d = float("inf")
    for n, data in G.nodes(data=True):
        nlat = data.get("lat")
        nlon = data.get("lon")
        if nlat is None or nlon is None:
            continue
        d = haversine(lat, lon, nlat, nlon)
        if d < best_d:
            best = n
            best_d = d
    return best, best_d


def build_road_graph(modal):
    """Monta um DiGraph de vias para carro ou moto.

    - modal='car': rota de carro proprio
    - modal='moto': rota de moto
    """
    roads = load_road_data()
    G = nx.DiGraph()

    # Limites realistas para area urbana
    modal_default_kmh = 30.0 if modal == "car" else 36.0
    modal_cap_kmh = 55.0 if modal == "car" else 65.0

    for way in roads:
        geom = way.get("geometria", [])
        if len(geom) < 2:
            continue

        oneway_text = str(way.get("mao_unica", "")).lower()
        is_oneway = oneway_text in {"yes", "1", "true"}

        raw_kmh = parse_maxspeed_kmh(way.get("velocidade_max", ""), fallback_kmh=modal_default_kmh)
        speed_kmh = min(raw_kmh, modal_cap_kmh)
        speed_ms = max(1.0, speed_kmh / 3.6)

        for a, b in zip(geom, geom[1:]):
            a_lat, a_lon = a.get("lat"), a.get("lon")
            b_lat, b_lon = b.get("lat"), b.get("lon")
            if None in (a_lat, a_lon, b_lat, b_lon):
                continue

            a_node = f"{a_lat:.6f},{a_lon:.6f}"
            b_node = f"{b_lat:.6f},{b_lon:.6f}"

            if not G.has_node(a_node):
                G.add_node(a_node, lat=a_lat, lon=a_lon)
            if not G.has_node(b_node):
                G.add_node(b_node, lat=b_lat, lon=b_lon)

            dist = haversine(a_lat, a_lon, b_lat, b_lon)
            time_s = dist / speed_ms

            edge_attrs = {
                "mode": modal,
                "distance_m": dist,
                "time_s": time_s,
                "road_type": way.get("tipo_via", ""),
                "road_name": way.get("nome", ""),
            }

            # Mantem apenas o melhor tempo entre os mesmos nos
            if G.has_edge(a_node, b_node):
                if G[a_node][b_node]["time_s"] > time_s:
                    G[a_node][b_node].update(edge_attrs)
            else:
                G.add_edge(a_node, b_node, **edge_attrs)

            if not is_oneway:
                if G.has_edge(b_node, a_node):
                    if G[b_node][a_node]["time_s"] > time_s:
                        G[b_node][a_node].update(edge_attrs)
                else:
                    G.add_edge(b_node, a_node, **edge_attrs)

    return G


def summarize_path_multigraph(G, path):
    total_time = 0.0
    total_dist = 0.0
    modes = []

    for u, v in zip(path, path[1:]):
        if not G.has_edge(u, v):
            continue
        edges = list(G[u][v].values())
        best = min(edges, key=lambda e: e.get("time_s", float("inf")))
        total_time += best.get("time_s", 0.0)
        total_dist += best.get("distance_m", 0.0)
        modes.append(best.get("mode", "unknown"))

    return {
        "total_time_s": total_time,
        "total_distance_m": total_dist,
        "modes": dict(Counter(modes)),
    }


def summarize_path_digraph(G, path):
    total_time = 0.0
    total_dist = 0.0

    for u, v in zip(path, path[1:]):
        if not G.has_edge(u, v):
            continue
        e = G[u][v]
        total_time += e.get("time_s", 0.0)
        total_dist += e.get("distance_m", 0.0)

    return {
        "total_time_s": total_time,
        "total_distance_m": total_dist,
        "modes": {G[path[0]][path[1]].get("mode", "unknown"): len(path) - 1} if len(path) > 1 else {},
    }


def path_to_coords(G, path):
    coords = []
    for node in path:
        data = G.nodes[node]
        coords.append({"lat": data.get("lat"), "lon": data.get("lon")})
    return coords


def compute_public_transport_route(origin, destination):
    G = load_transport_graph()

    src, src_d = find_nearest_node(G, origin["lat"], origin["lon"])
    dst, dst_d = find_nearest_node(G, destination["lat"], destination["lon"])

    path = nx.shortest_path(G, src, dst, weight="time_s")
    summary = summarize_path_multigraph(G, path)

    return {
        "modal": "transporte_publico",
        "start_node": src,
        "end_node": dst,
        "origin_to_network_m": src_d,
        "destination_to_network_m": dst_d,
        "n_nodes": len(path),
        "time_s": summary["total_time_s"],
        "distance_m": summary["total_distance_m"],
        "modes": summary["modes"],
        "path": path,
        "coordinates": path_to_coords(G, path),
    }


def compute_road_route(origin, destination, modal):
    G = build_road_graph(modal)

    src, src_d = find_nearest_node(G, origin["lat"], origin["lon"])
    dst, dst_d = find_nearest_node(G, destination["lat"], destination["lon"])

    path = nx.shortest_path(G, src, dst, weight="time_s")
    summary = summarize_path_digraph(G, path)

    return {
        "modal": "carro_proprio" if modal == "car" else "moto",
        "start_node": src,
        "end_node": dst,
        "origin_to_network_m": src_d,
        "destination_to_network_m": dst_d,
        "n_nodes": len(path),
        "time_s": summary["total_time_s"],
        "distance_m": summary["total_distance_m"],
        "modes": summary["modes"],
        "path": path,
        "coordinates": path_to_coords(G, path),
    }


def generate_three_best_routes(output_path=OUTPUT_FILE):
    output_path = Path(output_path)
    if not output_path.is_absolute():
        output_path = BASE_DIR / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    origin = {"lat": CINEMA_SAO_LUIZ["lat"], "lon": CINEMA_SAO_LUIZ["lon"], "name": CINEMA_SAO_LUIZ["nome"]}
    destination = {"lat": FACULDADE_NOVA_ROMA["lat"], "lon": FACULDADE_NOVA_ROMA["lon"], "name": FACULDADE_NOVA_ROMA["nome"]}

    result = {
        "origin": origin,
        "destination": destination,
        "routes": [
            compute_public_transport_route(origin, destination),
            compute_road_route(origin, destination, modal="car"),
            compute_road_route(origin, destination, modal="moto"),
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"3 rotas geradas com sucesso: {output_path}")
    for route in result["routes"]:
        print(
            f"- {route['modal']}: {route['time_s'] / 60:.1f} min, "
            f"{route['distance_m'] / 1000:.2f} km, {route['n_nodes']} nos"
        )

    return result


if __name__ == "__main__":
    generate_three_best_routes()
