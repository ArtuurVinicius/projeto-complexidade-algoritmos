<template>
  <div id="map"></div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import L from 'leaflet'

import 'leaflet/dist/leaflet.css'

const props = defineProps({
  routes: {
    type: Object,
    default: () => ({})
  },
  routeErrors: {
    type: Object,
    default: () => ({})
  }
})

let map
let routeLayer

const routeColors = {
  transport: '#2e7d32',
  car: '#000080',
  moto: '#57A0D2'
}

const getRouteColor = (key) => routeColors[key] || '#455a64'

const resolveRouteColor = (key, routeData) => {
  if (routeData?.meta?.modal === 'car') {
    return routeColors.car
  }
  if (routeData?.meta?.modal === 'moto') {
    return routeColors.moto
  }
  if (routeData?.type === 'transport-route') {
    return routeColors.transport
  }
  return getRouteColor(key)
}

const clearRoute = () => {
  if (routeLayer) {
    routeLayer.clearLayers()
  }
}

const renderGeometry = (geometry, color, bounds) => {
  if (!geometry || geometry.type !== 'LineString' || !Array.isArray(geometry.coordinates)) {
    return false
  }

  const latLngs = geometry.coordinates
    .filter((coord) => Array.isArray(coord) && coord.length >= 2)
    .map((coord) => [coord[1], coord[0]])

  if (latLngs.length < 2) {
    return false
  }

  latLngs.forEach((point) => bounds.push(point))

  L.polyline(latLngs, {
    color,
    weight: 5,
    opacity: 0.9
  }).addTo(routeLayer)

  return true
}

const renderRoutes = (routes) => {
  if (!map || !routeLayer) {
    return
  }

  clearRoute()

  if (!routes || typeof routes !== 'object') {
    return
  }

  const bounds = []
  let metaOrigin = null
  let metaDestination = null

  const orderedKeys = ['transport', 'car', 'moto']

  orderedKeys.forEach((key) => {
    const routeData = routes[key]
    if (!routeData || !Array.isArray(routeData.edges)) {
      return
    }

    if (!metaOrigin && routeData.meta?.origin) {
      metaOrigin = routeData.meta.origin
    }
    if (!metaDestination && routeData.meta?.destination) {
      metaDestination = routeData.meta.destination
    }

    const color = resolveRouteColor(key, routeData)
    const usedGeometry = renderGeometry(routeData.geometry, color, bounds)
    if (usedGeometry) {
      return
    }
    routeData.edges.forEach((edge) => {
      const usedEdgeGeometry = renderGeometry(edge.geometry, color, bounds)
      if (usedEdgeGeometry) {
        return
      }
      if (!edge.from_coord || !edge.to_coord) {
        return
      }

      const fromLatLng = [edge.from_coord.lat, edge.from_coord.lon]
      const toLatLng = [edge.to_coord.lat, edge.to_coord.lon]
      bounds.push(fromLatLng, toLatLng)

      L.polyline([fromLatLng, toLatLng], {
        color,
        weight: 4,
        opacity: 0.85
      }).addTo(routeLayer)
    })
  })

  if (metaOrigin) {
    L.marker([metaOrigin.lat, metaOrigin.lon])
      .addTo(routeLayer)
      .bindPopup(metaOrigin.name || 'Origem')
  }

  if (metaDestination) {
    L.marker([metaDestination.lat, metaDestination.lon])
      .addTo(routeLayer)
      .bindPopup(metaDestination.name || 'Destino')
  }

  if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [20, 20] })
  }
}

onMounted(() => {

  // Coordenadas Recife
  map = L.map('map').setView([-8.0476, -34.8770], 13)

  // Tiles do OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)

  routeLayer = L.layerGroup().addTo(map)
  renderRoutes(props.routes)
})

watch(
  () => props.routes,
  (value) => {
    renderRoutes(value)
  },
  { deep: true }
)

watch(
  () => props.routeErrors,
  (value) => {
    if (value && typeof value === 'object') {
      Object.entries(value).forEach(([key, error]) => {
        if (error) {
          console.warn(`Route load error (${key}):`, error)
        }
      })
    }
  },
  { deep: true }
)
</script>

<style scoped>
#map {
  width: 100%;
  height: 100%;
}

.map-area {
  flex: 1;
}
</style>