<template>
  <header class="navbar">
    <div class="container navbar-inner">
      <router-link to="/" class="brand">
        <span class="brand-mark">⬢</span>
        <span>ThinkEsports</span>
      </router-link>

      <nav class="nav-links" :class="{ open: menuOpen }">
        <router-link to="/tournaments" @click="menuOpen = false">Tournaments</router-link>
        <router-link v-if="player.isLoggedIn" to="/dashboard" @click="menuOpen = false">Dashboard</router-link>
        <router-link v-if="player.isLoggedIn" to="/teams/create" @click="menuOpen = false">Create Team</router-link>

        <template v-if="player.isLoggedIn">
          <button class="btn btn-outline btn-sm" @click="handleLogout">Log out</button>
        </template>
        <router-link v-else to="/enter" class="btn btn-primary btn-sm" @click="menuOpen = false">
          Sign In
        </router-link>
      </nav>

      <button class="hamburger" @click="menuOpen = !menuOpen" aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { usePlayerStore } from "../store/player";
import { useToastStore } from "../store/toast";

const player = usePlayerStore();
const toast = useToastStore();
const router = useRouter();
const menuOpen = ref(false);

function handleLogout() {
  player.logout();
  toast.info("Signed out");
  router.push("/");
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(233, 240, 237, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 68px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-heading);
  font-weight: 800;
  font-size: 1.3rem;
  color: var(--color-text-heading);
}

.brand-mark {
  color: var(--color-primary);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-links a {
  color: var(--color-text-heading);
  font-weight: 500;
  font-size: 0.95rem;
}

.nav-links a.router-link-active {
  color: var(--color-primary);
}

.hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
}
.hamburger span {
  width: 22px;
  height: 2px;
  background: var(--color-text-heading);
  border-radius: 2px;
}

@media (max-width: 767px) {
  .hamburger {
    display: flex;
  }
  .nav-links {
    position: absolute;
    top: 68px;
    left: 0;
    right: 0;
    background: var(--color-card);
    flex-direction: column;
    align-items: stretch;
    padding: 16px 20px 24px;
    gap: 16px;
    box-shadow: var(--shadow-md);
    display: none;
  }
  .nav-links.open {
    display: flex;
  }
}
</style>
