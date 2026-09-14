<template>
  <div class="container section">
    <div class="dash-header card">
      <div>
        <h2>Welcome back, {{ playerStore.player?.player_name }} 👋</h2>
        <p class="mb-0">{{ playerStore.player?.phone_number }}</p>
      </div>
      <div class="dash-stats">
        <div>
          <span class="stat-value">{{ playerStore.teams.length }}</span>
          <span class="stat-label">Teams</span>
        </div>
        <div>
          <span class="stat-value">{{ playerStore.registrations.length }}</span>
          <span class="stat-label">Registrations</span>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <router-link to="/teams/create" class="btn btn-accent">+ Create Team</router-link>
      <router-link to="/tournaments" class="btn btn-outline">Browse Tournaments</router-link>
    </div>

    <section class="section">
      <h3>My Teams</h3>
      <div v-if="loading" class="grid grid-3">
        <div v-for="i in 2" :key="i" class="card skeleton" style="height: 140px"></div>
      </div>
      <EmptyState
        v-else-if="!playerStore.teams.length"
        emoji="🛡️"
        title="No teams yet"
        message="Create a squad to start registering for tournaments."
      >
        <router-link to="/teams/create" class="btn btn-primary" style="margin-top: 12px">Create Team</router-link>
      </EmptyState>
      <div v-else class="grid grid-3">
        <router-link v-for="team in playerStore.teams" :key="team.id" :to="`/teams/${team.id}`" class="card card-hover">
          <div class="flex-between">
            <strong>{{ team.team_name }}</strong>
            <span class="tag-pill">{{ team.team_tag }}</span>
          </div>
          <p class="mb-0" style="margin-top: 8px; font-size: 0.85rem">{{ team.member_count }} / 5 members</p>
        </router-link>
      </div>
    </section>

    <section class="section">
      <h3>My Registrations</h3>
      <div v-if="loading" class="card skeleton" style="height: 100px"></div>
      <EmptyState
        v-else-if="!playerStore.registrations.length"
        emoji="📝"
        title="No registrations yet"
        message="Register one of your teams for an upcoming tournament."
      />
      <div v-else class="reg-list">
        <div v-for="r in playerStore.registrations" :key="r.id" class="card reg-row">
          <div>
            <strong>{{ r.team?.team_name }}</strong>
            <p class="mb-0" style="font-size: 0.82rem">Registered {{ formatDate(r.registered_at) }}</p>
          </div>
          <span class="badge" :class="`badge-${r.payment_status}`">{{ r.payment_status }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { usePlayerStore } from "../store/player";
import { useToastStore } from "../store/toast";
import EmptyState from "../components/EmptyState.vue";

const playerStore = usePlayerStore();
const toast = useToastStore();
const loading = ref(true);

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString(undefined, { day: "numeric", month: "short" }) : "";
}

onMounted(async () => {
  try {
    await playerStore.fetchDashboard();
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.dash-stats {
  display: flex;
  gap: 28px;
}
.stat-value {
  display: block;
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--color-primary);
  text-align: center;
}
.stat-label {
  display: block;
  font-size: 0.78rem;
  color: var(--color-text-body);
  text-align: center;
}
.quick-actions {
  display: flex;
  gap: 14px;
  margin-top: 24px;
  flex-wrap: wrap;
}
.tag-pill {
  background: #eef2ff;
  color: var(--color-primary-dark);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  font-weight: 700;
}
.reg-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.reg-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
