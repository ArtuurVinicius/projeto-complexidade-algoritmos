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
    <div class="routes-summary" v-if="costs">
      <h3 class="routes-title">Comparação de Custos</h3>
      <div class="route-card">
        <div class="route-card-details">
          <div class="detail-item">
            <span class="detail-label">Carro - Distância:</span>
            <span class="detail-value">{{ costs?.car?.distance_km }} km</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Carro - Custo por km:</span>
            <span class="detail-value">{{ formatCurrency(costs?.car?.cost_per_km) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Carro - Custo total:</span>
            <span class="detail-value">{{ formatCurrency(costs?.car?.total_cost) }}</span>
          </div>

          <div class="detail-item">
            <span class="detail-label">Moto - Distância:</span>
            <span class="detail-value">{{ costs?.moto?.distance_km }} km</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Moto - Custo por km:</span>
            <span class="detail-value">{{ formatCurrency(costs?.moto?.cost_per_km) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Moto - Custo total:</span>
            <span class="detail-value">{{ formatCurrency(costs?.moto?.total_cost) }}</span>
          </div>

          <div class="detail-item">
            <span class="detail-label">Ônibus - Distância:</span>
            <span class="detail-value">{{ costs?.bus?.distance_km }} km</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Ônibus - Embarques:</span>
            <span class="detail-value">{{ costs?.bus?.boardings }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Ônibus - Custo total:</span>
            <span class="detail-value">{{ formatCurrency(costs?.bus?.total_cost) }}</span>
          </div>

          <div class="detail-item" style="margin-top:8px;">
            <span class="detail-label">Recomendação:</span>
            <span class="detail-value">{{ costs?.recommendation?.modal }} ({{ formatCurrency(costs?.recommendation?.cost) }})</span>
          </div>
        </div>
      </div>
    </div>

    <div class="action-buttons">
      <button class="action-btn" @click="onCompareCosts">
        <div class="icon">🔍</div>
        <div>Comparar custos</div>
      </button>
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
  },
  costs: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['compare-costs'])

const costs = computed(() => props.costs)

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

const formatCurrency = (value) => {
  if (value === null || value === undefined) return 'R$0.00'
  return `R$${Number(value).toFixed(2)}`
}

const onCompareCosts = () => {
  emit('compare-costs')
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
  display: flex;
  justify-content: center;
  align-items: center;
  /* center this block vertically within the sidebar column */
  margin: auto;
  padding: 12px 0;
  width: 100%;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  width: 200px;
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
