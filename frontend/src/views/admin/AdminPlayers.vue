<template>
  <div>
    <div class="flex-between">
      <h2>Players</h2>
      <input v-model="search" type="text" placeholder="Search players..." class="search-input" />
    </div>

    <div v-if="loading" class="card skeleton" style="height: 300px"></div>
    <EmptyState v-else-if="!filtered.length" emoji="👤" title="No players found" />
    <div v-else class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Joined</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in paginated" :key="p.id">
            <td>{{ p.player_name }}</td>
            <td>{{ p.phone_number }}</td>
            <td>{{ formatDate(p.created_at) }}</td>
            <td><button class="btn btn-sm btn-danger" @click="askDelete(p)">Delete</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button class="btn btn-sm btn-outline" :disabled="page === 1" @click="page--">Prev</button>
      <span>Page {{ page }} of {{ totalPages }}</span>
      <button class="btn btn-sm btn-outline" :disabled="page === totalPages" @click="page++">Next</button>
    </div>

    <ConfirmModal
      v-model="showConfirm"
      title="Delete player?"
      message="This removes the player record. Existing team memberships referencing this phone number may be affected."
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import client from "../../api/client";
import { useToastStore } from "../../store/toast";
import EmptyState from "../../components/EmptyState.vue";
import ConfirmModal from "../../components/ConfirmModal.vue";

const toast = useToastStore();
const players = ref([]);
const loading = ref(true);
const search = ref("");
const page = ref(1);
const pageSize = 12;
const showConfirm = ref(false);
const pendingDelete = ref(null);

const filtered = computed(() =>
  players.value.filter(
    (p) =>
      p.player_name.toLowerCase().includes(search.value.toLowerCase()) ||
      p.phone_number.includes(search.value)
  )
);
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)));
const paginated = computed(() => filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize));

watch(search, () => (page.value = 1));

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "";
}

async function load() {
  loading.value = true;
  try {
    const { data } = await client.get("/players/", { role: "admin" });
    players.value = data;
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}

function askDelete(p) {
  pendingDelete.value = p;
  showConfirm.value = true;
}

async function confirmDelete() {
  try {
    await client.delete(`/players/${pendingDelete.value.id}`, { role: "admin" });
    toast.success("Player deleted");
    await load();
  } catch (e) {
    toast.error(e.friendlyMessage);
  }
}

onMounted(load);
</script>

<style scoped>
.search-input {
  min-height: 40px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  padding: 0 14px;
  min-width: 220px;
}
.table-wrap {
  overflow-x: auto;
  padding: 0;
  margin-top: 20px;
}
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 520px;
}
th,
td {
  text-align: left;
  padding: 14px 18px;
  font-size: 0.88rem;
  border-bottom: 1px solid var(--color-border);
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  font-size: 0.9rem;
}
</style>
