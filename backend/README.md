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

### OSRM Integration
The backend can query an OSRM server to return route geometries between graph nodes. By default it uses the public OSRM endpoint `https://router.project-osrm.org` but you can set a different base with the environment variable `OSRM_URL` (e.g. `http://localhost:5000/route/v1`).

- GET /api/graph/route?from=<nodeId>&to=<nodeId>&profile=driving
  - Returns OSRM route (distance, duration and GeoJSON LineString) between two transport graph nodes.
- GET /api/graph/transport/edges-geo?limit=100&profile=driving
  - Returns geometries for the first `limit` transport edges. Useful for drawing edges directly on a frontend map.

Response format for `edges-geo`:
```
{ "status": "ok", "data": [ { "edge": { ... }, "geometry": { distance, duration, geometry: { type: 'LineString', coordinates: [...] } } }, ... ] }
```

Frontend example (Leaflet) to draw edge geometries:
```javascript
fetch('/api/graph/transport/edges-geo?limit=200')
  .then(r => r.json())
  .then(json => {
    if (json.status !== 'ok') throw new Error('API error');
    json.data.forEach(item => {
      if (item.geometry && item.geometry.geometry) {
        const coords = item.geometry.geometry.coordinates.map(c => [c[1], c[0]]); // [lat,lon]
        L.polyline(coords, { color: 'blue', weight: 2 }).addTo(map);
      }
    });
  });
```

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
