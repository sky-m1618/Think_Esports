<template>
  <div class="container section">
    <div v-if="loading" class="card skeleton" style="height: 320px"></div>
    <div v-else-if="!tournament" class="empty-state">
      <div class="emoji">🔍</div>
      <h3>Tournament not found</h3>
    </div>
    <template v-else>
      <div class="card detail-hero">
        <div class="flex-between">
          <StatusBadge :status="tournament.status" />
          <router-link :to="`/leaderboard/${tournament.id}`" class="btn btn-sm btn-secondary">View Leaderboard</router-link>
        </div>
        <h2>{{ tournament.tournament_name }}</h2>
        <p>{{ tournament.description }}</p>

        <div class="stat-grid">
          <div>
            <span class="label">Prize Pool</span>
            <span class="value">₹{{ Number(tournament.prize_pool).toLocaleString("en-IN") }}</span>
          </div>
          <div>
            <span class="label">Entry Fee</span>
            <span class="value">{{ tournament.entry_fee > 0 ? `₹${tournament.entry_fee}` : "Free" }}</span>
          </div>
          <div>
            <span class="label">Slots</span>
            <span class="value">{{ tournament.registered_teams }}/{{ tournament.max_teams }}</span>
          </div>
          <div>
            <span class="label">Starts</span>
            <span class="value">{{ formatDate(tournament.start_date) }}</span>
          </div>
        </div>

        <div class="register-box" v-if="tournament.status !== 'completed'">
          <template v-if="!playerStore.isLoggedIn">
            <router-link to="/enter" class="btn btn-accent">Sign in to Register</router-link>
          </template>
          <template v-else-if="!playerStore.teams.length">
            <p class="mb-0">You need a team to register.</p>
            <router-link to="/teams/create" class="btn btn-accent">Create Team</router-link>
          </template>
          <template v-else>
            <select v-model="selectedTeam" class="team-select">
              <option value="" disabled>Select a team you lead</option>
              <option v-for="t in leaderTeams" :key="t.id" :value="t.id">{{ t.team_name }}</option>
            </select>
            <button class="btn btn-accent" :disabled="!selectedTeam || registering" @click="register">
              <span v-if="registering" class="spinner"></span>
              <span v-else>Register Team</span>
            </button>
          </template>
        </div>
      </div>

      <section class="section">
        <h3>Registered Teams ({{ tournament.registrations.length }})</h3>
        <EmptyState v-if="!tournament.registrations.length" emoji="👥" title="No teams registered yet" />
        <div v-else class="grid grid-3">
          <div v-for="r in tournament.registrations" :key="r.id" class="card reg-card">
            <router-link :to="`/teams/${r.team_id}`"><strong>{{ r.team?.team_name }}</strong></router-link>
            <span class="badge" :class="`badge-${r.payment_status}`">{{ r.payment_status }}</span>
          </div>
        </div>
      </section>

      <section class="section" v-if="tournament.matches.length">
        <h3>Matches</h3>
        <div class="match-list">
          <div v-for="m in tournament.matches" :key="m.id" class="card match-row">
            <div>
              <strong>{{ m.match_name }}</strong>
              <p class="mb-0" style="font-size: 0.82rem">{{ m.map_name }} &middot; {{ formatDate(m.match_date) }}</p>
            </div>
            <StatusBadge :status="m.status === 'live' ? 'ongoing' : m.status === 'scheduled' ? 'upcoming' : 'completed'" />
          </div>
        </div>
      </section>

      <section class="section" v-if="tournament.rules">
        <h3>Rules</h3>
        <div class="card">
          <p class="mb-0" style="white-space: pre-wrap">{{ tournament.rules }}</p>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import client from "../api/client";
import { usePlayerStore } from "../store/player";
import { useToastStore } from "../store/toast";
import StatusBadge from "../components/StatusBadge.vue";
import EmptyState from "../components/EmptyState.vue";

const route = useRoute();
const playerStore = usePlayerStore();
const toast = useToastStore();

const tournament = ref(null);
const loading = ref(true);
const selectedTeam = ref("");
const registering = ref(false);

const leaderTeams = computed(() =>
  playerStore.teams.filter((t) => t.leader_phone === playerStore.player?.phone_number)
);

function formatDate(d) {
  return d
    ? new Date(d).toLocaleString(undefined, { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })
    : "TBA";
}

async function load() {
  loading.value = true;
  try {
    const { data } = await client.get(`/tournaments/${route.params.id}`);
    tournament.value = data;
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}

async function register() {
  registering.value = true;
  try {
    await client.post(
      `/tournaments/${route.params.id}/register`,
      { team_id: selectedTeam.value },
      { role: "player" }
    );
    toast.success("Team registered! Payment status: pending");
    await load();
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    registering.value = false;
  }
}

onMounted(async () => {
  await load();
  if (playerStore.isLoggedIn) {
    try {
      await playerStore.fetchDashboard();
    } catch {
      /* not fatal for viewing the tournament */
    }
  }
});
</script>

<style scoped>
.detail-hero h2 {
  margin-top: 14px;
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 20px 0;
}
.stat-grid .label {
  display: block;
  font-size: 0.72rem;
  text-transform: uppercase;
  color: var(--color-text-body);
}
.stat-grid .value {
  display: block;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--color-text-heading);
}
@media (max-width: 640px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.register-box {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}
.team-select {
  min-height: 44px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  padding: 0 12px;
}
.reg-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.match-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.match-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
