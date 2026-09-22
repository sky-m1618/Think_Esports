<template>
  <div class="container entry-page">
    <div class="card entry-card">
      <h2>{{ heading }}</h2>
      <p v-if="step === 'phone'">Enter your phone number to sign in or create a player profile.</p>
      <p v-else-if="step === 'login'">
        Enter your 4-digit PIN for <strong>{{ phone }}</strong>.
      </p>
      <p v-else-if="step === 'register'">
        First time here — set a 4-digit PIN for <strong>{{ phone }}</strong>.
      </p>

      <!-- Step 1: phone number -->
      <form v-if="step === 'phone'" @submit.prevent="submitPhone">
        <div class="field" :class="{ 'has-error': errors.phone }">
          <label>Phone Number</label>
          <div class="phone-row">
            <select v-model="countryCode">
              <option value="+91">🇮🇳 +91</option>
              <option value="+1">🇺🇸 +1</option>
              <option value="+44">🇬🇧 +44</option>
              <option value="+61">🇦🇺 +61</option>
              <option value="+971">🇦🇪 +971</option>
            </select>
            <input v-model="phone" type="tel" placeholder="9990000001" maxlength="15" />
          </div>
          <p v-if="errors.phone" class="error-text">{{ errors.phone }}</p>
        </div>
        <button class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Continue</span>
        </button>
      </form>

      <!-- Step 2a: existing player — login with PIN -->
      <form v-else-if="step === 'login'" @submit.prevent="submitLogin">
        <div class="field" :class="{ 'has-error': errors.pin }">
          <label>PIN</label>
          <PinBoxes v-model="pin" ref="pinBoxesRef" />
          <p v-if="errors.pin" class="error-text">{{ errors.pin }}</p>
        </div>

        <button class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Sign In</span>
        </button>
        <button type="button" class="btn btn-outline btn-block" style="margin-top: 10px" @click="resetToPhone">
          Change number
        </button>
      </form>

      <!-- Step 2b: new player — name + set PIN + confirm PIN -->
      <form v-else-if="step === 'register'" @submit.prevent="submitRegister">
        <div class="field" :class="{ 'has-error': errors.name }">
          <label>Player Name</label>
          <input v-model="playerName" type="text" placeholder="Your in-game name" maxlength="80" />
          <p class="hint">The name teammates will see.</p>
          <p v-if="errors.name" class="error-text">{{ errors.name }}</p>
        </div>

        <div class="field" :class="{ 'has-error': errors.pin }">
          <label>Create PIN</label>
          <PinBoxes v-model="pin" ref="pinBoxesRef" />
          <p v-if="errors.pin" class="error-text">{{ errors.pin }}</p>
        </div>

        <div class="field" :class="{ 'has-error': errors.confirmPin }">
          <label>Confirm PIN</label>
          <PinBoxes v-model="confirmPin" ref="confirmPinBoxesRef" />
          <p v-if="errors.confirmPin" class="error-text">{{ errors.confirmPin }}</p>
        </div>

        <button class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Create Account</span>
        </button>
        <button type="button" class="btn btn-outline btn-block" style="margin-top: 10px" @click="resetToPhone">
          Change number
        </button>
      </form>
      <!-- Step 2c: existing player, no PIN yet (e.g. added as a teammate) -->
<form v-else-if="step === 'setup'" @submit.prevent="submitSetup">
  <div class="field">
    <label>Player Name</label>
    <input :value="playerName" type="text" disabled />
    <p class="hint">You were added to a team with this number — set a PIN to sign in.</p>
  </div>

  <div class="field" :class="{ 'has-error': errors.pin }">
    <label>Create PIN</label>
    <PinBoxes v-model="pin" ref="pinBoxesRef" />
    <p v-if="errors.pin" class="error-text">{{ errors.pin }}</p>
  </div>

  <div class="field" :class="{ 'has-error': errors.confirmPin }">
    <label>Confirm PIN</label>
    <PinBoxes v-model="confirmPin" ref="confirmPinBoxesRef" />
    <p v-if="errors.confirmPin" class="error-text">{{ errors.confirmPin }}</p>
  </div>

  <button class="btn btn-primary btn-block" :disabled="loading">
    <span v-if="loading" class="spinner"></span>
    <span v-else>Set PIN &amp; Continue</span>
  </button>
  <button type="button" class="btn btn-outline btn-block" style="margin-top: 10px" @click="resetToPhone">
    Change number
  </button>
</form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { usePlayerStore } from "../store/player";
import { useToastStore } from "../store/toast";
import PinBoxes from "../components/PinBoxes.vue";

const router = useRouter();
const route = useRoute();
const playerStore = usePlayerStore();
const toast = useToastStore();

const step = ref("phone"); // "phone" | "login" | "register"
const countryCode = ref("+91");
const phone = ref("");
const playerName = ref("");
const pin = ref("");
const confirmPin = ref("");
const loading = ref(false);
const errors = ref({});

const pinBoxesRef = ref(null);
const confirmPinBoxesRef = ref(null);

const heading = computed(() => {
  if (step.value === "login") return "Enter your PIN";
  if (step.value === "register") return "Create your PIN";
  if (step.value === "setup") return "Set your PIN";
  return "Sign in to Arena";
});

function resetToPhone() {
  step.value = "phone";
  pin.value = "";
  confirmPin.value = "";
  errors.value = {};
}

async function submitPhone() {
  errors.value = {};
  if (!/^\d{10,15}$/.test(phone.value)) {
    errors.value.phone = "Enter a valid phone number (10-15 digits)";
    return;
  }
  loading.value = true;
  try {
    const { exists, pin_set, player_name } = await playerStore.checkPhone(phone.value);
    if (!exists) {
      step.value = "register";
    } else if (!pin_set) {
      playerName.value = player_name; // pre-fill, read-only in the template
      step.value = "setup";
    } else {
      step.value = "login";
    }
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}
async function submitSetup() {
  errors.value = {};
  let ok = true;
  if (!/^\d{4}$/.test(pin.value)) {
    errors.value.pin = "Enter a 4-digit PIN";
    ok = false;
  }
  if (!/^\d{4}$/.test(confirmPin.value)) {
    errors.value.confirmPin = "Confirm your 4-digit PIN";
    ok = false;
  } else if (ok && pin.value !== confirmPin.value) {
    errors.value.confirmPin = "PINs don't match";
    ok = false;
  }
  if (!ok) return;

  loading.value = true;
  try {
    await playerStore.setPin({ phoneNumber: phone.value, pin: pin.value });
    toast.success(`Welcome, ${playerStore.player.player_name}!`);
    router.push(route.query.redirect || "/dashboard");
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}

async function submitLogin() {
  errors.value = {};
  if (!/^\d{4}$/.test(pin.value)) {
    errors.value.pin = "Enter your 4-digit PIN";
    return;
  }
  loading.value = true;
  try {
    await playerStore.loginWithPin({ phoneNumber: phone.value, pin: pin.value });
    toast.success(`Welcome back, ${playerStore.player.player_name}!`);
    router.push(route.query.redirect || "/dashboard");
  } catch (e) {
    errors.value.pin = "Incorrect PIN";
    pin.value = "";
    pinBoxesRef.value?.focusFirst();
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}

async function submitRegister() {
  errors.value = {};
  let ok = true;

  if (!playerName.value.trim()) {
    errors.value.name = "Player name is required";
    ok = false;
  }
  if (!/^\d{4}$/.test(pin.value)) {
    errors.value.pin = "Enter a 4-digit PIN";
    ok = false;
  }
  if (!/^\d{4}$/.test(confirmPin.value)) {
    errors.value.confirmPin = "Confirm your 4-digit PIN";
    ok = false;
  } else if (ok && pin.value !== confirmPin.value) {
    errors.value.confirmPin = "PINs don't match";
    ok = false;
  }
  if (!ok) return;

  loading.value = true;
  try {
    await playerStore.registerWithPin({
      phoneNumber: phone.value,
      playerName: playerName.value.trim(),
      pin: pin.value,
    });
    toast.success(`Welcome, ${playerStore.player.player_name}!`);
    router.push(route.query.redirect || "/dashboard");
  } catch (e) {
    toast.error(e.friendlyMessage);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.entry-page {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}
.entry-card {
  max-width: 440px;
  width: 100%;
}
.phone-row {
  display: flex;
  gap: 10px;
}
.phone-row select {
  width: 110px;
  min-height: 44px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  padding: 0 8px;
}
.phone-row input {
  flex: 1;
}
</style>