<template>
  <div>
    <div class="flex-between">
      <h2>Teams</h2>
      <input v-model="search" type="text" placeholder="Search teams..." class="search-input" />
    </div>

    <div v-if="loading" class="card skeleton" style="height: 300px"></div>
    <EmptyState v-else-if="!filtered.length" emoji="🛡️" title="No teams found" />
    <div v-else class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Team</th>
            <th>Tag</th>
            <th>Leader</th>
            <th>Members</th>
            <th>Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in paginated" :key="t.id">
            <td><router-link :to="`/teams/${t.id}`">{{ t.team_name }}</router-link></td>
            <td>{{ t.team_tag }}</td>
            <td>{{ t.leader_name }}</td>
            <td>{{ t.member_count }}</td>
            <td>{{ formatDate(t.created_at) }}</td>
            <td><button class="btn btn-sm btn-danger" @click="askDelete(t)">Delete</button></td>
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
      title="Delete team?"
      message="This removes the team, its roster and any tournament registrations."
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
const teams = ref([]);
const loading = ref(true);
const search = ref("");
const page = ref(1);
const pageSize = 10;
const showConfirm = ref(false);
const pendingDelete = ref(null);

const filtered = computed(() =>
  teams.value.filter((t) => t.team_name.toLowerCase().includes(search.value.toLowerCase()))
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
    const { data } = await client.get("/teams/");
    teams.value = data;
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}

function askDelete(t) {
  pendingDelete.value = t;
  showConfirm.value = true;
}

async function confirmDelete() {
  try {
    await client.delete(`/teams/${pendingDelete.value.id}`, { role: "admin" });
    toast.success("Team deleted");
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
  min-width: 640px;
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
