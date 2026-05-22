const express = require('express');

const {
  getTransportGraphJson,
  getTransportRouteJson,
  getRoadGraphJson,
  getRoadRouteJson,
  addTransportNode,
  addTransportEdge,
  getCostsComparison,
} = require('../services/graphService');
const {
  parseNumber,
  validateNodePayload,
  validateEdgePayload,
} = require('../utils/validation');

const router = express.Router();

const osrmService = require('../services/osrmService');

/*
Endpoints:
- GET /api/graph/transport
- GET /api/graph/road?modal=car|moto
- POST /api/graph/transport/nodes
- POST /api/graph/transport/edges
*/
router.get('/transport', async (req, res, next) => {
  try {
    let walkThresholdM;
    if (req.query.walkThresholdM !== undefined) {
      const parsed = parseNumber(req.query.walkThresholdM);
      if (parsed === null || parsed < 0) {
        return res.status(400).json({
          status: 'error',
          message: 'walkThresholdM must be a non-negative number',
        });
      }
      walkThresholdM = parsed;
    }

    const rebuild = String(req.query.rebuild || '').toLowerCase() === 'true';
    const wantsRoute = String(req.query.route || '').toLowerCase() === 'true';
    const payload = wantsRoute
      ? await getTransportRouteJson({ walkThresholdM, rebuild })
      : getTransportGraphJson({ walkThresholdM, rebuild });

    res.json({ status: 'ok', data: payload });
  } catch (err) {
    next(err);
  }
});

router.get('/road', async (req, res, next) => {
  try {
    const modal = req.query.modal ? String(req.query.modal).toLowerCase() : 'car';
    if (modal !== 'car' && modal !== 'moto') {
      return res.status(400).json({
        status: 'error',
        message: 'modal must be car or moto',
      });
    }

    const rebuild = String(req.query.rebuild || '').toLowerCase() === 'true';
    const wantsRoute = String(req.query.route || '').toLowerCase() === 'true';
    const payload = wantsRoute
      ? await getRoadRouteJson({ modal, rebuild })
      : getRoadGraphJson({ modal, rebuild });

    res.json({ status: 'ok', data: payload });
  } catch (err) {
    next(err);
  }
});

// Get geometry between two existing nodes using OSRM
router.get('/route', async (req, res, next) => {
  try {
    const from = req.query.from;
    const to = req.query.to;
    const profile = req.query.profile ? String(req.query.profile) : 'driving';
    if (!from || !to) {
      return res.status(400).json({ status: 'error', message: 'from and to query parameters are required' });
    }

    // get graph nodes
    const graph = getTransportGraphJson();
    const nodes = graph.nodes.reduce((acc, n) => { acc[n.id] = n; return acc; }, {});
    const nFrom = nodes[from];
    const nTo = nodes[to];
    if (!nFrom) return res.status(404).json({ status: 'error', message: `from node not found: ${from}` });
    if (!nTo) return res.status(404).json({ status: 'error', message: `to node not found: ${to}` });

    const geom = await osrmService.getRouteGeojson([nFrom.lon, nFrom.lat], [nTo.lon, nTo.lat], profile);
    res.json({ status: 'ok', data: geom });
  } catch (err) {
    next(err);
  }
});

// Return geometries for first N transport edges (useful for frontend map overlay)
router.get('/transport/edges-geo', async (req, res, next) => {
  try {
    const limit = req.query.limit ? Number(req.query.limit) : 100;
    const profile = req.query.profile ? String(req.query.profile) : 'driving';
    const graph = getTransportGraphJson();
    const nodesMap = graph.nodes.reduce((acc, n) => { acc[n.id] = n; return acc; }, {});
    const edges = graph.edges.slice(0, limit);

    const results = [];
    for (const e of edges) {
      const a = nodesMap[e.from];
      const b = nodesMap[e.to];
      if (!a || !b) continue;
      try {
        const geom = await osrmService.getRouteGeojson([a.lon, a.lat], [b.lon, b.lat], profile);
        results.push({ edge: e, geometry: geom });
      } catch (err) {
        // skip failures but keep metadata
        results.push({ edge: e, error: String(err) });
      }
    }
    res.json({ status: 'ok', data: results });
  } catch (err) {
    next(err);
  }
});

router.post('/transport/nodes', (req, res, next) => {
  try {
    const validation = validateNodePayload(req.body);
    if (!validation.ok) {
      return res.status(400).json({
        status: 'error',
        message: 'Invalid node payload',
        details: validation.errors,
      });
    }

    const node = addTransportNode(validation.value);
    res.status(201).json({ status: 'ok', data: node });
  } catch (err) {
    next(err);
  }
});

router.post('/transport/edges', (req, res, next) => {
  try {
    const validation = validateEdgePayload(req.body);
    if (!validation.ok) {
      return res.status(400).json({
        status: 'error',
        message: 'Invalid edge payload',
        details: validation.errors,
      });
    }

    const edge = addTransportEdge(validation.value);
    res.status(201).json({ status: 'ok', data: edge });
  } catch (err) {
    next(err);
  }
});

// Compare costs for car, moto and bus for the origin-destination
router.get('/compare-costs', async (req, res, next) => {
  try {
    const rebuild = String(req.query.rebuild || '').toLowerCase() === 'true';
    let walkThresholdM;
    if (req.query.walkThresholdM !== undefined) {
      const parsed = parseNumber(req.query.walkThresholdM);
      if (parsed === null || parsed < 0) {
        return res.status(400).json({ status: 'error', message: 'walkThresholdM must be a non-negative number' });
      }
      walkThresholdM = parsed;
    }

    const result = await getCostsComparison({ rebuild, walkThresholdM });
    res.json({ status: 'ok', data: result });
  } catch (err) {
    next(err);
  }
});

module.exports = router;

