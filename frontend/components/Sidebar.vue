<template>
  <div class="sidebar">
    <div class="location-info">
      <div class="route-header">
        <div class="route-item">
          <span class="route-label">Origem</span>
          <p class="route-name">{{ origin || 'Cinema São Luis' }}</p>
        </div>
        <div class="route-divider"></div>
        <div class="route-item">
          <span class="route-label">Destino</span>
          <p class="route-name">{{ destination || 'Faculdade Nova Roma' }}</p>
        </div>
      </div>
    </div>

    <div class="routes-summary" v-if="availableRoutes.length > 0">
      <h3 class="routes-title">Rotas Disponíveis</h3>
      <div class="route-card" v-for="route in availableRoutes" :key="route.key">
        <div class="route-card-header">
          <div class="route-vehicle">
            <span class="vehicle-name">{{ getRouteName(route.key) }}</span>
          </div>
          <div class="route-time" :style="{ color: getRouteColor(route.key) }">
            {{ formatTime(route.data.summary?.total_time_s) }}
          </div>
        </div>
        <div class="route-card-details">
          <div class="detail-item">
            <span class="detail-label">Distância:</span>
            <span class="detail-value">{{ formatDistance(route.data.summary?.total_distance_m) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  origin: String,
  destination: String,
  routes: {
    type: Object,
    default: () => ({})
  }
})

const routeColors = {
  transport: '#2e7d32',
  car: '#000080',
  moto: '#57A0D2'
}

const availableRoutes = computed(() => {
  return Object.entries(props.routes)
    .filter(([key, data]) => data && data.summary)
    .map(([key, data]) => ({
      key,
      data
    }))
    .sort((a, b) => (a.data.summary?.total_time_s || 0) - (b.data.summary?.total_time_s || 0))
})

const getRouteName = (key) => {
  const names = {
    'transport': 'Transporte Público',
    'car': 'Carro',
    'moto': 'Moto'
  }
  return names[key] || key
}

const getRouteColor = (key) => {
  return routeColors[key] || '#455a64'
}

const formatTime = (seconds) => {
  if (!seconds || seconds < 0) return '0 min'
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) {
    return `${minutes} min`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins}m`
}

const formatDistance = (meters) => {
  if (!meters || meters < 0) return '0 km'
  if (meters < 1000) {
    return `${Math.round(meters)} m`
  }
  const km = (meters / 1000).toFixed(2)
  return `${km} km`
}
</script>

<style scoped>
.sidebar {
  width: 400px;
  background-color: white;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.location-info {
  padding: 20px;
}

.route-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e8e8e8;
}

.route-item {
  margin-bottom: 12px;
}

.route-item:last-child {
  margin-bottom: 0;
}

.route-label {
  font-size: 12px;
  font-weight: 600;
  color: #5f6368;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.route-name {
  font-size: 18px;
  font-weight: 500;
  color: #202124;
  margin: 4px 0 0 0;
}

.route-divider {
  height: 2px;
  background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
  margin: 12px 0;
}

.routes-summary {
  padding: 16px 20px;
  border-top: 1px solid #e8e8e8;
  flex: 1;
  overflow-y: auto;
}

.routes-title {
  font-size: 14px;
  font-weight: 600;
  color: #202124;
  margin: 0 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.route-card {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.route-card:hover {
  background-color: #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.route-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.route-vehicle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.vehicle-name {
  font-size: 14px;
  color: #202124;
}

.route-time {
  font-size: 16px;
  font-weight: 700;
}

.route-card-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.detail-label {
  color: #5f6368;
  font-weight: 500;
}

.detail-value {
  color: #202124;
  font-weight: 600;
}

.address-details {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e8e8e8;
}

.address-details p {
  margin: 0;
  font-size: 14px;
  color: #5f6368;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e8e8e8;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #202124;
  transition: all 0.3s;
}

.action-btn:hover {
  background-color: #f8f9fa;
  border-color: #4285f4;
}

.action-btn .icon {
  font-size: 20px;
}

.menu-options {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background-color: white;
  border: none;
  cursor: pointer;
  text-align: left;
  font-size: 13px;
  color: #5f6368;
  transition: background-color 0.3s;
}

.menu-item:hover {
  background-color: #f8f9fa;
}

.menu-item span:first-child {
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid #e8e8e8;
  text-align: center;
  font-size: 12px;
  color: #70757a;
}
</style>
