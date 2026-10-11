<template>
  <q-page class="flex flex-center q-pa-md">
    <q-card class="q-pa-lg" style="width: 100%; max-width: 380px">
      <q-card-section class="text-center">
        <div class="text-h4 text-weight-bold text-primary">Nomoni</div>
        <div class="text-subtitle2 text-grey-7"> Tus gastos, bajo control </div>
      </q-card-section>

      <q-card-section>
        <q-form class="q-gutter-md" @submit="onSubmit">
          <q-input
            v-model="email"
            filled
            label="Correo electrónico"
            type="email"
            lazy-rules
            :rules="[val => (val && val.length > 0) || 'Ingresa tu correo']"
          />
          <q-input
            v-model="password"
            filled
            label="Contraseña"
            :type="showPassword ? 'text' : 'password'"
            lazy-rules
            :rules="[val => (val && val.length > 0) || 'Ingresa tu contraseña']"
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
            label="Iniciar sesión"
            type="submit"
            no-caps
            :loading="loading"
          />
        </q-form>
      </q-card-section>

      <q-card-section class="text-center">
        <q-btn
          flat
          label="¿No tienes cuenta? Regístrate"
          color="primary"
          no-caps
          to="/auth/register"
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from "quasar";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const $q = useQuasar();
const router = useRouter();
const auth = useAuthStore();

const email = ref("");
const password = ref("");
const showPassword = ref(false);
const loading = ref(false);

async function onSubmit(): Promise<void> {
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    await router.push("/");
  } catch {
    $q.notify({
      type: "negative",
      message: "Correo o contraseña incorrectos"
    });
  } finally {
    loading.value = false;
  }
}
</script>
