<template>
  <q-btn
    v-if="$q.screen.gt.sm"
    color="primary"
    icon="add"
    label="Registrar gasto"
    no-caps
    class="q-mt-lg"
    @click="dialog = true"
  />

  <q-page-sticky v-else position="bottom-right" :offset="[20, 20]">
    <q-btn
      round
      size="lg"
      color="primary"
      icon="add"
      aria-label="Registrar gasto"
      @click="dialog = true"
    />
  </q-page-sticky>

  <q-dialog v-model="dialog" persistent>
    <q-card style="min-width: 340px">
      <q-card-section class="text-h6">Registrar gasto</q-card-section>
      <q-card-section>
        <q-form class="q-gutter-md" @submit="onSubmit">
          <q-input
            v-model="amount"
            filled
            label="Monto (ej. 25.50)"
            inputmode="decimal"
            lazy-rules
            :rules="[
              val => (val && val.length > 0) || 'Ingresa el monto',
              val => !Number.isNaN(Number(val)) || 'Monto inválido',
              val => Number(val) > 0 || 'El monto debe ser mayor a 0'
            ]"
          />
          <q-input v-model="note" filled label="Nota (opcional)" />
          <q-select
            v-model="categoryId"
            filled
            label="Categoría"
            :options="categoryOptions"
            option-value="id"
            option-label="name"
            emit-value
            map-options
            clearable
          />
          <q-select
            v-model="walletId"
            filled
            label="Monedero"
            :options="walletOptions"
            option-value="id"
            option-label="name"
            emit-value
            map-options
            clearable
          />
        </q-form>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Cancelar" no-caps v-close-popup />
        <q-btn
          flat
          color="primary"
          label="Guardar"
          type="submit"
          no-caps
          :loading="loading"
          @click="onSubmit"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useQuasar } from "quasar";
import { computed, ref } from "vue";
import { useCatalogStore } from "@/stores/catalog";
import { useTransactionsStore } from "@/stores/transactions";
import { parseAmountToCents } from "@/utils/money";

const $q = useQuasar();
const catalog = useCatalogStore();
const transactions = useTransactionsStore();

const emit = defineEmits<{ saved: [] }>();

const dialog = ref(false);
const amount = ref("");
const note = ref("");
const categoryId = ref<string | null>(null);
const walletId = ref<string | null>(null);
const loading = ref(false);

const categoryOptions = computed(() =>
  catalog.activeCategories.map(c => ({ id: c.id, name: c.name }))
);

const walletOptions = computed(() =>
  catalog.wallets.filter(w => !w.hidden).map(w => ({ id: w.id, name: w.name }))
);

async function onSubmit(): Promise<void> {
  try {
    const cents = parseAmountToCents(amount.value);
    loading.value = true;
    await transactions.create({
      amount: cents,
      note: note.value || null,
      category_id: categoryId.value ?? null,
      wallet_id: walletId.value ?? null,
      occurred_at: new Date().toISOString().slice(0, 10)
    });
    amount.value = "";
    note.value = "";
    categoryId.value = null;
    walletId.value = null;
    dialog.value = false;
    $q.notify({ type: "positive", message: "Gasto registrado" });
    emit("saved");
  } catch (err) {
    $q.notify({
      type: "negative",
      message:
        err instanceof Error && err.message
          ? err.message
          : "No se pudo registrar el gasto"
    });
  } finally {
    loading.value = false;
  }
}
</script>
