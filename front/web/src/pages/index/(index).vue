<template>
  <q-page class="q-pa-lg q-pb-xl page-content">
    <q-card flat bordered class="q-pa-md q-mb-md">
      <div class="text-caption text-grey-7">Gasto de este mes</div>
      <div class="text-h4 text-weight-bold text-negative">
        {{ fmtCents(monthTotal, currency) }}
      </div>
      <div class="text-caption text-grey-7">
        {{ currentMonthLabel }}
      </div>
    </q-card>

    <q-card flat bordered class="q-pa-md q-mb-md">
      <div class="text-subtitle1 text-weight-medium q-mb-sm"> Monederos </div>
      <div v-if="catalog.balances.length === 0" class="text-grey-7 q-pb-md">
        Aún no tienes monederos. Crea uno en la sección Monederos.
      </div>
      <div
        v-for="balance in catalog.balances"
        :key="balance.id"
        class="row items-center justify-between q-py-xs"
      >
        <div>{{ balance.name }}</div>
        <div
          class="text-weight-medium"
          :class="balance.balance < 0 ? 'text-negative' : ''"
        >
          {{ fmtCents(balance.balance, currency) }}
        </div>
      </div>
    </q-card>

    <div v-if="transactions.items.length > 0" class="q-mt-lg">
      <div class="text-subtitle1 text-weight-medium q-mb-sm">
        Últimos movimientos
      </div>
      <TransactionList :transactions="transactions.items.slice(0, 10)" />
      <q-btn
        flat
        color="primary"
        label="Ver todos los movimientos"
        no-caps
        to="/transactions"
        class="q-mt-sm full-width"
      />
    </div>

    <!-- place QPageSticky at end of page -->
    <QuickAddForm @saved="onReload" />
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useCatalogStore } from "@/stores/catalog";
import { useTransactionsStore } from "@/stores/transactions";
import { useAuthStore } from "@/stores/auth";
import { fmtCents } from "@/utils/money";
import QuickAddForm from "@/components/QuickAddForm.vue";
import TransactionList from "@/components/TransactionList.vue";

const catalog = useCatalogStore();
const transactions = useTransactionsStore();
const auth = useAuthStore();

const now = new Date();
const currency = computed(() => auth.user?.currency || "MXN");
const currentMonthLabel = computed(() =>
  now.toLocaleDateString("es-MX", { month: "long", year: "numeric" })
);

const monthTotal = ref(0);

async function onReload(): Promise<void> {
  await transactions.fetch({
    year: now.getFullYear(),
    month: now.getMonth() + 1
  });
  monthTotal.value = transactions.items.reduce((sum, t) => sum + t.amount, 0);
}

onMounted(() => {
  if (!catalog.loaded) {
    void catalog.load().catch(() => {
      // silencioso: se reintentará al recargar
    });
  }
  onReload().catch(() => {
    // silencioso
  });
});
</script>
