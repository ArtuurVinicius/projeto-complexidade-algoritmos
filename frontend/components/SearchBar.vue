<template>
  <div class="search-header" :class="{ dark: isDark }">

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

      <button class="theme-btn" @click="toggleTheme">
        <span
          class="mdi"
          :class="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        ></span>
      </button>

    </div>

    <div class="filters">
      <button
        v-for="filter in filters"
        :key="filter"
        class="filter-btn"
        :class="{ active: selectedFilters.includes(filter) }"
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

const isDark = ref(false)

const selectedFilters = ref([])

const filters = [
  'Transporte público',
  'Carro',
  'Moto'
]

const filterIcons = {
  'Transporte público': 'mdi-bus',
  'Carro': 'mdi-car',
  'Moto': 'mdi-motorbike'
}

const emit = defineEmits(['search'])

const performSearch = () => {
  emit('search', {
    origin: origin.value,
    destination: destination.value
  })
}

const swapLocations = () => {
  const temp = origin.value
  origin.value = destination.value
  destination.value = temp
}

const toggleTheme = () => {
  isDark.value = !isDark.value
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
  return filterIcons[filter] || 'mdi-map-marker'
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
  color: #202124;

  transition: color 0.3s;
}

.route-input {
  padding: 10px 12px;

  border: 1px solid #ddd;
  border-radius: 4px;

  font-size: 14px;

  outline: none;

  transition: all 0.3s;
}

.route-input:focus {
  border-color: #4285f4;
}

.swap-button {
  display: flex;
}

.swap-button button {
  padding: 10px 12px;

  background-color: #abd5ff;

  border: 1px solid #ddd;
  border-radius: 4px;

  cursor: pointer;

  font-size: 18px;

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

  font-size: 18px;

  transition: all 0.3s;
}

.search-btn:hover {
  background-color: #3367d6;
}

.theme-btn {
  padding: 12px;

  background-color: #222;
  color: white;

  border: none;
  border-radius: 4px;

  cursor: pointer;

  font-size: 18px;

  transition: all 0.3s;
}

.theme-btn:hover {
  opacity: 0.9;
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

  background-color: #abd5ff;

  border: 1px solid #ddd;
  border-radius: 20px;

  cursor: pointer;

  font-size: 13px;
  color: black;

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

.filter-btn .mdi {
  font-size: 16px;
}

.filter-btn.active .mdi {
  color: white;
}

/* DARK MODE */

.dark {
  background-color: #1e1e1e;
}

.dark .input-group label {
  color: white;
}

.dark .route-input {
  background-color: #2c2c2c;
  color: white;
  border-color: #555;
}

.dark .route-input::placeholder {
  color: #aaa;
}

.dark .swap-button button {
  background-color: #2c2c2c;
  color: white;
  border-color: #555;
}

.dark .swap-button button:hover {
  background-color: #3a3a3a;
}

.dark .filter-btn {
  background-color: #2c2c2c;
  color: white;
  border-color: #555;
}

.dark .filter-btn .mdi {
  color: white;
}

.dark .filter-btn:hover {
  background-color: #3a3a3a;
}

.dark .filter-btn.active {
  background-color: #4285f4;
  border-color: #4285f4;
}

.dark .theme-btn {
  background-color: #f5f5f5;
  color: black;
}
</style>