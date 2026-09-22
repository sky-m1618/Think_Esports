<template>
  <div class="pin-boxes" @paste="onPaste">
    <input
      v-for="(digit, i) in digits"
      :key="i"
      ref="inputRefs"
      v-model="digits[i]"
      type="password"
      inputmode="numeric"
      maxlength="1"
      class="pin-box"
      @input="onInput(i, $event)"
      @keydown="onKeydown(i, $event)"
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from "vue";

const props = defineProps({ modelValue: { type: String, default: "" } });
const emit = defineEmits(["update:modelValue"]);

const digits = ref(["", "", "", ""]);
const inputRefs = ref([]);

watch(
  () => props.modelValue,
  (val) => {
    const chars = (val || "").split("").slice(0, 4);
    digits.value = [chars[0] || "", chars[1] || "", chars[2] || "", chars[3] || ""];
  },
  { immediate: true }
);

function emitValue() {
  emit("update:modelValue", digits.value.join(""));
}

function onInput(i, e) {
  const val = e.target.value.replace(/\D/g, "").slice(-1);
  digits.value[i] = val;
  emitValue();
  if (val && i < 3) {
    nextTick(() => inputRefs.value[i + 1]?.focus());
  }
}

function onKeydown(i, e) {
  if (e.key === "Backspace" && !digits.value[i] && i > 0) {
    nextTick(() => inputRefs.value[i - 1]?.focus());
  }
}

function onPaste(e) {
  const text = (e.clipboardData?.getData("text") || "").replace(/\D/g, "").slice(0, 4);
  if (!text) return;
  e.preventDefault();
  const chars = text.split("");
  digits.value = [chars[0] || "", chars[1] || "", chars[2] || "", chars[3] || ""];
  emitValue();
  nextTick(() => inputRefs.value[Math.min(text.length, 3)]?.focus());
}

function focusFirst() {
  nextTick(() => inputRefs.value[0]?.focus());
}

defineExpose({ focusFirst });
</script>

<style scoped>
.pin-boxes {
  display: flex;
  gap: 12px;
}
.pin-box {
  width: 52px;
  height: 56px;
  text-align: center;
  font-size: 1.4rem;
  font-weight: 700;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  background: #fff;
  color: var(--color-text-heading);
  transition: border-color var(--transition), box-shadow var(--transition);
}
.pin-box:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}
</style>