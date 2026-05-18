<template>
  <v-app>
    <div class="container">
      <search-bar @search="handleSearch" @filter-change="handleFilterChange" />
      <div class="main-content">
        <sidebar :origin="searchRoute.origin" :destination="searchRoute.destination" :routes="graphData" />
        <map-area :routes="graphData" :route-errors="graphErrors" :selected-route="selectedRoute" />
      </div>
    </div>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import SearchBar from './components/SearchBar.vue'
import Sidebar from './components/Sidebar.vue'
import MapArea from './components/MapArea.vue'

const searchRoute = ref({
  origin: 'Cinema São Luis',
  destination: 'Faculdade Nova Roma'
})

const selectedRoute = ref(null)

const graphData = ref({
  transport: null,
  car: null,
  moto: null
})
const graphErrors = ref({
  transport: '',
  car: '',
  moto: ''
})

const filterToRouteKey = (filter) => {
  const mapping = {
    'Transporte publico': 'transport',
    'Carro': 'car',
    'Moto': 'moto'
  }
  return mapping[filter] || 'transport'
}

const handleFilterChange = (filter) => {
  selectedRoute.value = filterToRouteKey(filter)
}

const handleSearch = async (route) => {
  searchRoute.value = route
  graphErrors.value = {
    transport: '',
    car: '',
    moto: ''
  }

  try {
    const fetchRoute = async (key, endpoint) => {
      try {
        const response = await fetch(endpoint)
        if (!response.ok) {
          throw new Error(`Backend responded with ${response.status}`)
        }
        const payload = await response.json()
        return { key, data: payload.data, error: '' }
      } catch (error) {
        return {
          key,
          data: null,
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      }
    }

    const results = await Promise.all([
      fetchRoute('transport', '/api/graph/transport?route=true'),
      fetchRoute('car', '/api/graph/road?modal=car&route=true'),
      fetchRoute('moto', '/api/graph/road?modal=moto&route=true')
    ])

    const nextData = { ...graphData.value }
    const nextErrors = { ...graphErrors.value }

    results.forEach((result) => {
      nextData[result.key] = result.data
      nextErrors[result.key] = result.error
      if (result.error) {
        console.error(`Failed to load ${result.key} route:`, result.error)
      }
    })

    graphData.value = nextData
    graphErrors.value = nextErrors
  } catch (error) {
    console.error('Failed to load route data:', error)
  }
}
</script>

<style scoped>
.container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>
