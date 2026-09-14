import axios from "axios";

const isLocal = import.meta.env.DEV; 

const client = axios.create({
  baseURL: isLocal ? '/api' : 'https://thinkesports.onrender.com/',
  headers: { "Content-Type": "application/json" },
});

/**
 * Admin and player sessions are independent JWTs stored under separate keys,
 * so a browser can hold both at once. Pass `{ role: 'admin' }` in a request's
 * config to force which token is attached; otherwise the client prefers the
 * player token (the common case for public-facing pages) and falls back to
 * whichever token exists.
 */
client.interceptors.request.use((config) => {
  const adminToken = localStorage.getItem("admin_token");
  const playerToken = localStorage.getItem("player_token");
  const role = config.role;

  let token;
  if (role === "admin") token = adminToken;
  else if (role === "player") token = playerToken;
  else token = playerToken || adminToken;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      error.friendlyMessage = error.response.data?.error || (error.response.data?.errors || [])[0] || "Something went wrong.";
    } else {
      error.friendlyMessage = "Network error. Please check your connection.";
    }
    return Promise.reject(error);
  }
);

export default client;
