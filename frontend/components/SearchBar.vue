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
        <button @click="swapLocations" title="Trocar origem e destino">
          <span class="mdi mdi-swap-horizontal"></span>
        </button>
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

      <button class="search-btn" @click="performSearch">
        <span class="mdi mdi-map-search-outline"></span>
      </button>

    </div>

    <div class="filters">
      <button
        v-for="filter in filters"
        :key="filter"
        class="filter-btn"
        :class="{ active: selectedFilter === filter }"
        @click="toggleFilter(filter)"
      >
        <span :class="['mdi', getFilterIcon(filter)]"></span>

        {{ filter }}
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const origin = ref('Cinema São Luis')
const destination = ref('Faculdade Nova Roma')

const selectedFilter = ref('Transporte publico')

const filters = [
  'Transporte publico',
  'Carro',
  'Moto'
]

const filterIcons = {
  'Transporte publico': 'mdi-bus',
  'Carro': 'mdi-car',
  'Moto': 'mdi-motorbike'
}

const emit = defineEmits(['search', 'filter-change'])

const performSearch = () => {
  emit('search', {
    origin: origin.value,
    destination: destination.value,
    mode: selectedFilter.value
  })
}

const swapLocations = () => {
  const temp = origin.value
  origin.value = destination.value
  destination.value = temp
}

const toggleFilter = (filter) => {
  selectedFilter.value = filter
  emit('filter-change', filter)
}

const getFilterIcon = (filter) => {
  return filterIcons[filter] || 'mdi-map-marker'
}
</script>

<style scoped>
.search-header {
  background-color: #1e1e1e;

  padding: 15px;

  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);

  display: flex;
  flex-direction: column;
  gap: 12px;

  transition: all 0.3s;
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
  color: white;
}

.route-input {
  padding: 10px 12px;

  background-color: #2c2c2c;
  color: white;

  border: 1px solid #555;
  border-radius: 4px;

  font-size: 14px;

  outline: none;

  transition: all 0.3s;
}

.route-input::placeholder {
  color: #aaa;
}

.route-input:focus {
  border-color: #4285f4;
}

.swap-button {
  display: flex;
}

.swap-button button {
  padding: 10px 12px;

  background-color: #2c2c2c;
  color: white;

  border: 1px solid #555;
  border-radius: 4px;

  cursor: pointer;

  font-size: 18px;

  transition: all 0.3s;
}

.swap-button button:hover {
  background-color: #3a3a3a;
  border-color: #4285f4;
}

.search-btn {
  padding: 12px 20px;

  background-color: #4285f4;
  color: white;

  border: none;
  border-radius: 4px;

  cursor: pointer;

  font-size: 18px;

  transition: all 0.3s;
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
  display: flex;
  align-items: center;
  gap: 6px;

  padding: 8px 16px;

  background-color: #2c2c2c;
  color: white;

  border: 1px solid #555;
  border-radius: 20px;

  cursor: pointer;

  font-size: 13px;

  transition: all 0.3s;

  white-space: nowrap;
}

.filter-btn .mdi {
  font-size: 16px;
}

.filter-btn:hover {
  background-color: #3a3a3a;
  border-color: #4285f4;
}

.filter-btn.active {
  background-color: #4285f4;
  border-color: #4285f4;
}
</style>