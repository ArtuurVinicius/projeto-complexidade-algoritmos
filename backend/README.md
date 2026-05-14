# Graph API (Node.js)

REST API that exposes the same graph-building logic from the `algoritmos` folder.

## Requirements
- Node.js 18+

## Setup
- npm install
- npm start

Default port: 3001 (set `PORT` to change).

Swagger UI: http://localhost:3001/api/docs

## Data source
The API reads JSON files from `algoritmos/dados_coletados`. You can override the path with `ALGORITMOS_DIR`.

## Endpoints
- GET /api/health
- GET /api/graph/transport
  - Query: walkThresholdM (number), rebuild=true|false
- GET /api/graph/road?modal=car|moto
  - Query: rebuild=true|false
- POST /api/graph/transport/nodes
- POST /api/graph/transport/edges

### Payloads
POST /api/graph/transport/nodes
```
{
  "id": "custom:node-1",
  "lat": -8.10,
  "lon": -34.90,
  "name": "Custom stop",
  "type": "custom"
}
```

POST /api/graph/transport/edges
```
{
  "from": "custom:node-1",
  "to": "bus:123",
  "mode": "walk",
  "distance_m": 120.5,
  "time_s": 86.0,
  "cost": 0.0,
  "route": ""
}
```

Notes:
- POST endpoints update the in-memory graph only.
