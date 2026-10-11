<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn
          v-if="$q.screen.lt.md"
          flat
          dense
          round
          icon="menu"
          aria-label="Menú"
          @click="drawerOpen = !drawerOpen"
        />
        <q-toolbar-title class="text-weight-bold">
          {{ title }}
        </q-toolbar-title>
        <div v-if="$q.screen.gt.sm" class="text-caption q-pr-sm">
          {{ auth.user?.name || auth.user?.email }}
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="drawerOpen"
      show-if-above
      :width="240"
      bordered
      class="bg-grey-1 column"
    >
      <div class="q-pa-lg text-center q-mt-md">
        <div class="text-h5 text-weight-bold text-primary">Nomoni</div>
        <div class="text-caption text-grey-7"> Tus gastos, bajo control </div>
      </div>

      <q-list padding>
        <q-item
          v-for="item in tabs"
          :key="item.to"
          clickable
          v-ripple
          :active="route.path === item.to"
          active-class="bg-primary text-white"
          @click="router.push(item.to)"
        >
          <q-item-section avatar>
            <q-icon :name="item.icon" />
          </q-item-section>
          <q-item-section>{{ item.label }}</q-item-section>
        </q-item>
      </q-list>

      <q-space />

      <q-list padding>
        <q-separator />
        <q-item clickable v-ripple @click="onLogout">
          <q-item-section avatar>
            <q-icon name="logout" color="negative" />
          </q-item-section>
          <q-item-section class="text-negative">Cerrar sesión</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer v-if="$q.screen.lt.md" bordered class="bg-white text-grey-8">
      <q-tabs
        no-caps
        align="justify"
        active-color="primary"
        indicator-color="transparent"
      >
        <q-tab
          v-for="item in tabs"
          :key="item.to"
          :name="item.to"
          :icon="item.icon"
          :label="item.label"
          @click="router.push(item.to)"
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from "quasar";
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const $q = useQuasar();
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const drawerOpen = ref(false);

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

const title = computed(() => titles[route.path] || "Nomoni");

watch(
  () => route.path,
  () => {
    if ($q.screen.lt.md) {
      drawerOpen.value = false;
    }
  }
);

if (auth.isLoggedIn && !auth.user) {
  onMounted(() => {
    auth.fetchMe().catch(() => {
      auth.logout();
      router.push("/auth/login");
    });
  });
}

function onLogout(): void {
  auth.logout();
  router.push("/auth/login");
}
</script>
