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
    async checkPhone(phoneNumber) {
  const { data } = await client.get(`/players/check/${phoneNumber}`);
  return data;
},

async loginWithPin({ phoneNumber, pin }) {
  const { data } = await client.post("/auth/player/login", {
    phone_number: phoneNumber,
    pin,
  });
  this.token = data.token;
  this.player = data.player;
  localStorage.setItem("player_token", data.token);
  localStorage.setItem("player_data", JSON.stringify(data.player));
  return data;
},
async registerWithPin({ phoneNumber, playerName, pin }) {
  const { data } = await client.post("/auth/player/register", {
    phone_number: phoneNumber,
    player_name: playerName,
    pin,
  });
  this.token = data.token;
  this.player = data.player;
  localStorage.setItem("player_token", data.token);
  localStorage.setItem("player_data", JSON.stringify(data.player));
  return data;
},
async setPin({ phoneNumber, pin }) {
  const { data } = await client.post("/auth/player/set-pin", {
    phone_number: phoneNumber,
    pin,
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
