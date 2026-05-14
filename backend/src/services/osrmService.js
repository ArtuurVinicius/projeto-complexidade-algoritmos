const fetch = global.fetch || require('node-fetch');

const OSRM_URL_BASE = process.env.OSRM_URL || 'https://router.project-osrm.org/route/v1';

// Simple in-memory cache: key -> geojson
const cache = new Map();

function coordKey(a, b, profile) {
  return `${profile}:${a[0]},${a[1]}|${b[0]},${b[1]}`;
}

async function getRouteGeojson(aLonLat, bLonLat, profile = 'driving') {
  const key = coordKey(aLonLat, bLonLat, profile);
  if (cache.has(key)) return cache.get(key);

  // OSRM expects lon,lat
  const coords = `${aLonLat[0]},${aLonLat[1]};${bLonLat[0]},${bLonLat[1]}`;
  const url = `${OSRM_URL_BASE}/${profile}/${coords}?overview=full&geometries=geojson`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`OSRM request failed: ${res.status} ${res.statusText}`);
  }
  const data = await res.json();
  if (!data.routes || data.routes.length === 0) {
    throw new Error('OSRM returned no route');
  }
  const route = data.routes[0];
  const out = {
    distance: route.distance,
    duration: route.duration,
    geometry: route.geometry, // geojson LineString
  };
  cache.set(key, out);
  return out;
}

module.exports = { getRouteGeojson };
