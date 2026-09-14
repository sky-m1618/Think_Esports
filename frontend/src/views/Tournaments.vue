<template>
  <div class="container section">
    <div class="flex-between page-header">
      <h2 class="mb-0">Tournaments</h2>
    </div>

    <div class="filters card">
      <div class="field mb-0">
        <label>Status</label>
        <select v-model="statusFilter">
          <option value="">All</option>
          <option value="upcoming">Upcoming</option>
          <option value="ongoing">Ongoing</option>
          <option value="completed">Completed</option>
        </select>
      </div>
      <div class="field mb-0">
        <label>Entry Fee</label>
        <select v-model="feeFilter">
          <option value="">All</option>
          <option value="free">Free</option>
          <option value="paid">Paid</option>
        </select>
      </div>
      <div class="field mb-0" style="flex: 1">
        <label>Search</label>
        <input v-model="search" type="text" placeholder="Search tournaments..." />
      </div>
    </div>

    <div v-if="loading" class="grid grid-3">
      <div v-for="i in 6" :key="i" class="card skeleton" style="height: 220px"></div>
    </div>
    <EmptyState
      v-else-if="!filtered.length"
      emoji="🏆"
      title="No tournaments match your filters"
      message="Try adjusting your search or filters."
    />
    <div v-else class="grid grid-3">
      <TournamentCard v-for="t in paginated" :key="t.id" :t="t" />
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button class="btn btn-sm btn-outline" :disabled="page === 1" @click="page--">Prev</button>
      <span>Page {{ page }} of {{ totalPages }}</span>
      <button class="btn btn-sm btn-outline" :disabled="page === totalPages" @click="page++">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import client from "../api/client";
import TournamentCard from "../components/TournamentCard.vue";
import EmptyState from "../components/EmptyState.vue";
import { useToastStore } from "../store/toast";

const toast = useToastStore();
const tournaments = ref([]);
const loading = ref(true);
const statusFilter = ref("");
const feeFilter = ref("");
const search = ref("");
const page = ref(1);
const pageSize = 9;

const filtered = computed(() => {
  return tournaments.value.filter((t) => {
    if (statusFilter.value && t.status !== statusFilter.value) return false;
    if (feeFilter.value === "free" && t.entry_fee > 0) return false;
    if (feeFilter.value === "paid" && t.entry_fee <= 0) return false;
    if (search.value && !t.tournament_name.toLowerCase().includes(search.value.toLowerCase())) return false;
    return true;
  });
});

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)));
const paginated = computed(() => filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize));

watch([statusFilter, feeFilter, search], () => (page.value = 1));

onMounted(async () => {
  try {
    const { data } = await client.get("/tournaments/");
    tournaments.value = data;
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}
.filters {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 28px;
}
.filters .field {
  min-width: 160px;
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 30px;
  font-size: 0.9rem;
}
</style>
