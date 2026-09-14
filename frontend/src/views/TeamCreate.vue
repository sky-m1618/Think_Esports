<template>
  <div class="container section">
    <div class="card create-card">
      <h2>Create Your Team</h2>
      <p>You'll be added automatically as team leader. Add up to 4 teammates.</p>

      <form @submit.prevent="submit">
        <div class="grid grid-2">
          <div class="field" :class="{ 'has-error': errors.team_name }">
            <label>Team Name</label>
            <input v-model="teamName" type="text" placeholder="Alpha Legends" maxlength="80" />
            <p v-if="errors.team_name" class="error-text">{{ errors.team_name }}</p>
          </div>
          <div class="field" :class="{ 'has-error': errors.team_tag }">
            <label>Team Tag (3-4 chars)</label>
            <input v-model="teamTag" type="text" placeholder="ALG" maxlength="4" style="text-transform: uppercase" />
            <p v-if="errors.team_tag" class="error-text">{{ errors.team_tag }}</p>
          </div>
        </div>

        <div class="field">
          <label>Team Logo (optional)</label>
          <div class="logo-upload">
            <div class="logo-preview" :class="{ empty: !logoPreview }">
              <img v-if="logoPreview" :src="logoPreview" alt="Team logo preview" />
              <span v-else>No logo</span>
            </div>
            <input type="file" accept="image/*" @change="onLogoChange" />
          </div>
        </div>

        <div class="field">
          <label>Leader</label>
          <div class="leader-row">
            <strong>{{ playerStore.player?.player_name }}</strong>
            <span class="tag-pill">{{ playerStore.player?.phone_number }}</span>
            <span class="badge badge-confirmed">Leader</span>
          </div>
        </div>

        <div class="teammates-section">
          <div class="flex-between">
            <label class="mb-0">Teammates ({{ members.length }}/4)</label>
            <button
              type="button"
              class="btn btn-sm btn-secondary"
              :disabled="members.length >= 4"
              @click="addMember"
            >
              + Add Teammate
            </button>
          </div>

          <div v-for="(m, i) in members" :key="m.key" class="teammate-row">
            <div class="field" :class="{ 'has-error': errors.members[i]?.player_name }">
              <label>Name</label>
              <input v-model="m.player_name" type="text" placeholder="Player name" maxlength="80" />
              <p v-if="errors.members[i]?.player_name" class="error-text">{{ errors.members[i].player_name }}</p>
            </div>
            <div class="field" :class="{ 'has-error': errors.members[i]?.phone_number }">
              <label>Phone Number</label>
              <input
                v-model="m.phone_number"
                type="tel"
                placeholder="9990000002"
                maxlength="15"
                @blur="checkDuplicate(i)"
              />
              <p v-if="errors.members[i]?.phone_number" class="error-text">{{ errors.members[i].phone_number }}</p>
              <p v-else-if="m.checked && m.isNewPlayer" class="hint">New player — will be registered automatically.</p>
              <p v-else-if="m.checked && !m.isNewPlayer" class="hint">Existing player: {{ m.existingName }}</p>
            </div>
            <button type="button" class="btn btn-sm btn-danger remove-btn" @click="removeMember(i)">Remove</button>
          </div>

          <EmptyState
            v-if="!members.length"
            emoji="👤"
            title="Solo squad"
            message="You can submit with just yourself, or add up to 4 teammates."
          />
        </div>

        <button class="btn btn-primary btn-block" style="margin-top: 24px" :disabled="submitting">
          <span v-if="submitting" class="spinner"></span>
          <span v-else>Create Team</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import client from "../api/client";
import { usePlayerStore } from "../store/player";
import { useToastStore } from "../store/toast";
import EmptyState from "../components/EmptyState.vue";

const playerStore = usePlayerStore();
const toast = useToastStore();
const router = useRouter();

const teamName = ref("");
const teamTag = ref("");
const logoFile = ref(null);
const logoPreview = ref(null);
const submitting = ref(false);
let keyCounter = 0;

const members = reactive([]);
const errors = reactive({ team_name: "", team_tag: "", members: [] });

function addMember() {
  if (members.length >= 4) return;
  members.push({
    key: keyCounter++,
    player_name: "",
    phone_number: "",
    checked: false,
    isNewPlayer: true,
    existingName: "",
  });
}

function removeMember(i) {
  members.splice(i, 1);
}

function onLogoChange(e) {
  const file = e.target.files[0];
  if (!file) return;
  logoFile.value = file;
  logoPreview.value = URL.createObjectURL(file);
}

async function checkDuplicate(i) {
  const m = members[i];
  if (!/^\d{10,15}$/.test(m.phone_number)) return;

  // Flag duplicates within this form first (cheap, no network needed)
  const dupe = members.filter((x, idx) => idx !== i && x.phone_number === m.phone_number).length > 0;
  if (dupe || m.phone_number === playerStore.player?.phone_number) {
    m.checked = false;
    return;
  }

  try {
    const { data } = await client.get(`/players/check/${m.phone_number}`);
    m.checked = true;
    m.isNewPlayer = !data.exists;
    m.existingName = data.player_name || "";
  } catch {
    // Non-fatal: server-side validation still runs on submit.
  }
}

function validate() {
  errors.team_name = "";
  errors.team_tag = "";
  errors.members = members.map(() => ({}));
  let ok = true;

  if (!teamName.value.trim()) {
    errors.team_name = "Team name is required";
    ok = false;
  }
  if (!/^[A-Za-z0-9]{3,4}$/.test(teamTag.value.trim())) {
    errors.team_tag = "Tag must be 3-4 alphanumeric characters";
    ok = false;
  }

  const seenPhones = new Set([playerStore.player?.phone_number]);
  members.forEach((m, i) => {
    if (!m.player_name.trim()) {
      errors.members[i].player_name = "Name is required";
      ok = false;
    }
    if (!/^\d{10,15}$/.test(m.phone_number)) {
      errors.members[i].phone_number = "Enter a valid phone number";
      ok = false;
    } else if (seenPhones.has(m.phone_number)) {
      errors.members[i].phone_number = "Duplicate phone number";
      ok = false;
    }
    seenPhones.add(m.phone_number);
  });

  return ok;
}

async function submit() {
  if (!validate()) {
    toast.error("Please fix the highlighted fields");
    return;
  }

  submitting.value = true;
  try {
    let logoUrl = null;
    if (logoFile.value) {
      const formData = new FormData();
      formData.append("file", logoFile.value);
      const { data } = await client.post("/uploads/team-logo", formData, {
        role: "player",
        headers: { "Content-Type": "multipart/form-data" },
      });
      logoUrl = data.logo_url;
    }

    const { data: team } = await client.post(
      "/teams/",
      {
        team_name: teamName.value.trim(),
        team_tag: teamTag.value.trim().toUpperCase(),
        logo_url: logoUrl,
        members: members.map((m) => ({ player_name: m.player_name.trim(), phone_number: m.phone_number.trim() })),
      },
      { role: "player" }
    );

    toast.success("Team created!");
    router.push(`/teams/${team.id}`);
  } catch (e) {
    const apiErrors = e.response?.data?.errors;
    if (apiErrors?.length) {
      apiErrors.forEach((msg) => toast.error(msg));
    } else {
      toast.error(e.friendlyMessage);
    }
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.create-card {
  max-width: 720px;
  margin: 0 auto;
}
.leader-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: var(--radius-md);
}
.tag-pill {
  background: #eef2ff;
  color: var(--color-primary-dark);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 600;
}
.teammates-section {
  margin-top: 24px;
  border-top: 1px solid var(--color-border);
  padding-top: 20px;
}
.teammate-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 12px;
  align-items: start;
  margin-top: 16px;
}
.remove-btn {
  margin-top: 28px;
}
@media (max-width: 640px) {
  .teammate-row {
    grid-template-columns: 1fr;
  }
  .remove-btn {
    margin-top: 0;
    width: 100%;
  }
}
.logo-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}
.logo-preview {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 0.7rem;
  color: var(--color-text-body);
}
.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
