<template>
  <teleport to="body">
    <div v-if="modelValue" class="modal-backdrop" @click.self="close">
      <div class="modal-card" role="dialog" aria-modal="true">
        <h3>{{ title }}</h3>
        <p>{{ message }}</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="close">Cancel</button>
          <button class="btn btn-danger" @click="confirm">{{ confirmLabel }}</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean,
  title: { type: String, default: "Are you sure?" },
  message: { type: String, default: "This action cannot be undone." },
  confirmLabel: { type: String, default: "Delete" },
});
const emit = defineEmits(["update:modelValue", "confirm"]);

function close() {
  emit("update:modelValue", false);
}
function confirm() {
  emit("confirm");
  emit("update:modelValue", false);
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(30, 41, 59, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1500;
  padding: 20px;
}
.modal-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 28px;
  max-width: 420px;
  width: 100%;
  box-shadow: var(--shadow-lg);
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}
</style>
