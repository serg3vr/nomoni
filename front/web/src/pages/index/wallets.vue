<template>
  <q-page class="q-pa-md q-pb-xl page-content">
    <q-btn
      color="primary"
      icon="add"
      label="Nuevo monedero"
      no-caps
      class="q-mb-md"
      @click="dialog = true"
    />

    <div class="q-mb-md row q-col-gutter-sm">
      <div v-for="balance in catalog.balances" :key="balance.id" class="col-6">
        <q-card flat bordered class="q-pa-md">
          <div class="text-caption text-grey-7 ellipsis">
            {{ balance.name }}
          </div>
          <div
            class="text-h6 text-weight-bold"
            :class="balance.balance < 0 ? 'text-negative' : ''"
          >
            {{ fmtCents(balance.balance, currency) }}
          </div>
          <div class="text-caption text-grey-7">
            Gastado: {{ fmtCents(balance.spent, currency) }}
          </div>
        </q-card>
      </div>
    </div>

    <q-card flat bordered>
      <q-list separator>
        <div v-if="catalog.wallets.length === 0" class="q-pa-md text-grey-7">
          No tienes monederos.
        </div>
        <q-item v-for="wallet in catalog.wallets" :key="wallet.id">
          <q-item-section avatar>
            <q-avatar
              color="primary"
              text-color="white"
              :icon="walletIcon(wallet.type)"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ wallet.name }}</q-item-label>
            <q-item-label caption>
              {{ walletTypeLabel(wallet.type) }} · Inicial:
              {{ fmtCents(wallet.initial_balance, currency) }}
            </q-item-label>
          </q-item-section>
          <q-item-section v-if="!wallet.is_system" side>
            <q-btn
              flat
              round
              dense
              icon="delete"
              @click="onDelete(wallet.id)"
            />
          </q-item-section>
        </q-item>
      </q-list>
    </q-card>

    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 320px">
        <q-card-section class="text-h6">Nuevo monedero</q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input v-model="form.name" filled label="Nombre" autofocus />
          <q-select
            v-model="form.type"
            filled
            label="Tipo"
            :options="walletTypes"
            option-value="value"
            option-label="label"
            emit-value
            map-options
          />
          <q-input
            v-model="form.initialBalance"
            filled
            label="Saldo inicial (opcional)"
            inputmode="decimal"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" no-caps v-close-popup />
          <q-btn
            flat
            color="primary"
            label="Guardar"
            no-caps
            :loading="saving"
            @click="onSave"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from "quasar";
import { computed, ref } from "vue";
import { useCatalogStore } from "@/stores/catalog";
import { useAuthStore } from "@/stores/auth";
import { fmtCents, parseAmountToCents } from "@/utils/money";

const $q = useQuasar();
const catalog = useCatalogStore();
const auth = useAuthStore();

const currency = computed(() => auth.user?.currency || "MXN");

const walletTypes = [
  { value: "CASH", label: "Efectivo" },
  { value: "BANK", label: "Banco" },
  { value: "CREDIT_CARD", label: "Tarjeta de crédito" },
  { value: "DIGITAL", label: "Digital" }
];

const dialog = ref(false);
const saving = ref(false);
const form = ref({ name: "", type: "CASH", initialBalance: "" });

void catalog.load();

function walletIcon(type: string): string {
  const icons: Record<string, string> = {
    CASH: "money",
    BANK: "account_balance",
    CREDIT_CARD: "credit_card",
    DIGITAL: "smartphone"
  };
  return icons[type] || "account_balance_wallet";
}

function walletTypeLabel(type: string): string {
  return walletTypes.find(t => t.value === type)?.label || type;
}

async function onSave(): Promise<void> {
  if (!form.value.name.trim()) {
    $q.notify({ type: "negative", message: "Ingresa un nombre" });
    return;
  }
  saving.value = true;
  try {
    const initialBalance =
      form.value.initialBalance && Number(form.value.initialBalance) > 0
        ? parseAmountToCents(form.value.initialBalance)
        : 0;
    await catalog.addWallet({
      name: form.value.name.trim(),
      type: form.value.type,
      initial_balance: initialBalance
    });
    dialog.value = false;
    form.value = { name: "", type: "CASH", initialBalance: "" };
  } catch (err) {
    $q.notify({
      type: "negative",
      message:
        err instanceof Error && err.message ? err.message : "No se pudo guardar"
    });
  } finally {
    saving.value = false;
  }
}

async function onDelete(id: string): Promise<void> {
  try {
    await catalog.deleteWallet(id);
  } catch {
    $q.notify({ type: "negative", message: "No se pudo eliminar" });
  }
}
</script>
