<template>
  <div class="container section">
    <h2>Leaderboard</h2>

    <div v-if="loading" class="card skeleton" style="height: 320px"></div>
    <EmptyState v-else-if="!rows.length" emoji="📊" title="No results yet" message="Results will appear once matches are played." />
    <div v-else class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Team</th>
            <th>Matches</th>
            <th>Kills</th>
            <th>Damage</th>
            <th>Total Points</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in paginated" :key="r.team_id" :class="rankClass(r.rank)">
            <td>
              <span v-if="r.rank <= 3" class="medal">{{ ["🥇", "🥈", "🥉"][r.rank - 1] }}</span>
              <span v-else>{{ r.rank }}</span>
            </td>
            <td>
              <router-link :to="`/teams/${r.team_id}`">
                <strong>{{ r.team_name }}</strong> <span class="tag-pill">{{ r.team_tag }}</span>
              </router-link>
            </td>
            <td>{{ r.matches_played }}</td>
            <td>{{ r.total_kills }}</td>
            <td>{{ r.total_damage.toFixed(0) }}</td>
            <td><strong>{{ r.total_points }}</strong></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button class="btn btn-sm btn-outline" :disabled="page === 1" @click="page--">Prev</button>
      <span>Page {{ page }} of {{ totalPages }}</span>
      <button class="btn btn-sm btn-outline" :disabled="page === totalPages" @click="page++">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import client from "../api/client";
import { useToastStore } from "../store/toast";
import EmptyState from "../components/EmptyState.vue";

const route = useRoute();
const toast = useToastStore();
const rows = ref([]);
const loading = ref(true);
const page = ref(1);
const pageSize = 15;

const totalPages = computed(() => Math.max(1, Math.ceil(rows.value.length / pageSize)));
const paginated = computed(() => rows.value.slice((page.value - 1) * pageSize, page.value * pageSize));

function rankClass(rank) {
  if (rank === 1) return "rank-gold";
  if (rank === 2) return "rank-silver";
  if (rank === 3) return "rank-bronze";
  return "";
}

onMounted(async () => {
  try {
    const { data } = await client.get(`/leaderboard/${route.params.tournamentId}`);
    rows.value = data;
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.table-wrap {
  overflow-x: auto;
  padding: 0;
}
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 640px;
}
th,
td {
  text-align: left;
  padding: 14px 18px;
  font-size: 0.9rem;
  border-bottom: 1px solid var(--color-border);
}
th {
  color: var(--color-text-body);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.rank-gold {
  background: linear-gradient(90deg, #fef9c3, transparent);
}
.rank-silver {
  background: linear-gradient(90deg, #f1f5f9, transparent);
}
.rank-bronze {
  background: linear-gradient(90deg, #ffedd5, transparent);
}
.medal {
  font-size: 1.1rem;
}
.tag-pill {
  background: #eef2ff;
  color: var(--color-primary-dark);
  padding: 1px 8px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 700;
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  font-size: 0.9rem;
}
</style>
