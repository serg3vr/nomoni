<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-banner
        v-if="auth.isLoggedIn"
        dense
        rounded
        class="q-ma-md bg-light-blue-1 text-grey-9"
      >
        Ya tienes una sesión activa ({{ auth.user?.email }}).
        <q-btn
          flat
          dense
          color="primary"
          label="Cerrar sesión"
          no-caps
          @click="onLogout"
        />
      </q-banner>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();

onMounted(() => {
  if (auth.isLoggedIn && !auth.user) {
    void auth.fetchMe();
  }
});

function onLogout(): void {
  auth.logout();
  void router.push("/auth/register");
}
</script>
