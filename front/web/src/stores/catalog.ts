import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { api } from "@/boot/axios";
import type { Category, Wallet, WalletBalance } from "@/types/api";

export const useCatalogStore = defineStore("catalog", () => {
  const categories = ref<Category[]>([]);
  const wallets = ref<Wallet[]>([]);
  const balances = ref<WalletBalance[]>([]);
  const loaded = ref(false);

  const activeCategories = computed(() =>
    categories.value.filter(c => !c.hidden)
  );

  async function load(): Promise<void> {
    const [cats, walls, bals] = await Promise.all([
      api.get<Category[]>("/categories"),
      api.get<Wallet[]>("/wallets"),
      api.get<WalletBalance[]>("/wallets/balances")
    ]);
    categories.value = cats.data;
    wallets.value = walls.data;
    balances.value = bals.data;
    loaded.value = true;
  }

  async function reloadBalances(): Promise<void> {
    const { data } = await api.get<WalletBalance[]>("/wallets/balances");
    balances.value = data;
  }

  async function addCategory(payload: {
    name: string;
    color?: string;
  }): Promise<void> {
    const { data } = await api.post<Category>("/categories", {
      ...payload,
      type: "EXPENSE"
    });
    categories.value.push(data);
  }

  async function updateCategory(
    id: string,
    payload: { name?: string; hidden?: boolean }
  ): Promise<void> {
    const { data } = await api.patch<Category>(`/categories/${id}`, payload);
    const idx = categories.value.findIndex(c => c.id === id);
    if (idx >= 0) categories.value[idx] = data;
  }

  async function deleteCategory(id: string): Promise<void> {
    await api.delete(`/categories/${id}`);
    categories.value = categories.value.filter(c => c.id !== id);
    await reloadBalances();
  }

  async function addWallet(payload: {
    name: string;
    type: string;
    initial_balance: number;
  }): Promise<void> {
    const { data } = await api.post<Wallet>("/wallets", payload);
    wallets.value.push(data);
    await reloadBalances();
  }

  async function updateWallet(
    id: string,
    payload: { name?: string; hidden?: boolean; initial_balance?: number }
  ): Promise<void> {
    const { data } = await api.patch<Wallet>(`/wallets/${id}`, payload);
    const idx = wallets.value.findIndex(w => w.id === id);
    if (idx >= 0) wallets.value[idx] = data;
    await reloadBalances();
  }

  async function deleteWallet(id: string): Promise<void> {
    await api.delete(`/wallets/${id}`);
    wallets.value = wallets.value.filter(w => w.id !== id);
    balances.value = balances.value.filter(b => b.id !== id);
  }

  return {
    categories,
    wallets,
    balances,
    loaded,
    activeCategories,
    load,
    reloadBalances,
    addCategory,
    updateCategory,
    deleteCategory,
    addWallet,
    updateWallet,
    deleteWallet
  };
});
