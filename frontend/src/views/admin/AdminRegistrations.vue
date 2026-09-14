<template>
  <div>
    <div class="flex-between">
      <h2>Registrations</h2>
      <select v-model="selectedTournament" @change="loadRegistrations" class="tournament-select">
        <option value="" disabled>Select a tournament</option>
        <option v-for="t in tournaments" :key="t.id" :value="t.id">{{ t.tournament_name }}</option>
      </select>
    </div>

    <div v-if="!selectedTournament" class="empty-state">
      <div class="emoji">📝</div>
      <h3>Select a tournament</h3>
      <p>Choose a tournament above to review its registrations.</p>
    </div>
    <div v-else-if="loading" class="card skeleton" style="height: 260px"></div>
    <EmptyState v-else-if="!registrations.length" emoji="📭" title="No registrations yet" />
    <div v-else class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Team</th>
            <th>Registered</th>
            <th>Payment Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in registrations" :key="r.id">
            <td><router-link :to="`/teams/${r.team_id}`">{{ r.team?.team_name }}</router-link></td>
            <td>{{ formatDate(r.registered_at) }}</td>
            <td><span class="badge" :class="`badge-${r.payment_status}`">{{ r.payment_status }}</span></td>
            <td class="actions">
              <button
                v-if="r.payment_status !== 'confirmed'"
                class="btn btn-sm btn-secondary"
                @click="setStatus(r, 'confirmed')"
              >
                Approve
              </button>
              <button class="btn btn-sm btn-danger" @click="reject(r)">Reject</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import client from "../../api/client";
import { useToastStore } from "../../store/toast";
import EmptyState from "../../components/EmptyState.vue";

const toast = useToastStore();
const tournaments = ref([]);
const selectedTournament = ref("");
const registrations = ref([]);
const loading = ref(false);

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "";
}

async function loadTournaments() {
  const { data } = await client.get("/tournaments/");
  tournaments.value = data;
}

async function loadRegistrations() {
  if (!selectedTournament.value) return;
  loading.value = true;
  try {
    const { data } = await client.get(`/tournaments/${selectedTournament.value}`);
    registrations.value = data.registrations || [];
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}

async function setStatus(r, status) {
  try {
    await client.put(`/tournaments/registrations/${r.id}`, { payment_status: status }, { role: "admin" });
    toast.success("Payment status updated");
    await loadRegistrations();
  } catch (e) {
    toast.error(e.friendlyMessage);
  }
}

async function reject(r) {
  try {
    await client.delete(`/tournaments/registrations/${r.id}`, { role: "admin" });
    toast.success("Registration removed");
    await loadRegistrations();
  } catch (e) {
    toast.error(e.friendlyMessage);
  }
}

onMounted(loadTournaments);
</script>

<style scoped>
.tournament-select {
  min-height: 42px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  padding: 0 14px;
  min-width: 240px;
}
.table-wrap {
  overflow-x: auto;
  padding: 0;
  margin-top: 20px;
}
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 560px;
}
th,
td {
  text-align: left;
  padding: 14px 18px;
  font-size: 0.88rem;
  border-bottom: 1px solid var(--color-border);
}
.actions {
  display: flex;
  gap: 8px;
}
</style>
