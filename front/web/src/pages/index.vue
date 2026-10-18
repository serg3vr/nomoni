<template>
  <q-layout view="lHh Lpr lFf">
    <q-header class="app-header bg-dark text-white">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menú"
          @click="drawerOpen = !drawerOpen"
        />
        <q-toolbar-title>
          <span class="text-grey-6">Dashboard</span>
          <span class="q-px-sm text-grey-5">/</span>
          <span class="text-weight-bold">{{ title }}</span>
        </q-toolbar-title>
        <q-btn flat no-caps dense class="rounded-borders" @click.stop>
          <div class="row items-center q-gutter-xs">
            <q-avatar size="32px" color="primary" text-color="white">
              <span class="text-caption text-weight-bold">{{ initials }}</span>
            </q-avatar>
            <span v-if="$q.screen.gt.sm" class="text-weight-medium">
              {{ auth.user?.name || auth.user?.email }}
            </span>
            <q-icon name="expand_more" size="1.5em" />
          </div>

          <q-menu
            fit
            anchor="bottom end"
            transition-show="jump-down"
            transition-hide="jump-up"
          >
            <q-list padding style="min-width: 240px">
              <q-item>
                <q-item-section avatar>
                  <q-avatar size="40px" color="primary" text-color="white">
                    <span class="text-caption text-weight-bold">{{
                      initials
                    }}</span>
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-medium">
                    {{ auth.user?.name || "Usuario" }}
                  </q-item-label>
                  <q-item-label caption>{{ auth.user?.email }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-separator class="q-my-sm" />

              <q-item
                clickable
                v-ripple
                dense
                class="rounded-borders q-py-sm"
                @click="router.push('/profile')"
              >
                <q-item-section avatar>
                  <q-icon name="settings" color="grey-7" />
                </q-item-section>
                <q-item-section>Configuración</q-item-section>
              </q-item>

              <q-item
                clickable
                v-ripple
                dense
                class="rounded-borders q-py-sm"
                @click="onLogout"
              >
                <q-item-section avatar>
                  <q-icon name="logout" color="grey-7" />
                </q-item-section>
                <q-item-section>Cerrar sesión</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="drawerOpen"
      show-if-above
      bordered
      class="bg-white column"
    >
      <div class="q-pa-md row items-center q-gutter-sm">
        <q-avatar
          size="40px"
          color="primary"
          text-color="white"
          class="brand-avatar"
        >
          <q-icon name="account_balance_wallet" size="26px" />
        </q-avatar>
        <div class="text-h6 text-weight-bold">Nomoni</div>
      </div>

      <q-list class="q-px-sm">
        <q-item-label header class="text-grey-6 q-px-sm q-py-sm">
          Principal
        </q-item-label>
        <q-item
          v-for="item in tabs"
          :key="item.to"
          clickable
          v-ripple
          :active="route.path === item.to"
          active-class="bg-grey-2 text-grey-9 app-active-item"
          class="rounded-borders q-py-sm"
          @click="router.push(item.to)"
        >
          <q-item-section avatar>
            <q-icon
              :name="item.icon"
              :color="route.path === item.to ? 'primary' : 'grey-7'"
            />
          </q-item-section>
          <q-item-section>{{ item.label }}</q-item-section>
        </q-item>

        <q-separator class="q-my-md" />

        <q-item-label header class="text-grey-6 q-px-sm q-py-sm">
          Cuenta
        </q-item-label>
        <q-item
          clickable
          v-ripple
          :active="route.path === '/profile'"
          active-class="bg-grey-2 text-grey-9 app-active-item"
          class="rounded-borders q-py-sm"
          @click="router.push('/profile')"
        >
          <q-item-section avatar>
            <q-icon name="settings" color="grey-7" />
          </q-item-section>
          <q-item-section>Configuración</q-item-section>
        </q-item>
        <q-item
          clickable
          v-ripple
          class="rounded-borders q-py-sm"
          @click="onLogout"
        >
          <q-item-section avatar>
            <q-icon name="logout" color="grey-7" />
          </q-item-section>
          <q-item-section>Cerrar sesión</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer v-if="$q.screen.lt.md" class="bg-grey-1 border-top">
      <q-tabs
        v-model="mobileTab"
        no-caps
        align="justify"
        active-color="primary"
        indicator-color="transparent"
        class="text-grey-7"
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
const mobileTab = ref(route.path);

const tabs = [
  { to: "/", icon: "home", label: "Inicio" },
  { to: "/transactions", icon: "receipt_long", label: "Movimientos" },
  { to: "/categories", icon: "category", label: "Categorías" },
  { to: "/wallets", icon: "account_balance_wallet", label: "Monederos" }
];

const titles: Record<string, string> = {
  "/": "Inicio",
  "/transactions": "Movimientos",
  "/categories": "Categorías",
  "/wallets": "Monederos",
  "/profile": "Configuración"
};

const title = computed(() => titles[route.path] || "Nomoni");

const initials = computed(() => {
  const name = auth.user?.name || auth.user?.email || "?";
  return name.slice(0, 2).toUpperCase();
});

watch(
  () => route.path,
  value => {
    mobileTab.value = value;
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
