<template>
  <div class="admin-shell">
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-brand">
        <span class="brand-mark">⬢</span> Admin
      </div>
      <nav>
        <router-link to="/admin" exact-active-class="active" :class="{ active: $route.name === 'admin-dashboard' }" @click="sidebarOpen = false">
          📊 Dashboard
        </router-link>
        <router-link to="/admin/tournaments" @click="sidebarOpen = false">🏆 Tournaments</router-link>
        <router-link to="/admin/matches" @click="sidebarOpen = false">🎮 Matches &amp; Results</router-link>
        <router-link to="/admin/teams" @click="sidebarOpen = false">🛡️ Teams</router-link>
        <router-link to="/admin/players" @click="sidebarOpen = false">👤 Players</router-link>
        <router-link to="/admin/registrations" @click="sidebarOpen = false">📝 Registrations</router-link>
      </nav>
      <button class="btn btn-outline btn-block" @click="logout">Log Out</button>
    </aside>

    <div class="admin-main">
      <header class="admin-topbar">
        <button class="hamburger" @click="sidebarOpen = !sidebarOpen" aria-label="Toggle menu">☰</button>
        <span>{{ adminStore.admin?.username }}</span>
      </header>
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAdminStore } from "../../store/admin";
import { useToastStore } from "../../store/toast";

const adminStore = useAdminStore();
const toast = useToastStore();
const router = useRouter();
const sidebarOpen = ref(false);

function logout() {
  adminStore.logout();
  toast.info("Signed out");
  router.push("/admin/login");
}
</script>

<style scoped>
.admin-shell {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 240px;
  background: var(--color-text-heading);
  color: white;
  display: flex;
  flex-direction: column;
  padding: 24px 18px;
  flex-shrink: 0;
}
.sidebar-brand {
  font-family: var(--font-heading);
  font-weight: 800;
  font-size: 1.2rem;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.brand-mark {
  color: var(--color-primary-light);
}
.sidebar nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.sidebar nav a {
  color: #cbd5e1;
  padding: 11px 14px;
  border-radius: var(--radius-md);
  font-size: 0.92rem;
  font-weight: 500;
  transition: background var(--transition), color var(--transition);
}
.sidebar nav a:hover,
.sidebar nav a.router-link-active,
.sidebar nav a.active {
  background: rgba(99, 102, 241, 0.25);
  color: white;
}
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.admin-topbar {
  display: none;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: white;
  border-bottom: 1px solid var(--color-border);
}
.admin-content {
  padding: 28px;
  flex: 1;
}
.hamburger {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
}

@media (max-width: 900px) {
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform var(--transition);
  }
  .sidebar.open {
    transform: translateX(0);
  }
  .admin-topbar {
    display: flex;
  }
  .admin-content {
    padding: 18px;
  }
}
</style>
