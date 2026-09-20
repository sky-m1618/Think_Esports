<template>
  <div class="container entry-page">
    <div class="card entry-card">
      <h2>{{ step === "phone" ? "Sign in to Arena" : "Verify your number" }}</h2>
      <p v-if="step === 'phone'">Enter your phone number to sign in or create a player profile.</p>
      <p v-else>
        We sent a 6-digit code to <strong>{{ fullPhone }}</strong>
      </p>

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
        
        <div id="recaptcha-container" style="margin-bottom: 15px;"></div>

        <button class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Send OTP</span>
        </button>
      </form>

      <form v-else @submit.prevent="submitOtp">
        <div class="field" :class="{ 'has-error': errors.otp }">
          <label>OTP Code</label>
          <input v-model="otp" type="text" inputmode="numeric" maxlength="6" placeholder="123456" />
          <p v-if="errors.otp" class="error-text">{{ errors.otp }}</p>
        </div>

        <div v-if="needsName" class="field" :class="{ 'has-error': errors.name }">
          <label>Player Name</label>
          <input v-model="playerName" type="text" placeholder="Your in-game name" maxlength="80" />
          <p class="hint">First time here — pick the name teammates will see.</p>
          <p v-if="errors.name" class="error-text">{{ errors.name }}</p>
        </div>

        <button class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Verify &amp; Continue</span>
        </button>
        <button type="button" class="btn btn-outline btn-block" style="margin-top: 10px" @click="resetFlow">
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

// Firebase imports
import { auth } from "../firebase.js";
import { RecaptchaVerifier, signInWithPhoneNumber } from "firebase/auth";

const router = useRouter();
const route = useRoute();
const playerStore = usePlayerStore();
const toast = useToastStore();

const step = ref("phone");
const countryCode = ref("+91");
const phone = ref("");
const otp = ref("");
const playerName = ref("");
const loading = ref(false);
const needsName = ref(false);
const errors = ref({});

const fullPhone = computed(() => `${countryCode.value}${phone.value}`);
let confirmationResult = null;

function setupRecaptcha() {
  if (window.recaptchaVerifier) {
    window.recaptchaVerifier.clear();
  }
  window.recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
    'size': 'normal',
    'callback': () => {},
  });
}

async function submitPhone() {
  errors.value = {};
  if (!/^\d{7,15}$/.test(phone.value)) {
    errors.value.phone = "Enter a valid phone number";
    return;
  }
  loading.value = true;
  try {
    setupRecaptcha();
    confirmationResult = await signInWithPhoneNumber(auth, fullPhone.value, window.recaptchaVerifier);
    step.value = "otp";
    toast.success(`OTP sent to ${fullPhone.value}`);
  } catch (e) {
    console.error(e);
    toast.error(e.message || "Failed to send OTP. Try test number +91 9999999999 with code 123456");
    // Reset recaptcha if it fails
    if(window.recaptchaVerifier) window.recaptchaVerifier.render().then(wid => window.grecaptcha.reset(wid));
  } finally {
    loading.value = false;
  }
}

async function submitOtp() {
  errors.value = {};
  if (!/^\d{6}$/.test(otp.value)) {
    errors.value.otp = "Enter the 6-digit code";
    return;
  }
  loading.value = true;
  try {
    // 1. Verify with Firebase locally
    const result = await confirmationResult.confirm(otp.value);
    const idToken = await result.user.getIdToken();
    
    // 2. Now send Firebase token to YOUR Flask backend to create/login player
    // Your playerStore.verifyOtp should now accept idToken instead of otp
    await playerStore.verifyWithFirebase({ 
      idToken: idToken, 
      phoneNumber: fullPhone.value, 
      playerName: playerName.value 
    });

    toast.success(`Welcome, ${playerStore.player.player_name}!`);
    router.push(route.query.redirect || "/dashboard");
  } catch (e) {
    console.error(e);
    if (e.response?.status === 400 && /player_name/i.test(e.response?.data?.error || "")) {
      needsName.value = true;
    } else {
      toast.error(e.friendlyMessage || "Invalid OTP");
    }
  } finally {
    loading.value = false;
  }
}

function resetFlow(){
  step.value = 'phone';
  otp.value = '';
  if (window.recaptchaVerifier) {
    window.recaptchaVerifier.clear();
  }
}
</script>