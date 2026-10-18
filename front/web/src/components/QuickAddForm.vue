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
        <q-form @submit="onSubmit" greedy>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6">
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
            </div>
            <div class="col-12 col-sm-6">
              <q-input v-model="note" filled label="Nota (opcional)" />
            </div>
            <div class="col-12 col-sm-6">
              <q-select
                v-model="occurredAt"
                filled
                stack-label
                label="Fecha (opcional)"
                :display-value="displayDate"
                clearable
              >
                <template v-slot:prepend>
                  <q-icon name="event" />
                </template>
                <q-popup-proxy
                  ref="dateRef"
                  transition-show="scale"
                  transition-hide="scale"
                >
                  <div class="col-12">
                    <q-date
                      v-model="occurredAt"
                      mask="YYYY-MM-DD"
                      today-btn
                      @update:model-value="() => dateRef?.hide()"
                    />
                  </div>
                </q-popup-proxy>
              </q-select>
            </div>
            <div class="col-12 col-sm-6">
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
            </div>
            <div class="col-12 col-sm-6">
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
            </div>
            <div class="col-12" align="right">
              <q-card-actions align="right">
                <q-btn flat label="Cancelar" no-caps v-close-popup />
                <q-btn
                  flat
                  color="primary"
                  label="Guardar"
                  type="submit"
                  no-caps
                  :loading="loading"
                />
              </q-card-actions>
            </div>
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import dayjs from "dayjs";
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
/** ISO date (YYYY-MM-DD) internally, or null for "today". */
const occurredAt = ref<string | null>(null);
const loading = ref(false);
const dateRef = ref<{ hide: () => void } | null>(null);

const categoryOptions = computed(() =>
  catalog.activeCategories.map(c => ({ id: c.id, name: c.name }))
);

const walletOptions = computed(() =>
  catalog.wallets.filter(w => !w.hidden).map(w => ({ id: w.id, name: w.name }))
);

const displayDate = computed((): string | undefined =>
  occurredAt.value ? dayjs(occurredAt.value).format("DD/MM/YYYY") : undefined
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
      occurred_at: occurredAt.value ?? new Date().toISOString().slice(0, 10)
    });
    amount.value = "";
    note.value = "";
    categoryId.value = null;
    walletId.value = null;
    occurredAt.value = null;
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
