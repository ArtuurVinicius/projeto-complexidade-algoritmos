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
  </div>
</template>

<script setup>
defineProps({
  origin: String,
  destination: String
})
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
  flex: 1;
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
