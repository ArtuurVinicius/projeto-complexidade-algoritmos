<template>
  <div class="container">
    <search-bar @search="handleSearch" />
    <div class="main-content">
      <sidebar :origin="searchRoute.origin" :destination="searchRoute.destination" />
      <map-area />
    </div>
  </div>
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

const handleSearch = (route) => {
  searchRoute.value = route
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
