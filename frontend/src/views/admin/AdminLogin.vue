<template>
  <div class="admin-login-page">
    <div class="card login-card">
      <div class="brand-mark">⬢</div>
      <h2>Admin Panel</h2>
      <p>Sign in to manage tournaments, matches and teams.</p>

      <form @submit.prevent="submit">
        <div class="field">
          <label>Username or Email</label>
          <input v-model="username" type="text" placeholder="admin" autocomplete="username" />
        </div>
        <div class="field">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="••••••••" autocomplete="current-password" />
        </div>
        <button class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Log In</span>
        </button>
      </form>
      <p class="hint text-center" style="margin-top: 16px">Demo: admin / admin123</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAdminStore } from "../../store/admin";
import { useToastStore } from "../../store/toast";

const username = ref("");
const password = ref("");
const loading = ref(false);
const adminStore = useAdminStore();
const toast = useToastStore();
const router = useRouter();

async function submit() {
  loading.value = true;
  try {
    await adminStore.login(username.value, password.value);
    toast.success("Welcome back!");
    router.push("/admin");
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef2ff, #f0fdfa);
  padding: 20px;
}
.login-card {
  max-width: 380px;
  width: 100%;
  text-align: center;
}
.brand-mark {
  font-size: 2rem;
  color: var(--color-primary);
  margin-bottom: 6px;
}
.login-card form {
  text-align: left;
  margin-top: 20px;
}
</style>
