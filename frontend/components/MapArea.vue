<template>
  <div class="map-area">
    <div class="map-placeholder">
      <p>📍 Área reservada para o mapa</p>
      <p class="subtitle">Em desenvolvimento</p>
    </div>
  </div>
</template>

<script setup>
// Componente reservado para integração futura do mapa
</script>

<style scoped>
.map-area {
  flex: 1;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.map-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #bdbdbd;
}

.map-placeholder p {
  margin: 0;
  font-size: 18px;
}

.map-placeholder .subtitle {
  font-size: 14px;
  color: #d0d0d0;
}
</style>
