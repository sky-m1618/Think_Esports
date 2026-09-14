<template>
  <div class="container section">
    <div v-if="loading" class="card skeleton" style="height: 220px"></div>
    <div v-else-if="!team" class="empty-state">
      <div class="emoji">🔍</div>
      <h3>Team not found</h3>
    </div>
    <template v-else>
      <div class="card team-header">
        <div class="team-avatar-lg">
          <img v-if="team.logo_url" :src="team.logo_url" alt="" />
          <span v-else>{{ team.team_tag }}</span>
        </div>
        <div class="flex-1">
          <h2 class="mb-0">{{ team.team_name }}</h2>
          <p class="mb-0">
            <span class="tag-pill">{{ team.team_tag }}</span>
            &middot; {{ team.member_count }} members &middot; Created {{ formatDate(team.created_at) }}
          </p>
        </div>
      </div>

      <section class="section">
        <h3>Roster</h3>
        <div class="grid grid-2">
          <div v-for="m in team.members" :key="m.id" class="card member-card">
            <div>
              <strong>{{ m.player_name }}</strong>
              <p class="mb-0" style="font-size: 0.8rem">{{ m.player_phone }}</p>
            </div>
            <span class="badge" :class="m.role === 'leader' ? 'badge-confirmed' : 'badge-upcoming'">{{ m.role }}</span>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import client from "../api/client";
import { useToastStore } from "../store/toast";

const route = useRoute();
const toast = useToastStore();
const team = ref(null);
const loading = ref(true);

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "";
}

onMounted(async () => {
  try {
    const { data } = await client.get(`/teams/${route.params.id}`);
    team.value = data;
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.team-header {
  display: flex;
  align-items: center;
  gap: 20px;
}
.team-avatar-lg {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-secondary-light));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
  color: var(--color-primary-dark);
  overflow: hidden;
  flex-shrink: 0;
}
.team-avatar-lg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.tag-pill {
  background: #eef2ff;
  color: var(--color-primary-dark);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 600;
}
.member-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
