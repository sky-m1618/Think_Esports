<template>
  <div>
    <h2>Matches &amp; Results</h2>

    <div class="card filter-card">
      <div class="field mb-0" style="max-width: 320px">
        <label>Tournament</label>
        <select v-model="selectedTournament" @change="loadMatches">
          <option value="" disabled>Select a tournament</option>
          <option v-for="t in tournaments" :key="t.id" :value="t.id">{{ t.tournament_name }}</option>
        </select>
      </div>
      <button class="btn btn-primary" :disabled="!selectedTournament" @click="openMatchForm">+ New Match</button>
    </div>

    <div v-if="!selectedTournament" class="empty-state">
      <div class="emoji">🎮</div>
      <h3>Select a tournament</h3>
      <p>Choose a tournament above to manage its matches.</p>
    </div>
    <div v-else-if="loadingMatches" class="card skeleton" style="height: 200px"></div>
    <EmptyState v-else-if="!matches.length" emoji="🗓️" title="No matches scheduled" message="Create the first match above." />
    <div v-else class="match-cards">
      <div v-for="m in matches" :key="m.id" class="card match-card">
        <div class="flex-between">
          <div>
            <strong>{{ m.match_name }}</strong>
            <p class="mb-0" style="font-size: 0.82rem">{{ m.map_name }} &middot; {{ formatDate(m.match_date) }}</p>
          </div>
          <div class="flex gap-8">
            <select v-model="m.status" class="status-select" @change="updateStatus(m)">
              <option value="scheduled">Scheduled</option>
              <option value="live">Live</option>
              <option value="completed">Completed</option>
            </select>
            <button class="btn btn-sm btn-danger" @click="deleteMatch(m)">Delete</button>
          </div>
        </div>

        <button class="btn btn-sm btn-secondary" style="margin-top: 12px" @click="openResultsForm(m)">
          Enter Results
        </button>
      </div>
    </div>

    <!-- Create match modal -->
    <teleport to="body">
      <div v-if="showMatchForm" class="modal-backdrop" @click.self="showMatchForm = false">
        <div class="modal-card form-modal">
          <h3>New Match</h3>
          <form @submit.prevent="saveMatch">
            <div class="field">
              <label>Match Name</label>
              <input v-model="matchForm.match_name" type="text" placeholder="Match 1" required />
            </div>
            <div class="grid grid-2">
              <div class="field">
                <label>Map</label>
                <select v-model="matchForm.map_name">
                  <option v-for="mp in maps" :key="mp" :value="mp">{{ mp }}</option>
                </select>
              </div>
              <div class="field">
                <label>Date &amp; Time</label>
                <input v-model="matchForm.match_date" type="datetime-local" required />
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-outline" @click="showMatchForm = false">Cancel</button>
              <button class="btn btn-primary" :disabled="savingMatch">Create Match</button>
            </div>
          </form>
        </div>
      </div>
    </teleport>

    <!-- Results entry modal -->
    <teleport to="body">
      <div v-if="showResultsForm" class="modal-backdrop" @click.self="showResultsForm = false">
        <div class="modal-card form-modal">
          <h3>Results — {{ activeMatch?.match_name }}</h3>
          <form @submit.prevent="saveResult">
            <div class="field">
              <label>Team</label>
              <select v-model="resultForm.team_id" required>
                <option value="" disabled>Select team</option>
                <option v-for="t in registeredTeams" :key="t.id" :value="t.id">{{ t.team_name }}</option>
              </select>
            </div>
            <div class="grid grid-3">
              <div class="field">
                <label>Placement</label>
                <input v-model.number="resultForm.placement" type="number" min="1" required />
              </div>
              <div class="field">
                <label>Kills</label>
                <input v-model.number="resultForm.kills" type="number" min="0" />
              </div>
              <div class="field">
                <label>Damage</label>
                <input v-model.number="resultForm.damage" type="number" min="0" step="0.1" />
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-outline" @click="showResultsForm = false">Close</button>
              <button class="btn btn-primary" :disabled="savingResult">Save Result</button>
            </div>
          </form>

          <div v-if="activeMatchResults.length" class="results-table">
            <h4>Entered so far</h4>
            <table>
              <thead>
                <tr>
                  <th>Team</th>
                  <th>Placement</th>
                  <th>Kills</th>
                  <th>Points</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in activeMatchResults" :key="r.id">
                  <td>{{ r.team_name }}</td>
                  <td>{{ r.placement }}</td>
                  <td>{{ r.kills }}</td>
                  <td>{{ r.points }}</td>
                  <td><button class="btn btn-sm btn-danger" @click="deleteResult(r)">✕</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import client from "../../api/client";
import { useToastStore } from "../../store/toast";
import EmptyState from "../../components/EmptyState.vue";

const toast = useToastStore();
const maps = ["Erangel", "Miramar", "Sanhok", "Vikendi", "Livik"];

const tournaments = ref([]);
const selectedTournament = ref("");
const matches = ref([]);
const loadingMatches = ref(false);
const registeredTeams = ref([]);

const showMatchForm = ref(false);
const savingMatch = ref(false);
const matchForm = ref({ match_name: "", map_name: "Erangel", match_date: "" });

const showResultsForm = ref(false);
const savingResult = ref(false);
const activeMatch = ref(null);
const activeMatchResults = ref([]);
const resultForm = ref({ team_id: "", placement: 1, kills: 0, damage: 0 });

function formatDate(d) {
  return d
    ? new Date(d).toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })
    : "";
}

async function loadTournaments() {
  const { data } = await client.get("/tournaments/");
  tournaments.value = data;
}

async function loadMatches() {
  if (!selectedTournament.value) return;
  loadingMatches.value = true;
  try {
    const [{ data: matchData }, { data: tData }] = await Promise.all([
      client.get(`/matches/tournament/${selectedTournament.value}`),
      client.get(`/tournaments/${selectedTournament.value}`),
    ]);
    matches.value = matchData;
    registeredTeams.value = (tData.registrations || []).map((r) => r.team).filter(Boolean);
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loadingMatches.value = false;
  }
}

function openMatchForm() {
  matchForm.value = { match_name: "", map_name: "Erangel", match_date: "" };
  showMatchForm.value = true;
}

async function saveMatch() {
  savingMatch.value = true;
  try {
    await client.post(
      "/matches/",
      { tournament_id: selectedTournament.value, ...matchForm.value },
      { role: "admin" }
    );
    toast.success("Match created");
    showMatchForm.value = false;
    await loadMatches();
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    savingMatch.value = false;
  }
}

async function updateStatus(m) {
  try {
    await client.put(`/matches/${m.id}`, { status: m.status }, { role: "admin" });
    toast.success("Match status updated");
  } catch (e) {
    toast.error(e.friendlyMessage);
  }
}

async function deleteMatch(m) {
  try {
    await client.delete(`/matches/${m.id}`, { role: "admin" });
    toast.success("Match deleted");
    await loadMatches();
  } catch (e) {
    toast.error(e.friendlyMessage);
  }
}

async function openResultsForm(m) {
  activeMatch.value = m;
  resultForm.value = { team_id: "", placement: 1, kills: 0, damage: 0 };
  showResultsForm.value = true;
  try {
    const { data } = await client.get(`/matches/${m.id}`);
    activeMatchResults.value = data.results || [];
  } catch (e) {
    toast.error(e.friendlyMessage);
  }
}

async function saveResult() {
  savingResult.value = true;
  try {
    await client.post(`/matches/${activeMatch.value.id}/results`, resultForm.value, { role: "admin" });
    toast.success("Result saved");
    const { data } = await client.get(`/matches/${activeMatch.value.id}`);
    activeMatchResults.value = data.results || [];
    resultForm.value = { team_id: "", placement: 1, kills: 0, damage: 0 };
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    savingResult.value = false;
  }
}

async function deleteResult(r) {
  try {
    await client.delete(`/matches/results/${r.id}`, { role: "admin" });
    activeMatchResults.value = activeMatchResults.value.filter((x) => x.id !== r.id);
    toast.success("Result removed");
  } catch (e) {
    toast.error(e.friendlyMessage);
  }
}

onMounted(loadTournaments);
</script>

<style scoped>
.filter-card {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.match-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.status-select {
  min-height: 36px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  font-size: 0.82rem;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(30, 41, 59, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1500;
  padding: 20px;
  overflow-y: auto;
}
.form-modal {
  background: white;
  border-radius: var(--radius-lg);
  padding: 28px;
  max-width: 560px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.results-table {
  margin-top: 20px;
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
}
.results-table table {
  width: 100%;
  border-collapse: collapse;
}
.results-table th,
.results-table td {
  text-align: left;
  padding: 8px 10px;
  font-size: 0.85rem;
  border-bottom: 1px solid var(--color-border);
}
</style>
