import { createRouter, createWebHistory } from "vue-router";
import { usePlayerStore } from "../store/player";
import { useAdminStore } from "../store/admin";

const routes = [
  { path: "/", name: "landing", component: () => import("../views/Landing.vue") },
  { path: "/enter", name: "player-entry", component: () => import("../views/PlayerEntry.vue") },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("../views/PlayerDashboard.vue"),
    meta: { requiresPlayer: true },
  },
  {
    path: "/teams/create",
    name: "team-create",
    component: () => import("../views/TeamCreate.vue"),
    meta: { requiresPlayer: true },
  },
  { path: "/teams/:id", name: "team-detail", component: () => import("../views/TeamDetail.vue") },
  { path: "/tournaments", name: "tournaments", component: () => import("../views/Tournaments.vue") },
  {
    path: "/tournaments/:id",
    name: "tournament-detail",
    component: () => import("../views/TournamentDetail.vue"),
  },
  {
    path: "/leaderboard/:tournamentId",
    name: "leaderboard",
    component: () => import("../views/Leaderboard.vue"),
  },
  { path: "/admin/login", name: "admin-login", component: () => import("../views/admin/AdminLogin.vue") },
  {
    path: "/admin",
    component: () => import("../views/admin/AdminLayout.vue"),
    meta: { requiresAdmin: true },
    children: [
      { path: "", name: "admin-dashboard", component: () => import("../views/admin/AdminDashboard.vue") },
      { path: "tournaments", name: "admin-tournaments", component: () => import("../views/admin/AdminTournaments.vue") },
      { path: "matches", name: "admin-matches", component: () => import("../views/admin/AdminMatches.vue") },
      { path: "teams", name: "admin-teams", component: () => import("../views/admin/AdminTeams.vue") },
      { path: "players", name: "admin-players", component: () => import("../views/admin/AdminPlayers.vue") },
      { path: "registrations", name: "admin-registrations", component: () => import("../views/admin/AdminRegistrations.vue") },
    ],
  },
  { path: "/:pathMatch(.*)*", name: "not-found", component: () => import("../views/NotFound.vue") },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  if (to.meta.requiresPlayer) {
    const playerStore = usePlayerStore();
    if (!playerStore.isLoggedIn) {
      return { name: "player-entry", query: { redirect: to.fullPath } };
    }
  }
  if (to.meta.requiresAdmin) {
    const adminStore = useAdminStore();
    if (!adminStore.isLoggedIn) {
      return { name: "admin-login" };
    }
  }
  return true;
});

export default router;
