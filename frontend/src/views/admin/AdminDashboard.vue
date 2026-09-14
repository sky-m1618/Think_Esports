<template>
  <div>
    <h2>Dashboard</h2>
    <div v-if="loading" class="grid grid-4">
      <div v-for="i in 4" :key="i" class="card skeleton" style="height: 100px"></div>
    </div>
    <div v-else class="grid grid-4">
      <div class="card stat-card">
        <span class="stat-icon">👤</span>
        <span class="stat-value">{{ stats.total_players }}</span>
        <span class="stat-label">Total Players</span>
      </div>
      <div class="card stat-card">
        <span class="stat-icon">🛡️</span>
        <span class="stat-value">{{ stats.total_teams }}</span>
        <span class="stat-label">Total Teams</span>
      </div>
      <div class="card stat-card">
        <span class="stat-icon">🏆</span>
        <span class="stat-value">{{ stats.total_tournaments }}</span>
        <span class="stat-label">Tournaments ({{ stats.ongoing_tournaments }} live)</span>
      </div>
      <div class="card stat-card">
        <span class="stat-icon">💰</span>
        <span class="stat-value">₹{{ Number(stats.total_revenue).toLocaleString("en-IN") }}</span>
        <span class="stat-label">Confirmed Revenue</span>
      </div>
    </div>

    <div class="card" style="margin-top: 24px" v-if="!loading && stats.pending_payments > 0">
      <p class="mb-0">
        ⚠️ {{ stats.pending_payments }} registration(s) awaiting payment confirmation.
        <router-link to="/admin/registrations">Review now &rarr;</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import client from "../../api/client";
import { useToastStore } from "../../store/toast";

const toast = useToastStore();
const loading = ref(true);
const stats = ref({});

onMounted(async () => {
  try {
    const { data } = await client.get("/admin/stats", { role: "admin" });
    stats.value = data;
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.stat-card {
  text-align: center;
}
.stat-icon {
  font-size: 1.6rem;
  display: block;
  margin-bottom: 8px;
}
.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text-heading);
}
.stat-label {
  display: block;
  font-size: 0.8rem;
  color: var(--color-text-body);
  margin-top: 4px;
}
</style>
