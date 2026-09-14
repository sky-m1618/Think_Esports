<template>
  <footer class="site-footer">
    <div class="container footer-inner">
      <p class="mb-0">&copy; {{ year }} Arena Tournaments. Not affiliated with PUBG Mobile or Krafton.</p>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear();
</script>

<style scoped>
.site-footer {
  border-top: 1px solid var(--color-border);
  padding: 24px 0;
  margin-top: 60px;
}
.footer-inner {
  text-align: center;
  font-size: 0.85rem;
  color: var(--color-text-body);
}
</style>
