const fs = require('fs');
const path = require('path');

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

module.exports = {
  getTransportGraphJson,
  getRoadGraphJson,
  addTransportNode,
  addTransportEdge,
};
