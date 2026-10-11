<template>
  <q-page class="q-pa-lg q-pb-xl page-content">
    <div class="row q-col-gutter-sm q-mb-md">
      <div class="col">
        <q-select
          v-model="monthFilter"
          filled
          dense
          label="Mes"
          :options="monthOptions"
          emit-value
          map-options
        />
      </div>
      <div class="col">
        <q-select
          v-model="categoryFilter"
          filled
          dense
          label="Categoría"
          :options="categoryOptions"
          option-value="id"
          option-label="name"
          emit-value
          map-options
          clearable
        />
      </div>
      <div class="col">
        <q-select
          v-model="walletFilter"
          filled
          dense
          label="Monedero"
          :options="walletOptions"
          option-value="id"
          option-label="name"
          emit-value
          map-options
          clearable
        />
      </div>
    </div>

    <q-toggle v-model="pendingOnly" label="Solo pendientes" color="amber-9" />

    <div class="text-caption text-grey-7 q-my-sm">
      Total: {{ fmtCents(total, currency) }}
    </div>

    <transaction-list :transactions="transactions.items" show-delete />
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useCatalogStore } from "@/stores/catalog";
import { useTransactionsStore } from "@/stores/transactions";
import { useAuthStore } from "@/stores/auth";
import { fmtCents } from "@/utils/money";
import transactionList from "@/components/TransactionList.vue";

const now = new Date();
const catalog = useCatalogStore();
const transactions = useTransactionsStore();
const auth = useAuthStore();
const { categories, wallets } = storeToRefs(catalog);

const currency = computed(() => auth.user?.currency || "MXN");

const monthFilter = ref(now.getFullYear() * 100 + (now.getMonth() + 1));
const categoryFilter = ref<string | null>(null);
const walletFilter = ref<string | null>(null);
const pendingOnly = ref(false);

const monthOptions = Array.from({ length: 12 }, (_, i) => {
  const year = now.getFullYear();
  const month = now.getMonth() + 1 - i;
  const label = (y: number, m: number) =>
    new Date(y, m - 1, 1).toLocaleDateString("es-MX", {
      month: "long",
      year: "numeric"
    });
  if (month >= 1) {
    return { value: year * 100 + month, label: label(year, month) };
  }
  return {
    value: (year - 1) * 100 + (month + 12),
    label: label(year - 1, month + 12)
  };
});

const categoryOptions = computed(() => categories.value.filter(c => !c.hidden));
const walletOptions = computed(() => wallets.value.filter(w => !w.hidden));

const total = computed(() =>
  transactions.items.reduce((sum: number, t) => sum + t.amount, 0)
);

function applyFilters(): void {
  const selected = monthFilter.value;
  const year = Math.floor(selected / 100);
  const month = selected % 100;
  void transactions.fetch({
    year,
    month,
    category_id: categoryFilter.value || undefined,
    wallet_id: walletFilter.value || undefined,
    pending: pendingOnly.value || undefined
  });
}

watch([monthFilter, categoryFilter, walletFilter, pendingOnly], applyFilters);

onMounted(() => {
  if (!catalog.loaded) {
    void catalog.load();
  }
  applyFilters();
});
</script>
