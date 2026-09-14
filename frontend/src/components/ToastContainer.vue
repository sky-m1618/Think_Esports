<template>
  <div class="toast-wrap">
    <transition-group name="toast">
      <div v-for="t in store.toasts" :key="t.id" class="toast" :class="`toast-${t.type}`">
        <span class="toast-icon">{{ icon(t.type) }}</span>
        <span class="toast-msg">{{ t.message }}</span>
        <button class="toast-close" @click="store.dismiss(t.id)" aria-label="Dismiss">&times;</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToastStore } from "../store/toast";
const store = useToastStore();

function icon(type) {
  return { success: "✓", error: "✕", warning: "!", info: "i" }[type] || "i";
}
</script>

<style scoped>
.toast-wrap {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 360px;
}

@media (max-width: 767px) {
  .toast-wrap {
    left: 16px;
    right: 16px;
    top: 16px;
    max-width: none;
  }
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 14px 16px;
  font-size: 0.9rem;
  color: var(--color-text-heading);
  border-left: 4px solid var(--color-info);
}

.toast-success {
  border-left-color: var(--color-success);
}
.toast-error {
  border-left-color: var(--color-danger);
}
.toast-warning {
  border-left-color: var(--color-warning);
}

.toast-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #eef2ff;
  color: var(--color-primary);
  font-weight: 700;
  font-size: 0.75rem;
  flex-shrink: 0;
}
.toast-success .toast-icon {
  background: #d1fae5;
  color: var(--color-success);
}
.toast-error .toast-icon {
  background: #fee2e2;
  color: var(--color-danger);
}
.toast-warning .toast-icon {
  background: #fef3c7;
  color: var(--color-warning);
}

.toast-msg {
  flex: 1;
}

.toast-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  color: var(--color-text-body);
  line-height: 1;
  padding: 0;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 220ms ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
