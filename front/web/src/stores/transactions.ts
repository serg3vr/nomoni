import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/boot/axios";
import type { Transaction, TransactionFilters } from "@/types/api";
import { useCatalogStore } from "@/stores/catalog";

export const useTransactionsStore = defineStore("transactions", () => {
  const items = ref<Transaction[]>([]);
  const loading = ref(false);

  async function fetch(filters: TransactionFilters = {}): Promise<void> {
    loading.value = true;
    try {
      const { data } = await api.get<Transaction[]>("/transactions", {
        params: filters
      });
      items.value = data;
    } finally {
      loading.value = false;
    }
  }

  async function create(payload: {
    amount: number;
    note?: string | null;
    category_id?: string | null;
    wallet_id?: string | null;
    occurred_at?: string | null;
  }): Promise<void> {
    await api.post<Transaction>("/transactions", payload);
    await fetch();
    await useCatalogStore().reloadBalances();
  }

  async function update(
    id: string,
    payload: {
      amount?: number;
      note?: string | null;
      category_id?: string | null;
      wallet_id?: string | null;
      occurred_at?: string;
    }
  ): Promise<void> {
    await api.patch<Transaction>(`/transactions/${id}`, payload);
    await fetch();
    await useCatalogStore().reloadBalances();
  }

  async function remove(id: string): Promise<void> {
    await api.delete(`/transactions/${id}`);
    items.value = items.value.filter(t => t.id !== id);
    await useCatalogStore().reloadBalances();
  }

  return { items, loading, fetch, create, update, remove };
});
