const fs = require('fs');
const path = require('path');

const osrmService = require('./osrmService');

const ROOT_DIR = path.resolve(__dirname, '..', '..', '..');
const ALG_DIR = process.env.ALGORITMOS_DIR
  ? path.resolve(process.env.ALGORITMOS_DIR)
  : path.join(ROOT_DIR, 'algoritmos');
const DATA_DIR = path.join(ALG_DIR, 'dados_coletados');

const DEFAULT_WALK_THRESHOLD_M = 200;

const ORIGIN = {
  lat: -8.0631,
  lon: -34.8771,
  name: 'Cinema Sao Luiz (Boa Vista)',
};
const DESTINATION = {
  lat: -8.1197,
  lon: -34.9014,
  name: 'Faculdade Nova Roma (Boa Viagem)',
};

// Cost parameters (BRL)
const GAS_PRICE = 7.05; // R$ per liter
const CAR_CONSUMPTION_KM_PER_L = 12.0; // km per liter
const MOTO_CONSUMPTION_KM_PER_L = 40.0; // km per liter
const BUS_FARE = 4.5; // R$ per passage

const cache = {
  transport: null,
  road: {
    car: null,
    moto: null,
  },
};

function createError(statusCode, message) {
  const err = new Error(message);
  err.statusCode = statusCode;
  return err;
}

function loadJson(fileName) {
  const filePath = path.join(DATA_DIR, fileName);
  if (!fs.existsSync(filePath)) {
    throw createError(500, `Missing data file: ${filePath}`);
  }
  const raw = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(raw);
}

function haversine(aLat, aLon, bLat, bLon) {
  const r = 6371000.0;
  const phi1 = (aLat * Math.PI) / 180;
  const phi2 = (bLat * Math.PI) / 180;
  const dphi = ((bLat - aLat) * Math.PI) / 180;
  const dlambda = ((bLon - aLon) * Math.PI) / 180;
  const x =
    Math.sin(dphi / 2.0) ** 2 +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(dlambda / 2.0) ** 2;
  return 2 * r * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
}

function createGraphState(type, meta) {
  return {
    type,
    nodes: new Map(),
    nodeOrder: [],
    edges: [],
    nextEdgeId: 1,
    meta: {
      ...meta,
      builtAt: new Date().toISOString(),
    },
  };
}

function addEdge(graph, from, to, attrs) {
  const edge = {
    id: graph.nextEdgeId++,
    from,
    to,
    ...attrs,
  };
  graph.edges.push(edge);
  return edge;
}

function graphToJson(graph) {
  return {
    type: graph.type,
    meta: {
      ...graph.meta,
      nodeCount: graph.nodes.size,
      edgeCount: graph.edges.length,
    },
    nodes: Array.from(graph.nodes.values()),
    edges: graph.edges,
  };
}

function buildTransportGraphState(options) {
  const walkThresholdM = options.walkThresholdM || DEFAULT_WALK_THRESHOLD_M;
  const stops = loadJson('paradas_onibus.json');
  const stations = loadJson('estacoes_metro.json');
  const busLines = loadJson('linhas_onibus.json');
  const railLines = loadJson('linhas_metro.json');

  const graph = createGraphState('transport', {
    walkThresholdM,
    origin: ORIGIN,
    destination: DESTINATION,
  });

  const nodeIds = graph.nodeOrder;
  const coords = [];

  function addNode(prefix, element, type) {
    const id = `${prefix}:${element.id}`;
    const node = {
      id,
      lat: element.lat,
      lon: element.lon,
      name: element.nome || '',
      type,
    };
    graph.nodes.set(id, node);
    nodeIds.push(id);
    coords.push({ lat: node.lat, lon: node.lon });
    return id;
  }

  stops.forEach((stop) => addNode('bus', stop, 'bus_stop'));
  stations.forEach((station) => addNode('rail', station, 'rail_station'));

  function nearestNodesInRadius(lat, lon, radiusM) {
    const results = [];
    for (let i = 0; i < nodeIds.length; i += 1) {
      const coord = coords[i];
      if (!coord || coord.lat === undefined || coord.lon === undefined) {
        continue;
      }
      const dist = haversine(lat, lon, coord.lat, coord.lon);
      if (dist <= radiusM) {
        results.push(nodeIds[i]);
      }
    }
    return results;
  }

  for (let i = 0; i < nodeIds.length; i += 1) {
    const fromCoord = coords[i];
    if (!fromCoord || fromCoord.lat === undefined || fromCoord.lon === undefined) {
      continue;
    }
    for (let j = 0; j < nodeIds.length; j += 1) {
      if (i === j) {
        continue;
      }
      const toCoord = coords[j];
      if (!toCoord || toCoord.lat === undefined || toCoord.lon === undefined) {
        continue;
      }
      const dist = haversine(fromCoord.lat, fromCoord.lon, toCoord.lat, toCoord.lon);
      if (dist <= walkThresholdM) {
        const timeS = dist / 1.4;
        addEdge(graph, nodeIds[i], nodeIds[j], {
          mode: 'walk',
          distance_m: dist,
          time_s: timeS,
          cost: 0.0,
        });
      }
    }
  }

  function addLineEdges(lines, speedMs, modeName) {
    lines.forEach((line) => {
      const seq = line.paradas || line.estacoes || [];
      const nodeSeq = [];

      seq.forEach((member) => {
        const lat = member.lat;
        const lon = member.lon;
        if (lat === undefined || lon === undefined) {
          return;
        }
        const candidates = nearestNodesInRadius(lat, lon, 50);
        if (candidates.length > 0) {
          nodeSeq.push(candidates[0]);
        }
      });

      for (let i = 0; i < nodeSeq.length - 1; i += 1) {
        const from = nodeSeq[i];
        const to = nodeSeq[i + 1];
        const nodeA = graph.nodes.get(from);
        const nodeB = graph.nodes.get(to);
        if (!nodeA || !nodeB) {
          continue;
        }
        const dist = haversine(nodeA.lat, nodeA.lon, nodeB.lat, nodeB.lon);
        const timeS = Math.max(5.0, dist / speedMs);
        addEdge(graph, from, to, {
          mode: modeName,
          distance_m: dist,
          time_s: timeS,
          route: line.ref || '',
          cost: 0.0,
        });
      }
    });
  }

  addLineEdges(busLines, 8.0, 'bus');
  addLineEdges(railLines, 15.0, 'rail');

  return graph;
}

function parseMaxSpeedKmh(value, fallbackKmh) {
  if (!value) {
    return fallbackKmh;
  }
  const text = String(value).trim().toLowerCase();
  const cleanedText = text.replace(/[;,]/g, ' ');
  const parts = cleanedText.split(/\s+/).filter(Boolean);

  for (const part of parts) {
    const cleaned = part
      .split('')
      .filter((ch) => (ch >= '0' && ch <= '9') || ch === '.')
      .join('');
    if (!cleaned) {
      continue;
    }
    const speed = Number(cleaned);
    if (Number.isFinite(speed) && speed > 0) {
      return speed;
    }
  }
  return fallbackKmh;
}

function buildRoadGraphState(modal) {
  const roads = loadJson('rede_viaria.json');
  const graph = createGraphState('road', {
    modal,
    origin: ORIGIN,
    destination: DESTINATION,
  });

  const edgeByKey = new Map();
  const nodeIds = graph.nodeOrder;

  const modalDefaultKmh = modal === 'car' ? 30.0 : 36.0;
  const modalCapKmh = modal === 'car' ? 55.0 : 65.0;

  function addRoadNode(lat, lon) {
    const nodeId = `${Number(lat).toFixed(6)},${Number(lon).toFixed(6)}`;
    if (!graph.nodes.has(nodeId)) {
      const node = { id: nodeId, lat, lon };
      graph.nodes.set(nodeId, node);
      nodeIds.push(nodeId);
    }
    return nodeId;
  }

  function upsertEdge(from, to, attrs) {
    const key = `${from}|${to}`;
    const existing = edgeByKey.get(key);
    if (!existing || existing.time_s > attrs.time_s) {
      edgeByKey.set(key, {
        from,
        to,
        ...attrs,
      });
    }
  }

  roads.forEach((way) => {
    const geom = Array.isArray(way.geometria) ? way.geometria : [];
    if (geom.length < 2) {
      return;
    }

    const onewayText = String(way.mao_unica || '').toLowerCase();
    const isOneway = onewayText === 'yes' || onewayText === '1' || onewayText === 'true';

    const rawKmh = parseMaxSpeedKmh(way.velocidade_max || '', modalDefaultKmh);
    const speedKmh = Math.min(rawKmh, modalCapKmh);
    const speedMs = Math.max(1.0, speedKmh / 3.6);

    for (let i = 0; i < geom.length - 1; i += 1) {
      const a = geom[i];
      const b = geom[i + 1];
      const aLat = a.lat;
      const aLon = a.lon;
      const bLat = b.lat;
      const bLon = b.lon;

      if (aLat === undefined || aLon === undefined || bLat === undefined || bLon === undefined) {
        continue;
      }

      const aNode = addRoadNode(aLat, aLon);
      const bNode = addRoadNode(bLat, bLon);

      const dist = haversine(aLat, aLon, bLat, bLon);
      const timeS = dist / speedMs;

      const edgeAttrs = {
        mode: modal,
        distance_m: dist,
        time_s: timeS,
        road_type: way.tipo_via || '',
        road_name: way.nome || '',
      };

      upsertEdge(aNode, bNode, edgeAttrs);
      if (!isOneway) {
        upsertEdge(bNode, aNode, edgeAttrs);
      }
    }
  });

  graph.edges = [];
  graph.nextEdgeId = 1;
  edgeByKey.forEach((edge) => {
    graph.edges.push({ id: graph.nextEdgeId++, ...edge });
  });

  return graph;
}

function getTransportGraph(options = {}) {
  const walkThresholdM = options.walkThresholdM || DEFAULT_WALK_THRESHOLD_M;
  const shouldRebuild =
    options.rebuild ||
    !cache.transport ||
    cache.transport.meta.walkThresholdM !== walkThresholdM;

  if (shouldRebuild) {
    cache.transport = buildTransportGraphState({ walkThresholdM });
  }
  return cache.transport;
}

function getRoadGraph(modal, rebuild) {
  if (modal !== 'car' && modal !== 'moto') {
    throw createError(400, 'modal must be car or moto');
  }
  if (!cache.road[modal] || rebuild) {
    cache.road[modal] = buildRoadGraphState(modal);
  }
  return cache.road[modal];
}

function getTransportGraphJson(options = {}) {
  const graph = getTransportGraph(options);
  return graphToJson(graph);
}

function getRoadGraphJson(options = {}) {
  const modal = options.modal || 'car';
  const graph = getRoadGraph(modal, options.rebuild);
  return graphToJson(graph);
}

function cloneGraphState(graph) {
  return {
    type: graph.type,
    nodes: new Map(graph.nodes),
    nodeOrder: [...graph.nodeOrder],
    edges: graph.edges.map((edge) => ({ ...edge })),
    nextEdgeId: graph.nextEdgeId,
    meta: { ...graph.meta },
  };
}

function addAccessNode(graph, id, location) {
  if (graph.nodes.has(id)) {
    return;
  }
  graph.nodes.set(id, {
    id,
    lat: location.lat,
    lon: location.lon,
    name: location.name || '',
    type: 'access',
  });
  graph.nodeOrder.push(id);
}

function addAccessEdges(graph, accessId, radiusM) {
  const accessNode = graph.nodes.get(accessId);
  if (!accessNode) {
    return;
  }

  graph.nodes.forEach((node, nodeId) => {
    if (nodeId === accessId) {
      return;
    }
    const dist = haversine(accessNode.lat, accessNode.lon, node.lat, node.lon);
    if (dist > radiusM) {
      return;
    }

    const timeS = dist / 1.4;
    addEdge(graph, accessId, nodeId, {
      mode: 'walk',
      distance_m: dist,
      time_s: timeS,
      cost: 0.0,
    });
    addEdge(graph, nodeId, accessId, {
      mode: 'walk',
      distance_m: dist,
      time_s: timeS,
      cost: 0.0,
    });
  });
}

function getModalSpeedMs(modal) {
  const defaultKmh = modal === 'moto' ? 36.0 : 30.0;
  return Math.max(1.0, defaultKmh / 3.6);
}

function addRoadAccessEdges(graph, accessId, radiusM, modal) {
  const accessNode = graph.nodes.get(accessId);
  if (!accessNode) {
    return;
  }

  const candidates = [];
  graph.nodes.forEach((node, nodeId) => {
    if (nodeId === accessId) {
      return;
    }
    const dist = haversine(accessNode.lat, accessNode.lon, node.lat, node.lon);
    candidates.push({ id: nodeId, dist });
  });

  candidates.sort((a, b) => a.dist - b.dist);
  const withinRadius = candidates.filter((candidate) => candidate.dist <= radiusM);
  const selected = withinRadius.length > 0 ? withinRadius : candidates;
  const topCandidates = selected.slice(0, 5);
  const speedMs = getModalSpeedMs(modal);

  topCandidates.forEach((candidate) => {
    const timeS = candidate.dist / speedMs;
    addEdge(graph, accessId, candidate.id, {
      mode: modal,
      distance_m: candidate.dist,
      time_s: timeS,
      cost: 0.0,
    });
    addEdge(graph, candidate.id, accessId, {
      mode: modal,
      distance_m: candidate.dist,
      time_s: timeS,
      cost: 0.0,
    });
  });
}

class MinHeap {
  constructor() {
    this.items = [];
  }

  push(entry) {
    this.items.push(entry);
    this.bubbleUp(this.items.length - 1);
  }

  pop() {
    if (this.items.length === 0) {
      return null;
    }
    const top = this.items[0];
    const last = this.items.pop();
    if (this.items.length > 0 && last) {
      this.items[0] = last;
      this.bubbleDown(0);
    }
    return top;
  }

  bubbleUp(index) {
    let idx = index;
    while (idx > 0) {
      const parent = Math.floor((idx - 1) / 2);
      if (this.items[parent].dist <= this.items[idx].dist) {
        break;
      }
      [this.items[parent], this.items[idx]] = [this.items[idx], this.items[parent]];
      idx = parent;
    }
  }

  bubbleDown(index) {
    let idx = index;
    const length = this.items.length;
    while (true) {
      const left = idx * 2 + 1;
      const right = idx * 2 + 2;
      let smallest = idx;

      if (left < length && this.items[left].dist < this.items[smallest].dist) {
        smallest = left;
      }
      if (right < length && this.items[right].dist < this.items[smallest].dist) {
        smallest = right;
      }
      if (smallest === idx) {
        break;
      }
      [this.items[idx], this.items[smallest]] = [this.items[smallest], this.items[idx]];
      idx = smallest;
    }
  }

  isEmpty() {
    return this.items.length === 0;
  }
}

function computeShortestPath(graph, startId, endId) {
  const adjacency = new Map();
  graph.edges.forEach((edge) => {
    if (!adjacency.has(edge.from)) {
      adjacency.set(edge.from, []);
    }
    adjacency.get(edge.from).push(edge);
  });

  const distances = new Map();
  const previous = new Map();
  const heap = new MinHeap();

  distances.set(startId, 0);
  heap.push({ id: startId, dist: 0 });

  while (!heap.isEmpty()) {
    const current = heap.pop();
    if (!current) {
      break;
    }

    const knownDist = distances.get(current.id);
    if (knownDist === undefined || current.dist !== knownDist) {
      continue;
    }

    if (current.id === endId) {
      break;
    }

    const edges = adjacency.get(current.id) || [];
    edges.forEach((edge) => {
      const nextDist = current.dist + edge.time_s;
      const prevDist = distances.get(edge.to);
      if (prevDist === undefined || nextDist < prevDist) {
        distances.set(edge.to, nextDist);
        previous.set(edge.to, edge);
        heap.push({ id: edge.to, dist: nextDist });
      }
    });
  }

  if (!distances.has(endId)) {
    return null;
  }

  const pathEdges = [];
  let cursor = endId;
  while (cursor !== startId) {
    const edge = previous.get(cursor);
    if (!edge) {
      break;
    }
    pathEdges.push(edge);
    cursor = edge.from;
  }

  if (cursor !== startId) {
    return null;
  }

  return pathEdges.reverse();
}

function getTransportProfile(mode) {
  if (mode === 'walk') {
    return 'walking';
  }
  return 'driving';
}

async function getTransportRouteJson(options = {}) {
  const walkThresholdM = options.walkThresholdM || DEFAULT_WALK_THRESHOLD_M;
  const baseGraph = getTransportGraph(options);
  const graph = cloneGraphState(baseGraph);
  const accessRadiusM = Math.max(walkThresholdM, 600);

  const originId = 'origin:cinema-sao-luiz';
  const destinationId = 'destination:faculdade-nova-roma';

  addAccessNode(graph, originId, ORIGIN);
  addAccessNode(graph, destinationId, DESTINATION);

  addAccessEdges(graph, originId, accessRadiusM);
  addAccessEdges(graph, destinationId, accessRadiusM);

  const pathEdges = computeShortestPath(graph, originId, destinationId);
  if (!pathEdges) {
    throw createError(404, 'No route found between origin and destination');
  }

  const nodesById = graph.nodes;
  const edges = [];
  const totals = { distance_m: 0, time_s: 0 };

  for (const edge of pathEdges) {
    const fromNode = nodesById.get(edge.from);
    const toNode = nodesById.get(edge.to);
    let geometry = null;

    if (fromNode && toNode) {
      const profile = getTransportProfile(edge.mode);
      try {
        const osrm = await osrmService.getRouteGeojson(
          [fromNode.lon, fromNode.lat],
          [toNode.lon, toNode.lat],
          profile
        );
        geometry = osrm.geometry;
      } catch (err) {
        console.warn('OSRM transport edge failed:', err && err.message ? err.message : err);
      }
    }

    edges.push({
      id: edge.id,
      from: edge.from,
      to: edge.to,
      mode: edge.mode,
      distance_m: edge.distance_m,
      time_s: edge.time_s,
      cost: edge.cost || 0.0,
      route: edge.route || '',
      from_coord: fromNode ? { lat: fromNode.lat, lon: fromNode.lon } : null,
      to_coord: toNode ? { lat: toNode.lat, lon: toNode.lon } : null,
      geometry,
    });

    totals.distance_m += edge.distance_m || 0;
    totals.time_s += edge.time_s || 0;
  }

  return {
    type: 'transport-route',
    meta: {
      origin: ORIGIN,
      destination: DESTINATION,
      walkThresholdM,
      builtAt: new Date().toISOString(),
    },
    summary: {
      edgeCount: edges.length,
      total_distance_m: totals.distance_m,
      total_time_s: totals.time_s,
    },
    edges,
  };
}

async function getRoadRouteJson(options = {}) {
  const modal = options.modal || 'car';
  if (modal !== 'car' && modal !== 'moto') {
    throw createError(400, 'modal must be car or moto');
  }

  const baseGraph = getRoadGraph(modal, options.rebuild);
  const graph = cloneGraphState(baseGraph);

  const originId = 'origin:cinema-sao-luiz';
  const destinationId = 'destination:faculdade-nova-roma';
  const accessRadiusM = 1000;

  addAccessNode(graph, originId, ORIGIN);
  addAccessNode(graph, destinationId, DESTINATION);

  addRoadAccessEdges(graph, originId, accessRadiusM, modal);
  addRoadAccessEdges(graph, destinationId, accessRadiusM, modal);

  const pathEdges = computeShortestPath(graph, originId, destinationId);
  if (!pathEdges) {
    throw createError(404, 'No route found between origin and destination');
  }

  const nodesById = graph.nodes;
  const edges = pathEdges.map((edge) => {
    const fromNode = nodesById.get(edge.from);
    const toNode = nodesById.get(edge.to);
    return {
      id: edge.id,
      from: edge.from,
      to: edge.to,
      mode: edge.mode,
      distance_m: edge.distance_m,
      time_s: edge.time_s,
      cost: edge.cost || 0.0,
      route: edge.route || '',
      road_type: edge.road_type || '',
      road_name: edge.road_name || '',
      from_coord: fromNode ? { lat: fromNode.lat, lon: fromNode.lon } : null,
      to_coord: toNode ? { lat: toNode.lat, lon: toNode.lon } : null,
    };
  });

  const totals = edges.reduce(
    (acc, edge) => {
      acc.distance_m += edge.distance_m || 0;
      acc.time_s += edge.time_s || 0;
      return acc;
    },
    { distance_m: 0, time_s: 0 }
  );

  let geometry = null;
  try {
    const osrm = await osrmService.getRouteGeojson(
      [ORIGIN.lon, ORIGIN.lat],
      [DESTINATION.lon, DESTINATION.lat],
      'driving'
    );
    geometry = osrm.geometry;
  } catch (err) {
    console.warn('OSRM road route failed:', err && err.message ? err.message : err);
  }

  return {
    type: 'road-route',
    meta: {
      origin: ORIGIN,
      destination: DESTINATION,
      modal,
      builtAt: new Date().toISOString(),
    },
    summary: {
      edgeCount: edges.length,
      total_distance_m: totals.distance_m,
      total_time_s: totals.time_s,
    },
    geometry,
    edges,
  };
}

function addTransportNode(payload) {
  const graph = getTransportGraph();
  if (graph.nodes.has(payload.id)) {
    throw createError(409, `Node already exists: ${payload.id}`);
  }

  const node = {
    id: payload.id,
    lat: payload.lat,
    lon: payload.lon,
    name: payload.name || '',
    type: payload.type || 'custom',
  };

  graph.nodes.set(node.id, node);
  graph.nodeOrder.push(node.id);
  return node;
}

function addTransportEdge(payload) {
  const graph = getTransportGraph();
  if (!graph.nodes.has(payload.from)) {
    throw createError(404, `from node not found: ${payload.from}`);
  }
  if (!graph.nodes.has(payload.to)) {
    throw createError(404, `to node not found: ${payload.to}`);
  }

  return addEdge(graph, payload.from, payload.to, {
    mode: payload.mode,
    distance_m: payload.distance_m,
    time_s: payload.time_s,
    cost: payload.cost,
    route: payload.route || '',
  });
}

function countBusBoardingsFromEdges(edges) {
  if (!Array.isArray(edges) || edges.length === 0) return 0;
  let boardings = 0;
  let prevMode = null;
  let prevRoute = null;
  for (const e of edges) {
    const mode = e.mode || (e.mode === undefined && e.route ? 'bus' : null);
    const route = e.route || '';
    if (mode === 'bus') {
      if (prevMode !== 'bus' || prevRoute !== route) {
        boardings += 1;
      }
      prevMode = 'bus';
      prevRoute = route;
    } else {
      prevMode = mode;
      prevRoute = null;
    }
  }
  return boardings;
}

async function getCostsComparison(options = {}) {
  const rebuild = options.rebuild || false;
  const walkThresholdM = options.walkThresholdM || DEFAULT_WALK_THRESHOLD_M;

  // Road routes for car and moto
  const carRoute = await getRoadRouteJson({ modal: 'car', rebuild });
  const motoRoute = await getRoadRouteJson({ modal: 'moto', rebuild });

  // Transport route (for bus + walk)
  const transportRoute = await getTransportRouteJson({ walkThresholdM, rebuild });

  const carDistanceKm = (carRoute.summary.total_distance_m || 0) / 1000.0;
  const motoDistanceKm = (motoRoute.summary.total_distance_m || 0) / 1000.0;
  const transportDistanceKm = (transportRoute.summary.total_distance_m || 0) / 1000.0;

  const carCostPerKm = GAS_PRICE / CAR_CONSUMPTION_KM_PER_L;
  const motoCostPerKm = GAS_PRICE / MOTO_CONSUMPTION_KM_PER_L;

  const carTotalCost = carCostPerKm * carDistanceKm;
  const motoTotalCost = motoCostPerKm * motoDistanceKm;

  const busEdges = transportRoute.edges || [];
  const busBoardings = countBusBoardingsFromEdges(busEdges);
  const busTotalCost = BUS_FARE * (busBoardings || 1);

  return {
    meta: {
      origin: carRoute.meta.origin,
      destination: carRoute.meta.destination,
      computedAt: new Date().toISOString(),
    },
    car: {
      distance_km: Number(carDistanceKm.toFixed(3)),
      cost_per_km: Number(carCostPerKm.toFixed(4)),
      total_cost: Number(carTotalCost.toFixed(2)),
      breakdown: `R$${GAS_PRICE} / ${CAR_CONSUMPTION_KM_PER_L} km/l = R$${carCostPerKm.toFixed(4)} per km; ${carDistanceKm.toFixed(3)} km * R$${carCostPerKm.toFixed(4)} = R$${carTotalCost.toFixed(2)}`,
    },
    moto: {
      distance_km: Number(motoDistanceKm.toFixed(3)),
      cost_per_km: Number(motoCostPerKm.toFixed(4)),
      total_cost: Number(motoTotalCost.toFixed(2)),
      breakdown: `R$${GAS_PRICE} / ${MOTO_CONSUMPTION_KM_PER_L} km/l = R$${motoCostPerKm.toFixed(4)} per km; ${motoDistanceKm.toFixed(3)} km * R$${motoCostPerKm.toFixed(4)} = R$${motoTotalCost.toFixed(2)}`,
    },
    bus: {
      distance_km: Number(transportDistanceKm.toFixed(3)),
      boardings: busBoardings,
      fare_per_boarding: Number(BUS_FARE.toFixed(2)),
      total_cost: Number(busTotalCost.toFixed(2)),
      breakdown: `Boardings: ${busBoardings}; ${busBoardings} * R$${BUS_FARE.toFixed(2)} = R$${busTotalCost.toFixed(2)}`,
    },
    recommendation: (() => {
      const items = [
        { modal: 'car', cost: carTotalCost },
        { modal: 'moto', cost: motoTotalCost },
        { modal: 'bus', cost: busTotalCost },
      ];
      items.sort((a, b) => a.cost - b.cost);
      return items[0];
    })(),
  };
}

module.exports = {
  getTransportGraphJson,
  getTransportRouteJson,
  getRoadGraphJson,
  getRoadRouteJson,
  addTransportNode,
  addTransportEdge,
  // exported for advanced usages
  _getTransportGraphState: getTransportGraph,
  getCostsComparison,
};
