import { defineStore } from "pinia";
import client from "../api/client";

export const useAdminStore = defineStore("admin", {
  state: () => ({
    token: localStorage.getItem("admin_token") || null,
    admin: JSON.parse(localStorage.getItem("admin_data") || "null"),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async login(username, password) {
      const { data } = await client.post("/auth/admin/login", { username, password });
      this.token = data.token;
      this.admin = data.admin;
      localStorage.setItem("admin_token", data.token);
      localStorage.setItem("admin_data", JSON.stringify(data.admin));
      return data;
    },

    logout() {
      this.token = null;
      this.admin = null;
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_data");
    },
  },
});
