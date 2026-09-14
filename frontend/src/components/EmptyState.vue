<template>
  <div class="empty-state">
    <div class="emoji">{{ emoji }}</div>
    <h3>{{ title }}</h3>
    <p>{{ message }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  emoji: { type: String, default: "🎮" },
  title: { type: String, default: "Nothing here yet" },
  message: { type: String, default: "" },
});
</script>
