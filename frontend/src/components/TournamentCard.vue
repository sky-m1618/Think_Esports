<template>
  <router-link :to="`/tournaments/${t.id}`" class="t-card card card-hover">
    <div class="flex-between">
      <StatusBadge :status="t.status" />
      <span class="entry-fee">{{ t.entry_fee > 0 ? `₹${t.entry_fee} entry` : "Free entry" }}</span>
    </div>
    <h3 class="t-name">{{ t.tournament_name }}</h3>
    <p class="t-desc">{{ t.description }}</p>
    <div class="t-stats">
      <div>
        <span class="label">Prize Pool</span>
        <span class="value">₹{{ formatNumber(t.prize_pool) }}</span>
      </div>
      <div>
        <span class="label">Slots</span>
        <span class="value">{{ t.registered_teams }}/{{ t.max_teams }}</span>
      </div>
    </div>
    <div class="t-progress">
      <div class="t-progress-fill" :style="{ width: pct + '%' }"></div>
    </div>
    <div class="t-date">Starts {{ formatDate(t.start_date) }}</div>
  </router-link>
</template>

<script setup>
import { computed } from "vue";
import StatusBadge from "./StatusBadge.vue";

const props = defineProps({ t: { type: Object, required: true } });

const pct = computed(() =>
  props.t.max_teams ? Math.min(100, Math.round((props.t.registered_teams / props.t.max_teams) * 100)) : 0
);

function formatNumber(n) {
  return Number(n || 0).toLocaleString("en-IN");
}
function formatDate(d) {
  if (!d) return "TBA";
  return new Date(d).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}
</script>

<style scoped>
.t-card {
  display: block;
  color: inherit;
  margin-bottom: 10px;
}
.entry-fee {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-accent-dark);
}
.t-name {
  margin-top: 14px;
  margin-bottom: 6px;
  font-size: 1.15rem;
}
.t-desc {
  font-size: 0.88rem;
  color: var(--color-text-body);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 2.6em;
}
.t-stats {
  display: flex;
  justify-content: space-between;
  margin: 14px 0 10px;
}
.t-stats .label {
  display: block;
  font-size: 0.72rem;
  color: var(--color-text-body);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.t-stats .value {
  display: block;
  font-weight: 700;
  color: var(--color-text-heading);
  font-size: 1rem;
}
.t-progress {
  height: 6px;
  background: #eef2ff;
  border-radius: var(--radius-full);
  overflow: hidden;
}
.t-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
  border-radius: var(--radius-full);
  transition: width var(--transition);
}
.t-date {
  margin-top: 10px;
  font-size: 0.8rem;
  color: var(--color-text-body);
}
</style>
