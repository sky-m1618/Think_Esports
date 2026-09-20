<template>
  <div>
    <input v-model="phone" placeholder="+91 98765 43210" />
    <div id="recaptcha-container"></div>
    <button @click="sendOtp">Send OTP</button>

    <input v-model="otp" placeholder="Enter OTP" v-if="confirmationResult" />
    <button @click="verifyOtp" v-if="confirmationResult">Verify</button>
  </div>
</template>

<script>
import { auth } from '../firebase.js';
import { RecaptchaVerifier, signInWithPhoneNumber } from "firebase/auth";

export default {
  data(){ return { phone: "", otp: "", confirmationResult: null } },
  methods: {
    async sendOtp(){
      window.recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {});
      this.confirmationResult = await signInWithPhoneNumber(auth, this.phone, window.recaptchaVerifier);
      alert("OTP Sent");
    },
    async verifyOtp(){
      const result = await this.confirmationResult.confirm(this.otp);
      const idToken = await result.user.getIdToken();

      // Send this token to your Flask backend
      const res = await fetch("http://localhost:5000/api/auth/verify-firebase", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ idToken, phone: this.phone })
      });
      const data = await res.json();
      localStorage.setItem("token", data.token); // your JWT
    }
  }
}
</script>