<template>
  <q-card flat bordered>
    <q-list separator>
      <div v-if="transactions.length === 0" class="q-pa-md text-grey-7">
        Sin movimientos.
      </div>
      <q-item v-for="txn in transactions" :key="txn.id" class="q-py-sm">
        <q-item-section avatar>
          <q-avatar
            :color="categoryColor(txn.category_id)"
            text-color="white"
            icon="payments"
          />
        </q-item-section>
        <q-item-section>
          <q-item-label>
            {{ categoryLabel(txn) }}
          </q-item-label>
          <q-item-label caption>
            {{ dateLabel(txn) }}
            <span v-if="!txn.category_id"> · Pendiente de clasificar</span>
            <span v-if="walletLabel(txn)"> · {{ walletLabel(txn) }}</span>
          </q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-item-label class="text-negative text-weight-medium">
            -{{ fmtCents(txn.amount, currency) }}
          </q-item-label>
        </q-item-section>
        <q-item-section v-if="showDelete" side>
          <q-btn
            flat
            round
            dense
            color="grey-7"
            icon="delete"
            :loading="deletingId === txn.id"
            @click="onDelete(txn.id)"
          />
        </q-item-section>
      </q-item>
    </q-list>
  </q-card>
</template>

<script setup lang="ts">
import { useQuasar } from "quasar";
import { computed, ref } from "vue";
import { storeToRefs } from "pinia";
import { useTransactionsStore } from "@/stores/transactions";
import { useCatalogStore } from "@/stores/catalog";
import { useAuthStore } from "@/stores/auth";
import type { Category, Transaction } from "@/types/api";
import { fmtCents } from "@/utils/money";

defineProps<{
  transactions: Transaction[];
  showDelete?: boolean;
}>();

const $q = useQuasar();
const catalogStore = useCatalogStore();
const transactionsStore = useTransactionsStore();
const auth = useAuthStore();
const { categories, wallets } = storeToRefs(catalogStore);

const currency = computed(() => auth.user?.currency || "MXN");
const deletingId = ref<string | null>(null);

function categoryLabel(txn: Transaction): string {
  if (!txn.category_id) return txn.note || "Gasto";
  const category = categories.value.find(c => c.id === txn.category_id);
  return category?.name || txn.note || "Gasto";
}

function walletLabel(txn: Transaction): string {
  if (!txn.wallet_id) return "";
  return wallets.value.find(w => w.id === txn.wallet_id)?.name || "";
}

function categoryColor(categoryId: string | null): string {
  const category = categories.value.find(c => c.id === categoryId);
  if (category?.color) return category.color;
  if (!categoryId) return "orange-8";
  return "primary";
}

function dateLabel(txn: Transaction): string {
  return txn.occurred_at.split("-").reverse().join("/");
}

async function onDelete(id: string): Promise<void> {
  deletingId.value = id;
  try {
    await transactionsStore.remove(id);
    $q.notify({ message: "Movimiento eliminado", type: "info" });
  } catch {
    $q.notify({ message: "No se pudo eliminar", type: "negative" });
  } finally {
    deletingId.value = null;
  }
}
</script>
