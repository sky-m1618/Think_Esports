import { defineStore } from "pinia";
import client from "../api/client";

export const usePlayerStore = defineStore("player", {
  state: () => ({
    token: localStorage.getItem("player_token") || null,
    player: JSON.parse(localStorage.getItem("player_data") || "null"),
    teams: [],
    registrations: [],
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async requestOtp(phoneNumber) {
      const { data } = await client.post("/auth/player/request-otp", {
        phone_number: phoneNumber,
      });
      return data;
    },

    async verifyOtp({ phoneNumber, otp, playerName }) {
      const { data } = await client.post("/auth/player/verify-otp", {
        phone_number: phoneNumber,
        otp,
        player_name: playerName,
      });
      this.token = data.token;
      this.player = data.player;
      localStorage.setItem("player_token", data.token);
      localStorage.setItem("player_data", JSON.stringify(data.player));
      return data;
    },

    async fetchDashboard() {
      const { data } = await client.get("/players/me", { role: "player" });
      this.player = data.player;
      this.teams = data.teams;
      this.registrations = data.registrations;
      return data;
    },

    logout() {
      this.token = null;
      this.player = null;
      this.teams = [];
      this.registrations = [];
      localStorage.removeItem("player_token");
      localStorage.removeItem("player_data");
    },
  },
});
