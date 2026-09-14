<template>
  <span class="badge" :class="`badge-${status}`">{{ label }}</span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({ status: { type: String, required: true } });
const label = computed(() => props.status.charAt(0).toUpperCase() + props.status.slice(1));
</script>
