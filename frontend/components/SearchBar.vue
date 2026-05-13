<template>
  <div class="search-header">
    <div class="route-inputs">
      <div class="input-group">
        <label>Origem</label>
        <input
          v-model="origin"
          type="text"
          placeholder="Cinema São Luis"
          class="route-input"
          @keyup.enter="performSearch"
        />
      </div>
      <div class="swap-button">
        <button @click="swapLocations" title="Trocar origem e destino">⇅</button>
      </div>
      <div class="input-group">
        <label>Destino</label>
        <input
          v-model="destination"
          type="text"
          placeholder="Faculdade Nova Roma"
          class="route-input"
          @keyup.enter="performSearch"
        />
      </div>
      <button class="search-btn" @click="performSearch">🔍</button>
    </div>
    
    <div class="filters">
      <button
        v-for="filter in filters"
        :key="filter"
        class="filter-btn"
        :class="{ active: selectedFilters.includes(filter) }"
        @click="toggleFilter(filter)"
      >
        {{ getFilterIcon(filter) }} {{ filter }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const origin = ref('Cinema São Luis')
const destination = ref('Faculdade Nova Roma')
const selectedFilters = ref([])

const filters = [
  'Transporte público',
  'Carro',
  'Moto'
]

const filterIcons = {
  'Transporte público': '🚌',
  'Carro': '🚗',
  'Moto': '🏍️'
}

const emit = defineEmits(['search'])

const performSearch = () => {
  emit('search', { origin: origin.value, destination: destination.value })
}

const swapLocations = () => {
  const temp = origin.value
  origin.value = destination.value
  destination.value = temp
}

const toggleFilter = (filter) => {
  const index = selectedFilters.value.indexOf(filter)
  if (index > -1) {
    selectedFilters.value.splice(index, 1)
  } else {
    selectedFilters.value.push(filter)
  }
}

const getFilterIcon = (filter) => {
  return filterIcons[filter] || '📍'
}
</script>

<style scoped>
.search-header {
  background-color: white;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.route-inputs {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.input-group {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 4px;
}

.input-group label {
  font-size: 12px;
  font-weight: 600;
  color: #202124;
}

.route-input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.route-input:focus {
  border-color: #4285f4;
}

.swap-button {
  display: flex;
  margin-bottom: 0;
}

.swap-button button {
  padding: 10px 12px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.swap-button button:hover {
  background-color: #e8e8e8;
  border-color: #4285f4;
}

.search-btn {
  padding: 12px 20px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #3367d6;
}

.filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
  white-space: nowrap;
}

.filter-btn:hover {
  background-color: #e8e8e8;
  border-color: #4285f4;
}

.filter-btn.active {
  background-color: #4285f4;
  color: white;
  border-color: #4285f4;
}
</style>
