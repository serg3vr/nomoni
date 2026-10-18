<template>
  <q-page class="q-pa-lg q-pb-xl page-content">
    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-sm-4">
        <stat-card
          icon="payments"
          label="Gasto del mes"
          :value="fmtCents(monthTotal, currency)"
          :caption="`${transactions.items.length} movimientos`"
        />
      </div>
      <div class="col-12 col-sm-4">
        <stat-card
          icon="savings"
          label="Saldo total"
          :value="fmtCents(totalBalance, currency)"
          caption="Suma de tus monederos"
        />
      </div>
      <div class="col-12 col-sm-4">
        <stat-card
          icon="account_balance_wallet"
          label="Sin clasificar"
          :value="fmtCents(pendingTotal, currency)"
          caption="Gastos del mes pendientes"
        />
      </div>
    </div>

    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-sm-7">
        <q-card flat bordered class="q-pa-md">
          <div class="row items-center justify-between q-mb-sm">
            <div class="text-subtitle1 text-weight-medium">
              Top categorías
            </div>
            <div class="text-caption text-grey-7">
              de {{ currentMonthLabel }}
            </div>
          </div>
          <div
            v-if="categoryBreakdown.length === 0"
            class="text-grey-7 q-py-md"
          >
            No hay gastos con categoría este mes.
          </div>
          <div v-for="item in categoryBreakdown" :key="item.id" class="q-mb-sm">
            <div class="row items-center justify-between q-mb-xs">
              <div class="row items-center q-gutter-xs">
                <q-avatar size="18px" :color="item.color" />
                <div class="text-body2">{{ item.name }}</div>
              </div>
              <div class="row items-center q-gutter-sm">
                <div class="text-weight-medium">
                  {{ fmtCents(item.total, currency) }}
                </div>
                <div class="text-caption text-grey-7 stat-chip">
                  {{ item.percent }}%
                </div>
              </div>
            </div>
            <q-linear-progress
              :value="item.percent / 100"
              :color="item.color"
              size="8px"
              rounded
              track-color="grey-2"
            />
          </div>
        </q-card>
      </div>

      <div class="col-12 col-sm-5">
        <q-card flat bordered class="q-pa-md">
          <div class="text-subtitle1 text-weight-medium q-mb-sm">
            Saldos por monedero
          </div>
          <div v-if="catalog.balances.length === 0" class="text-grey-7">
            Aún no tienes monederos. Crea uno en la sección Monederos.
          </div>
          <div
            v-for="balance in catalog.balances"
            :key="balance.id"
            class="row items-center justify-between q-py-sm"
          >
            <div>
              <div>{{ balance.name }}</div>
              <div class="text-caption text-grey-7">
                Gastado: {{ fmtCents(balance.spent, currency) }}
              </div>
            </div>
            <div
              class="text-weight-bold"
              :class="balance.balance < 0 ? 'text-negative' : ''"
            >
              {{ fmtCents(balance.balance, currency) }}
            </div>
          </div>
        </q-card>
      </div>
    </div>

    <q-card v-if="transactions.items.length > 0" flat bordered class="q-pa-md">
      <div class="text-subtitle1 text-weight-medium q-mb-sm">
        Últimos movimientos
      </div>
      <TransactionList :transactions="transactions.items.slice(0, 5)" />
      <q-btn
        flat
        color="primary"
        label="Ver todos los movimientos"
        no-caps
        to="/transactions"
        class="q-mt-sm"
      />
    </q-card>

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
import StatCard from "@/components/StatCard.vue";
import TransactionList from "@/components/TransactionList.vue";

const catalog = useCatalogStore();
const transactions = useTransactionsStore();
const auth = useAuthStore();

const now = new Date();
const currency = computed(() => auth.user?.currency || "MXN");
const currentMonthLabel = computed(() =>
  now.toLocaleDateString("es-MX", { month: "short", year: "numeric" })
);

const monthTotal = ref(0);
const pendingTotal = ref(0);

const totalBalance = computed(() =>
  catalog.balances.reduce((sum, b) => sum + b.balance, 0)
);

const categoryBreakdown = computed(() => {
  const byCategory = new Map<string, number>();
  for (const txn of transactions.items) {
    if (!txn.category_id) continue;
    byCategory.set(
      txn.category_id,
      (byCategory.get(txn.category_id) || 0) + txn.amount
    );
  }
  const entries = [...byCategory.entries()].sort((a, b) => b[1] - a[1]);
  const available = monthTotal.value;
  return entries.slice(0, 6).map(([id, total]) => {
    const category = catalog.categories.find(c => c.id === id);
    return {
      id,
      name: category?.name || "Sin nombre",
      color: category?.color || "primary",
      total,
      percent: monthTotal.value > 0 ? Math.round((total / available) * 100) : 0
    };
  });
});

async function onReload(): Promise<void> {
  await transactions.fetch({
    year: now.getFullYear(),
    month: now.getMonth() + 1
  });
  monthTotal.value = transactions.items.reduce((sum, t) => sum + t.amount, 0);
  pendingTotal.value = transactions.items
    .filter(t => !t.category_id)
    .reduce((sum, t) => sum + t.amount, 0);
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
