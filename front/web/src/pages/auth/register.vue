<template>
  <q-page class="flex flex-center q-pa-md">
    <q-card class="q-pa-lg" style="width: 100%; max-width: 380px">
      <q-card-section class="text-center">
        <div class="text-h4 text-weight-bold text-primary">Nomoni</div>
        <div class="text-subtitle2 text-grey-7">Crea tu cuenta</div>
      </q-card-section>

      <q-card-section>
        <q-form class="q-gutter-md" @submit="onSubmit">
          <q-input v-model="name" filled label="Nombre (opcional)" />
          <q-input
            v-model="email"
            filled
            label="Correo electrónico"
            type="email"
            lazy-rules
            :rules="[
              val => (val && val.length > 0) || 'Ingresa tu correo',
              val => /.+@.+\..+/.test(val) || 'Correo inválido'
            ]"
          />
          <q-input
            v-model="password"
            filled
            label="Contraseña"
            :type="showPassword ? 'text' : 'password'"
            lazy-rules
            :rules="[val => (val && val.length >= 8) || 'Mínimo 8 caracteres']"
          >
            <template #append>
              <q-icon
                :name="showPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>

          <q-btn
            class="full-width"
            color="primary"
            label="Crear cuenta"
            type="submit"
            no-caps
            :loading="loading"
          />
        </q-form>
      </q-card-section>

      <q-card-section class="text-center">
        <q-btn
          flat
          label="¿Ya tienes cuenta? Inicia sesión"
          color="primary"
          no-caps
          to="/auth/login"
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from "quasar";
import axios from "axios";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const $q = useQuasar();
const router = useRouter();
const auth = useAuthStore();

const name = ref("");
const email = ref("");
const password = ref("");
const showPassword = ref(false);
const loading = ref(false);

async function onSubmit(): Promise<void> {
  loading.value = true;
  try {
    await auth.register({
      email: email.value,
      password: password.value,
      name: name.value || undefined
    });
    await router.push("/");
  } catch (err) {
    console.error("[register]", err);
    const axiosError = axios.isAxiosError(err) ? err : undefined;
    const detail = axiosError
      ? axiosError.response
        ? `HTTP ${axiosError.response.status}: ${JSON.stringify(axiosError.response.data)}`
        : `Error de red: ${axiosError.message}`
      : err instanceof Error
        ? err.message
        : String(err);
    $q.notify({
      type: "negative",
      message: `No se pudo crear la cuenta (${detail})`,
      multiLine: true,
      timeout: 8000
    });
  } finally {
    loading.value = false;
  }
}
</script>
