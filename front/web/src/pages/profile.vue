<template>
  <MainLayout>
    <q-page class="q-pa-lg q-pb-xl page-content">
      <q-card flat bordered class="q-pa-md q-mb-md">
        <div class="row items-center q-gutter-md">
          <q-avatar size="64px" color="primary" text-color="white">
            <span class="text-h5 text-weight-bold">{{ initials }}</span>
          </q-avatar>
          <div>
            <div class="text-h6">{{ auth.user?.name || "Usuario" }}</div>
            <div class="text-caption text-grey-7">{{ auth.user?.email }}</div>
          </div>
        </div>
      </q-card>

      <q-card flat bordered class="q-pa-md q-mb-md">
        <div class="text-subtitle1 text-weight-medium q-mb-sm">Perfil</div>
        <q-form class="q-gutter-md" @submit="onSave">
          <q-input v-model="form.name" filled label="Nombre" />
          <q-select
            v-model="form.currency"
            filled
            label="Moneda"
            :options="currencies"
          />
          <q-btn
            color="primary"
            label="Guardar cambios"
            type="submit"
            no-caps
            :loading="saving"
          />
        </q-form>
      </q-card>

      <q-btn
        flat
        color="negative"
        icon="logout"
        label="Cerrar sesión"
        no-caps
        class="full-width"
        @click="onLogout"
      />
    </q-page>
  </MainLayout>
</template>

<script setup lang="ts">
import MainLayout from "@/layouts/MainLayout.vue";
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();

const currencies = ["MXN", "USD", "EUR"];
const form = ref({ name: "", currency: "MXN" });
const saving = ref(false);

const initials = computed(() => {
  const name = auth.user?.name || auth.user?.email || "?";
  return name.slice(0, 2).toUpperCase();
});

onMounted(() => {
  if (auth.user) {
    form.value.name = auth.user.name || "";
    form.value.currency = auth.user.currency;
  }
});

async function onSave(): Promise<void> {
  saving.value = true;
  try {
    const needsFetch = !auth.user;
    await auth.updateProfile({
      name: form.value.name || null,
      currency: form.value.currency
    });
    if (needsFetch) await auth.fetchMe();
  } finally {
    saving.value = false;
  }
}

function onLogout(): void {
  auth.logout();
  void router.push("/auth/login");
}
</script>
