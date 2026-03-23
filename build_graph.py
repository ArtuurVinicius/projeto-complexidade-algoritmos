import json
import os
import math
import pickle
from collections import defaultdict

try:
    import networkx as nx
except ImportError:
    raise ImportError("networkx is required: pip install networkx")

try:
    from scipy.spatial import cKDTree
    _HAVE_KDTREE = True
except Exception:
    _HAVE_KDTREE = False

DATA_DIR = "dados_coletados"
GRAPH_FILE = "transport_graph.gpickle"


def haversine(a_lat, a_lon, b_lat, b_lon):
    # returns distance in meters
    R = 6371000.0
    phi1 = math.radians(a_lat)
    phi2 = math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlambda = math.radians(b_lon - a_lon)
    x = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    return 2 * R * math.atan2(math.sqrt(x), math.sqrt(1-x))


def load_json(name):
    path = os.path.join(DATA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_graph():
    """Carrega o grafo salvo do arquivo pickle."""
    with open(GRAPH_FILE, 'rb') as f:
        return pickle.load(f)


def build_graph(save=True, walk_threshold_m=200):
    """Constrói um grafo multimodal a partir dos JSONs em `dados_coletados`.

    - Nós: paradas e estações (ids prefixados)
    - Arestas: caminhada (entre nós próximos), ônibus/metro (sequência das linhas), ciclovias/rede_viaria (opcionais)
    """
    stops = load_json("paradas_onibus.json")
    stations = load_json("estacoes_metro.json")
    bus_lines = load_json("linhas_onibus.json")
    rail_lines = load_json("linhas_metro.json")

    G = nx.MultiDiGraph()

    # Add stop nodes
    def add_node(prefix, el, ntype):
        nid = f"{prefix}:{el['id']}"
        G.add_node(nid, lat=el.get("lat"), lon=el.get("lon"), name=el.get("nome", ""), type=ntype)
        return nid

    stop_nodes = {}
    for s in stops:
        stop_nodes[s["id"]] = add_node("bus", s, "bus_stop")

    station_nodes = {}
    for s in stations:
        station_nodes[s["id"]] = add_node("rail", s, "rail_station")

    # Combine node coords for spatial index
    node_ids = []
    coords = []
    for n, d in G.nodes(data=True):
        if d.get("lat") is None:
            continue
        node_ids.append(n)
        coords.append((d["lat"], d["lon"]))

    # Build KDTree if available
    tree = None
    if _HAVE_KDTREE and coords:
        latlons = [(lat, lon) for lat, lon in coords]
        # KDTree expects (x,y) cartesian; we will convert lat/lon to radians-projected approx using lat*111km
        pts = [(lat * 111000.0, lon * 111000.0 * math.cos(math.radians(lat))) for lat, lon in latlons]
        tree = cKDTree(pts)

    def nearest_nodes(lat, lon, radius_m):
        res = []
        if tree is not None:
            q = (lat * 111000.0, lon * 111000.0 * math.cos(math.radians(lat)))
            idxs = tree.query_ball_point(q, r=radius_m)
            for i in idxs:
                res.append(node_ids[i])
            return res
        # fallback brute force
        for nid in node_ids:
            d = G.nodes[nid]
            dist = haversine(lat, lon, d["lat"], d["lon"])
            if dist <= radius_m:
                res.append(nid)
        return res

    # Add walking edges between nearby nodes (undirected -> two directed edges)
    # For performance, we only connect nodes within walk_threshold_m
    for i, nid in enumerate(node_ids):
        lat1, lon1 = coords[i]
        neighbors = []
        if tree is not None:
            q = (lat1 * 111000.0, lon1 * 111000.0 * math.cos(math.radians(lat1)))
            idxs = tree.query_ball_point(q, r=walk_threshold_m)
            neighbors = [node_ids[j] for j in idxs if node_ids[j] != nid]
        else:
            for j, other in enumerate(node_ids):
                if other == nid:
                    continue
                lat2, lon2 = coords[j]
                if haversine(lat1, lon1, lat2, lon2) <= walk_threshold_m:
                    neighbors.append(other)
        for nbr in neighbors:
            if G.has_edge(nid, nbr):
                pass
            lat2 = G.nodes[nbr]["lat"]
            lon2 = G.nodes[nbr]["lon"]
            dist = haversine(lat1, lon1, lat2, lon2)
            walk_speed = 1.4  # m/s
            time_s = dist / walk_speed
            G.add_edge(nid, nbr, mode="walk", distance_m=dist, time_s=time_s, cost=0.0)

    # Helper: create transit edges from line sequences
    def add_line_edges(lines, prefix, speed_m_s=8.0, mode_name="bus"):
        for line in lines:
            seq = line.get("paradas") or line.get("estacoes") or []
            # map members to nearest nodes
            node_seq = []
            for member in seq:
                lat = member.get("lat")
                lon = member.get("lon")
                # find nearest node within small radius
                cand = nearest_nodes(lat, lon, radius_m=50)
                if cand:
                    node_seq.append(cand[0])
            for a, b in zip(node_seq, node_seq[1:]):
                la = G.nodes[a]
                lb = G.nodes[b]
                dist = haversine(la["lat"], la["lon"], lb["lat"], lb["lon"])
                t = max(5.0, dist / speed_m_s)
                G.add_edge(a, b, mode=mode_name, distance_m=dist, time_s=t, route=line.get("ref",""), cost=0.0)

    add_line_edges(bus_lines, "bus", speed_m_s=8.0, mode_name="bus")
    add_line_edges(rail_lines, "rail", speed_m_s=15.0, mode_name="rail")

    if save:
        with open(GRAPH_FILE, 'wb') as f:
            pickle.dump(G, f)
        print(f"Grafo salvo em: {GRAPH_FILE}")

    return G


if __name__ == "__main__":
    print("Construindo grafo multimodal a partir dos dados coletados...")
    g = build_graph()
    print(f"Nós: {g.number_of_nodes()}, Arestas: {g.number_of_edges()}")
