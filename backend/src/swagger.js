const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const PORT = Number.isFinite(Number(process.env.PORT)) ? Number(process.env.PORT) : 3001;

const swaggerSpec = swaggerJsdoc({
  definition: {
    openapi: '3.0.3',
    info: {
      title: 'Graph API',
      version: '1.0.0',
      description: 'REST API that exposes graph builders from the algoritmos dataset.',
    },
    servers: [
      {
        url: `http://localhost:${PORT}`,
        description: 'Local server',
      },
    ],
    tags: [
      { name: 'Health' },
      { name: 'Graph' },
    ],
    paths: {
      '/api/health': {
        get: {
          tags: ['Health'],
          summary: 'Health check',
          responses: {
            200: {
              description: 'Service is healthy',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/HealthResponse' },
                },
              },
            },
          },
        },
      },
      '/api/graph/transport': {
        get: {
          tags: ['Graph'],
          summary: 'Get transport graph (multimodal)',
          parameters: [
            {
              name: 'walkThresholdM',
              in: 'query',
              description: 'Max walking distance between nodes in meters',
              required: false,
              schema: { type: 'number', minimum: 0, default: 200 },
            },
            {
              name: 'route',
              in: 'query',
              description: 'Return only the route between origin and destination',
              required: false,
              schema: { type: 'boolean', default: false },
            },
            {
              name: 'rebuild',
              in: 'query',
              description: 'Force rebuild of the cached graph',
              required: false,
              schema: { type: 'boolean', default: false },
            },
          ],
          responses: {
            200: {
              description: 'Transport graph',
              content: {
                'application/json': {
                  schema: {
                    oneOf: [
                      { $ref: '#/components/schemas/GraphResponse' },
                      { $ref: '#/components/schemas/TransportRouteResponse' },
                    ],
                  },
                },
              },
            },
            400: {
              description: 'Invalid query',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ErrorResponse' },
                },
              },
            },
            500: {
              description: 'Server error',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ErrorResponse' },
                },
              },
            },
          },
        },
      },
      '/api/graph/road': {
        get: {
          tags: ['Graph'],
          summary: 'Get road graph (car or moto)',
          parameters: [
            {
              name: 'modal',
              in: 'query',
              description: 'Road modal',
              required: false,
              schema: { type: 'string', enum: ['car', 'moto'], default: 'car' },
            },
            {
              name: 'route',
              in: 'query',
              description: 'Return only the route between origin and destination',
              required: false,
              schema: { type: 'boolean', default: false },
            },
            {
              name: 'rebuild',
              in: 'query',
              description: 'Force rebuild of the cached graph',
              required: false,
              schema: { type: 'boolean', default: false },
            },
          ],
          responses: {
            200: {
              description: 'Road graph',
              content: {
                'application/json': {
                  schema: {
                    oneOf: [
                      { $ref: '#/components/schemas/GraphResponse' },
                      { $ref: '#/components/schemas/RoadRouteResponse' },
                    ],
                  },
                },
              },
            },
            400: {
              description: 'Invalid query',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ErrorResponse' },
                },
              },
            },
            500: {
              description: 'Server error',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ErrorResponse' },
                },
              },
            },
          },
        },
      },
      '/api/graph/transport/nodes': {
        post: {
          tags: ['Graph'],
          summary: 'Create a transport node (in-memory)',
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/NodeCreateRequest' },
              },
            },
          },
          responses: {
            201: {
              description: 'Node created',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/NodeResponse' },
                },
              },
            },
            400: {
              description: 'Validation error',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ErrorResponse' },
                },
              },
            },
            409: {
              description: 'Node already exists',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ErrorResponse' },
                },
              },
            },
          },
        },
      },
      '/api/graph/transport/edges': {
        post: {
          tags: ['Graph'],
          summary: 'Create a transport edge (in-memory)',
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/EdgeCreateRequest' },
              },
            },
          },
          responses: {
            201: {
              description: 'Edge created',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/EdgeResponse' },
                },
              },
            },
            400: {
              description: 'Validation error',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ErrorResponse' },
                },
              },
            },
            404: {
              description: 'Node not found',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ErrorResponse' },
                },
              },
            },
          },
        },
      },
      '/api/graph/route': {
        get: {
          tags: ['Graph'],
          summary: 'Get OSRM route geometry between two node ids (transport graph)',
          parameters: [
            { name: 'from', in: 'query', required: true, schema: { type: 'string' } },
            { name: 'to', in: 'query', required: true, schema: { type: 'string' } },
            { name: 'profile', in: 'query', required: false, schema: { type: 'string', example: 'driving' } },
          ],
          responses: {
            200: { description: 'GeoJSON route', content: { 'application/json': { schema: { type: 'object' } } } },
            400: { description: 'Invalid query', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            404: { description: 'Node not found', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
          },
        },
      },
      '/api/graph/transport/edges-geo': {
        get: {
          tags: ['Graph'],
          summary: 'Get geometries for first N transport edges using OSRM',
          parameters: [
            { name: 'limit', in: 'query', required: false, schema: { type: 'integer', default: 100 } },
            { name: 'profile', in: 'query', required: false, schema: { type: 'string', example: 'driving' } },
          ],
          responses: {
            200: { description: 'List of edges with geometry', content: { 'application/json': { schema: { type: 'object' } } } },
          },
        },
      },
    },
    components: {
      schemas: {
        HealthResponse: {
          type: 'object',
          properties: {
            status: { type: 'string', example: 'ok' },
          },
          required: ['status'],
        },
        GraphResponse: {
          type: 'object',
          properties: {
            status: { type: 'string', example: 'ok' },
            data: { $ref: '#/components/schemas/Graph' },
          },
          required: ['status', 'data'],
        },
        TransportRouteResponse: {
          type: 'object',
          properties: {
            status: { type: 'string', example: 'ok' },
            data: { $ref: '#/components/schemas/TransportRoute' },
          },
          required: ['status', 'data'],
        },
        RoadRouteResponse: {
          type: 'object',
          properties: {
            status: { type: 'string', example: 'ok' },
            data: { $ref: '#/components/schemas/RoadRoute' },
          },
          required: ['status', 'data'],
        },
        NodeResponse: {
          type: 'object',
          properties: {
            status: { type: 'string', example: 'ok' },
            data: { $ref: '#/components/schemas/GraphNode' },
          },
          required: ['status', 'data'],
        },
        EdgeResponse: {
          type: 'object',
          properties: {
            status: { type: 'string', example: 'ok' },
            data: { $ref: '#/components/schemas/GraphEdge' },
          },
          required: ['status', 'data'],
        },
        ErrorResponse: {
          type: 'object',
          properties: {
            status: { type: 'string', example: 'error' },
            message: { type: 'string' },
            details: {
              type: 'array',
              items: { type: 'string' },
              nullable: true,
            },
          },
          required: ['status', 'message'],
        },
        Graph: {
          type: 'object',
          properties: {
            type: { type: 'string', example: 'transport' },
            meta: { $ref: '#/components/schemas/GraphMeta' },
            nodes: {
              type: 'array',
              items: { $ref: '#/components/schemas/GraphNode' },
            },
            edges: {
              type: 'array',
              items: { $ref: '#/components/schemas/GraphEdge' },
            },
          },
          required: ['type', 'meta', 'nodes', 'edges'],
        },
        GraphMeta: {
          type: 'object',
          properties: {
            builtAt: { type: 'string', format: 'date-time' },
            walkThresholdM: { type: 'number' },
            modal: { type: 'string' },
            origin: { $ref: '#/components/schemas/Location' },
            destination: { $ref: '#/components/schemas/Location' },
            nodeCount: { type: 'integer' },
            edgeCount: { type: 'integer' },
          },
        },
        Location: {
          type: 'object',
          properties: {
            lat: { type: 'number' },
            lon: { type: 'number' },
            name: { type: 'string' },
          },
        },
        GraphNode: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            lat: { type: 'number' },
            lon: { type: 'number' },
            name: { type: 'string' },
            type: { type: 'string' },
          },
          required: ['id', 'lat', 'lon'],
        },
        GraphEdge: {
          type: 'object',
          properties: {
            id: { type: 'integer' },
            from: { type: 'string' },
            to: { type: 'string' },
            mode: { type: 'string' },
            distance_m: { type: 'number' },
            time_s: { type: 'number' },
            cost: { type: 'number' },
            route: { type: 'string' },
            road_type: { type: 'string' },
            road_name: { type: 'string' },
          },
          required: ['id', 'from', 'to', 'mode', 'distance_m', 'time_s'],
        },
        TransportRoute: {
          type: 'object',
          properties: {
            type: { type: 'string', example: 'transport-route' },
            meta: {
              type: 'object',
              properties: {
                origin: { $ref: '#/components/schemas/Location' },
                destination: { $ref: '#/components/schemas/Location' },
                walkThresholdM: { type: 'number' },
                builtAt: { type: 'string', format: 'date-time' },
              },
            },
            summary: {
              type: 'object',
              properties: {
                edgeCount: { type: 'integer' },
                total_distance_m: { type: 'number' },
                total_time_s: { type: 'number' },
              },
            },
            edges: {
              type: 'array',
              items: { $ref: '#/components/schemas/TransportRouteEdge' },
            },
          },
          required: ['type', 'meta', 'summary', 'edges'],
        },
        RoadRoute: {
          type: 'object',
          properties: {
            type: { type: 'string', example: 'road-route' },
            meta: {
              type: 'object',
              properties: {
                origin: { $ref: '#/components/schemas/Location' },
                destination: { $ref: '#/components/schemas/Location' },
                modal: { type: 'string', enum: ['car', 'moto'] },
                builtAt: { type: 'string', format: 'date-time' },
              },
            },
            summary: {
              type: 'object',
              properties: {
                edgeCount: { type: 'integer' },
                total_distance_m: { type: 'number' },
                total_time_s: { type: 'number' },
              },
            },
            geometry: {
              type: 'object',
              nullable: true,
              properties: {
                type: { type: 'string', example: 'LineString' },
                coordinates: {
                  type: 'array',
                  items: {
                    type: 'array',
                    items: { type: 'number' },
                    minItems: 2,
                    maxItems: 2,
                  },
                },
              },
            },
            edges: {
              type: 'array',
              items: { $ref: '#/components/schemas/RoadRouteEdge' },
            },
          },
          required: ['type', 'meta', 'summary', 'edges'],
        },
        TransportRouteEdge: {
          type: 'object',
          properties: {
            id: { type: 'integer' },
            from: { type: 'string' },
            to: { type: 'string' },
            mode: { type: 'string' },
            distance_m: { type: 'number' },
            time_s: { type: 'number' },
            cost: { type: 'number' },
            route: { type: 'string' },
            from_coord: { $ref: '#/components/schemas/Location' },
            to_coord: { $ref: '#/components/schemas/Location' },
            geometry: {
              type: 'object',
              nullable: true,
              properties: {
                type: { type: 'string', example: 'LineString' },
                coordinates: {
                  type: 'array',
                  items: {
                    type: 'array',
                    items: { type: 'number' },
                    minItems: 2,
                    maxItems: 2,
                  },
                },
              },
            },
          },
          required: ['id', 'from', 'to', 'mode', 'distance_m', 'time_s'],
        },
        RoadRouteEdge: {
          type: 'object',
          properties: {
            id: { type: 'integer' },
            from: { type: 'string' },
            to: { type: 'string' },
            mode: { type: 'string' },
            distance_m: { type: 'number' },
            time_s: { type: 'number' },
            cost: { type: 'number' },
            route: { type: 'string' },
            road_type: { type: 'string' },
            road_name: { type: 'string' },
            from_coord: { $ref: '#/components/schemas/Location' },
            to_coord: { $ref: '#/components/schemas/Location' },
          },
          required: ['id', 'from', 'to', 'mode', 'distance_m', 'time_s'],
        },
        NodeCreateRequest: {
          type: 'object',
          properties: {
            id: { type: 'string', example: 'custom:node-1' },
            lat: { type: 'number', example: -8.1 },
            lon: { type: 'number', example: -34.9 },
            name: { type: 'string', example: 'Custom stop' },
            type: { type: 'string', example: 'custom' },
          },
          required: ['id', 'lat', 'lon'],
        },
        EdgeCreateRequest: {
          type: 'object',
          properties: {
            from: { type: 'string', example: 'custom:node-1' },
            to: { type: 'string', example: 'bus:123' },
            mode: { type: 'string', example: 'walk' },
            distance_m: { type: 'number', example: 120.5 },
            time_s: { type: 'number', example: 86.0 },
            cost: { type: 'number', example: 0.0 },
            route: { type: 'string', example: '' },
          },
          required: ['from', 'to', 'mode', 'distance_m', 'time_s'],
        },
      },
    },
  },
  apis: [],
});

module.exports = {
  swaggerUi,
  swaggerSpec,
};
