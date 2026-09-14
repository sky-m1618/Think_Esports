<template>
  <div class="landing">
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="container hero-inner">
        <span class="eyebrow">Season 1 · Registrations Open</span>
        <h1>Compete. Squad up. <br />Own the chicken dinner.</h1>
        
        <div class="hero-actions">
          <router-link to="/tournaments" class="btn btn-accent">Browse Tournaments</router-link>
          <router-link to="/enter" class="btn btn-accent">Get Started</router-link>
        </div>
      </div>
    </section>

    <section class="section container">
      <div class="flex-between">
        <h2>Featured Tournaments</h2>
        <router-link to="/tournaments">View all &rarr;</router-link>
      </div>

      <div v-if="loadingTournaments" class="grid grid-3">
        <div v-for="i in 3" :key="i" class="card skeleton" style="height: 220px"></div>
      </div>
      <EmptyState
        v-else-if="!featured.length"
        emoji="🏆"
        title="Login to see tournament"
        message="Check back soon — new tournaments are added regularly."
      />
      <div v-else class="grid grid-3">
        <TournamentCard v-for="t in featured" :key="t.id" :t="t" />
      </div>
    </section>

    <section class="section container">
      <h2>Live &amp; Upcoming Matches</h2>
      <div v-if="loadingTournaments" class="ticker skeleton" style="height: 60px"></div>
      <div v-else-if="ongoing.length" class="ticker card">
        <div v-for="t in ongoing" :key="t.id" class="ticker-item">
          <span class="live-dot"></span>
          <span>{{ t.tournament_name }}</span>
          <router-link :to="`/leaderboard/${t.id}`" class="btn btn-sm btn-secondary">Leaderboard</router-link>
        </div>
      </div>
      <EmptyState v-else emoji="📡" title="No live matches right now" message="Live tournaments will appear here." />
    </section>

    <section class="section container">
  <h2>Featured Maps</h2>
  
  <div class="grid grid-4">
    <!-- Map 1: Erangel -->
    <div class="card card-hover map-card">
      <img src="/maps/erangle.jpg" alt="Erangel Map" class="map-image" />
      <div class="map-overlay">
        <div class="map-tag">BGMI</div>
        <div class="map-name">ERANGLE</div>
      </div>
    </div>

    <!-- Map 2: Bind -->
    <div class="card card-hover map-card">
      <img src="/maps/miramar.webp" alt="Bind Map" class="map-image" />
      <div class="map-overlay">
        <div class="map-tag">BGMI</div>
        <div class="map-name">MIRAMAR</div>
      </div>
    </div>

    <!-- Map 3: Mirage -->
    <div class="card card-hover map-card">
      <img src="/maps/sanhok.webp" alt="Mirage Map" class="map-image" />
      <div class="map-overlay">
        <div class="map-tag">BGMI</div>
        <div class="map-name">SANHOK</div>
      </div>
    </div>

    <!-- Map 4: World's Edge -->
    <div class="card card-hover map-card">
      <img src="/maps/vikendi.webp" alt="World's Edge Map" class="map-image" />
      <div class="map-overlay">
        <div class="map-tag">BGMI</div>
        <div class="map-name">VIKENDI</div>
      </div>
    </div>
  </div>
</section>


    <section class="section container cta-section">
      <div class="card cta-card">
        <h2>Ready to drop in?</h2>
        <p>Create your squad and register for an upcoming tournament in minutes.</p>
        <router-link to="/enter" class="btn btn-accent">Join Now</router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import client from "../api/client";
import TournamentCard from "../components/TournamentCard.vue";
import EmptyState from "../components/EmptyState.vue";

const tournaments = ref([]);
const teams = ref([]);
const loadingTournaments = ref(true);
const loadingTeams = ref(true);

const featured = computed(() => tournaments.value.slice(0, 3));
const ongoing = computed(() => tournaments.value.filter((t) => t.status === "ongoing"));
const topTeams = computed(() => teams.value.slice(0, 4));

onMounted(async () => {
  try {
    const { data } = await client.get("/tournaments/");
    tournaments.value = data;
  } finally {
    loadingTournaments.value = false;
  }
  try {
    const { data } = await client.get("/teams/");
    teams.value = data;
  } finally {
    loadingTeams.value = false;
  }
});
</script>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  padding: 100px 0 90px;
}
.hero-bg {
  position: absolute;
  inset: 0;
  z-index: -1;
  background: 
    radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.18), transparent 45%),
    radial-gradient(circle at 80% 30%, rgba(20, 184, 166, 0.18), transparent 45%),
    radial-gradient(circle at 50% 90%, rgba(251, 113, 133, 0.14), transparent 50%),
    url('https://wallpapercave.com/wp/wp5568541.jpg'); /* Add your direct image link here */

  /* Ensure the Pinterest image scales beautifully inside the div */
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
  

.hero-inner {
  max-width: 780px;
}

.hero-inner h1{
  color: white;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.6)
}
.eyebrow {
  display: inline-block;
  background: #e0e7ff;
  color: var(--color-primary-dark);
  padding: 6px 14px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 700;
  margin-bottom: 20px;
}
.hero h1 {
  font-size: clamp(2rem, 5vw, 3.4rem);
  font-weight: 800;
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.ticker {
  padding: 8px;
}
.ticker-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  font-weight: 600;
  color: var(--color-text-heading);
}
.map-card {
  position: relative;
  height: 180px; /* Matches your landing page structure precisely */
  padding: 0 !important; /* Removes default box model margins so image spans flush */
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.map-image {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Compresses image to box limits without stretching or squishing */
  display: block;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* Elegant visual zoom on hover */
.card-hover:hover .map-image {
  transform: scale(1.08);
}

.map-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  pointer-events: none; /* Allows click events to drop straight through to the card container */
}

.map-tag {
  font-size: 0.7rem;
  font-weight: 800;
  color: #42b883; /* Theme brand color accent */
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.map-name {
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
}

.live-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--color-danger);
  animation: pulse 1.4s ease infinite;
  flex-shrink: 0;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.35;
  }
}

.team-mini {
  text-align: center;
  color: inherit;
}
.team-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  margin: 0 auto 10px;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-secondary-light));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: var(--color-primary-dark);
}
.team-name {
  font-weight: 700;
  color: var(--color-text-heading);
}
.team-meta {
  font-size: 0.8rem;
  color: var(--color-text-body);
}

.cta-card {
  text-align: center;
  background: linear-gradient(135deg, #eef2ff, #f0fdfa);
  padding: 50px 24px;
}
</style>
