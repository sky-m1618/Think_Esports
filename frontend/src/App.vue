<template>
  <div id="app-shell">
    <NavBar v-if="!isAdminRoute" />
    <main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <SiteFooter v-if="!isAdminRoute" />
    <ToastContainer />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import NavBar from "./components/NavBar.vue";
import SiteFooter from "./components/SiteFooter.vue";
import ToastContainer from "./components/ToastContainer.vue";

const route = useRoute();
const isAdminRoute = computed(() => route.path.startsWith("/admin") && route.name !== "admin-login");
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 160ms ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

main {
  min-height: 70vh;
}
</style>
