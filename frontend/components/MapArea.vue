<template>
  <div id="map"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import L from 'leaflet'

import 'leaflet/dist/leaflet.css'

onMounted(() => {

  // Coordenadas Recife
  const map = L.map('map').setView([-8.0476, -34.8770], 13)

  // Tiles do OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)

  // Marcador exemplo
  L.marker([-8.0476, -34.8770])
    .addTo(map)
    .bindPopup('Recife')
    .openPopup()
})
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