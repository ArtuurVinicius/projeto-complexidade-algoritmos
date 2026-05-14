const express = require('express');

const {
  getTransportGraphJson,
  getRoadGraphJson,
  addTransportNode,
  addTransportEdge,
} = require('../services/graphService');
const {
  parseNumber,
  validateNodePayload,
  validateEdgePayload,
} = require('../utils/validation');

const router = express.Router();

/*
Endpoints:
- GET /api/graph/transport
- GET /api/graph/road?modal=car|moto
- POST /api/graph/transport/nodes
- POST /api/graph/transport/edges
*/
router.get('/transport', (req, res, next) => {
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
    const graph = getTransportGraphJson({ walkThresholdM, rebuild });

    res.json({ status: 'ok', data: graph });
  } catch (err) {
    next(err);
  }
});

router.get('/road', (req, res, next) => {
  try {
    const modal = req.query.modal ? String(req.query.modal).toLowerCase() : 'car';
    if (modal !== 'car' && modal !== 'moto') {
      return res.status(400).json({
        status: 'error',
        message: 'modal must be car or moto',
      });
    }

    const rebuild = String(req.query.rebuild || '').toLowerCase() === 'true';
    const graph = getRoadGraphJson({ modal, rebuild });

    res.json({ status: 'ok', data: graph });
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

module.exports = router;
