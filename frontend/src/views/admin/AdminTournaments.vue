<template>
  <div>
    <div class="flex-between">
      <h2>Tournaments</h2>
      <button class="btn btn-primary" @click="openCreate">+ New Tournament</button>
    </div>

    <div v-if="loading" class="card skeleton" style="height: 300px"></div>
    <EmptyState v-else-if="!tournaments.length" emoji="🏆" title="No tournaments yet" />
    <div v-else class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Slots</th>
            <th>Prize Pool</th>
            <th>Starts</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tournaments" :key="t.id">
            <td>{{ t.tournament_name }}</td>
            <td><StatusBadge :status="t.status" /></td>
            <td>{{ t.registered_teams }}/{{ t.max_teams }}</td>
            <td>₹{{ Number(t.prize_pool).toLocaleString("en-IN") }}</td>
            <td>{{ formatDate(t.start_date) }}</td>
            <td class="actions">
              <button class="btn btn-sm btn-outline" @click="openEdit(t)">Edit</button>
              <button class="btn btn-sm btn-danger" @click="askDelete(t)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <teleport to="body">
      <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
        <div class="modal-card form-modal">
          <h3>{{ editing ? "Edit Tournament" : "New Tournament" }}</h3>
          <form @submit.prevent="save">
            <div class="field">
              <label>Tournament Name</label>
              <input v-model="form.tournament_name" type="text" required />
            </div>
            <div class="field">
              <label>Description</label>
              <textarea v-model="form.description"></textarea>
            </div>
            <div class="grid grid-2">
              <div class="field">
                <label>Entry Fee (₹)</label>
                <input v-model.number="form.entry_fee" type="number" min="0" />
              </div>
              <div class="field">
                <label>Prize Pool (₹)</label>
                <input v-model.number="form.prize_pool" type="number" min="0" />
              </div>
              <div class="field">
                <label>Max Teams</label>
                <input v-model.number="form.max_teams" type="number" min="1" required />
              </div>
              <div class="field">
                <label>Status</label>
                <select v-model="form.status">
                  <option value="upcoming">Upcoming</option>
                  <option value="ongoing">Ongoing</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div class="field">
                <label>Start Date</label>
                <input v-model="form.start_date" type="datetime-local" required />
              </div>
              <div class="field">
                <label>End Date</label>
                <input v-model="form.end_date" type="datetime-local" />
              </div>
            </div>
            <div class="field">
              <label>Rules</label>
              <textarea v-model="form.rules"></textarea>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-outline" @click="showForm = false">Cancel</button>
              <button class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner spinner-dark"></span>
                <span v-else>{{ editing ? "Save Changes" : "Create" }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </teleport>

    <ConfirmModal
      v-model="showDeleteConfirm"
      title="Delete tournament?"
      message="This will remove the tournament and all its registrations and matches."
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import client from "../../api/client";
import { useToastStore } from "../../store/toast";
import StatusBadge from "../../components/StatusBadge.vue";
import EmptyState from "../../components/EmptyState.vue";
import ConfirmModal from "../../components/ConfirmModal.vue";

const toast = useToastStore();
const tournaments = ref([]);
const loading = ref(true);
const showForm = ref(false);
const editing = ref(null);
const saving = ref(false);
const showDeleteConfirm = ref(false);
const pendingDelete = ref(null);

const blankForm = () => ({
  tournament_name: "",
  description: "",
  entry_fee: 0,
  prize_pool: 0,
  max_teams: 16,
  status: "upcoming",
  start_date: "",
  end_date: "",
  rules: "",
});
const form = ref(blankForm());

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "TBA";
}

async function load() {
  loading.value = true;
  try {
    const { data } = await client.get("/tournaments/");
    tournaments.value = data;
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editing.value = null;
  form.value = blankForm();
  showForm.value = true;
}

function toLocalInput(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function openEdit(t) {
  editing.value = t;
  form.value = {
    tournament_name: t.tournament_name,
    description: t.description,
    entry_fee: t.entry_fee,
    prize_pool: t.prize_pool,
    max_teams: t.max_teams,
    status: t.status,
    start_date: toLocalInput(t.start_date),
    end_date: toLocalInput(t.end_date),
    rules: t.rules || "",
  };
  showForm.value = true;
}

async function save() {
  saving.value = true;
  try {
    const payload = { ...form.value };
    if (editing.value) {
      await client.put(`/tournaments/${editing.value.id}`, payload, { role: "admin" });
      toast.success("Tournament updated");
    } else {
      await client.post("/tournaments/", payload, { role: "admin" });
      toast.success("Tournament created");
    }
    showForm.value = false;
    await load();
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    saving.value = false;
  }
}

function askDelete(t) {
  pendingDelete.value = t;
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  try {
    await client.delete(`/tournaments/${pendingDelete.value.id}`, { role: "admin" });
    toast.success("Tournament deleted");
    await load();
  } catch (e) {
    toast.error(e.friendlyMessage);
  }
}

onMounted(load);
</script>

<style scoped>
.table-wrap {
  overflow-x: auto;
  padding: 0;
}
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 720px;
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
  margin-top: 10px;
}
</style>
