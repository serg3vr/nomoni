<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title class="text-weight-bold">
          {{ titles[route.path] || "Nomoni" }}
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer bordered class="bg-white text-grey-8">
      <q-tabs
        v-model="activeTab"
        no-caps
        align="justify"
        active-color="primary"
        indicator-color="transparent"
        class="shadow-up"
      >
        <q-tab
          v-for="tab in tabs"
          :key="tab.to"
          :name="tab.to"
          :icon="tab.icon"
          :label="tab.label"
          @click="router.push(tab.to)"
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from "quasar";
import { computed, onMounted, watch, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const $q = useQuasar();
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const tabs = [
  { to: "/", icon: "home", label: "Inicio" },
  { to: "/transactions", icon: "receipt_long", label: "Movimientos" },
  { to: "/categories", icon: "category", label: "Categorías" },
  { to: "/wallets", icon: "account_balance_wallet", label: "Monederos" },
  { to: "/profile", icon: "person", label: "Perfil" }
];

const titles: Record<string, string> = {
  "/": "Inicio",
  "/transactions": "Movimientos",
  "/categories": "Categorías",
  "/wallets": "Monederos",
  "/profile": "Perfil"
};

const activeTab = computed<string>(() => route.path);

if (auth.isLoggedIn && !auth.user) {
  onMounted(() => {
    auth.fetchMe().catch(() => {
      auth.logout();
      router.push("/auth/login");
    });
  });
}

watch(
  () => auth.token,
  value => {
    if (!value) {
      $q.notify({ message: "Sesión cerrada", type: "info" });
      router.push("/auth/login");
    }
  }
);
</script>
