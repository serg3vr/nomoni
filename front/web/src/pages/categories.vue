<template>
  <q-page class="q-pa-md q-pb-xl">
    <q-btn
      color="primary"
      icon="add"
      label="Nueva categoría"
      no-caps
      class="q-mb-md"
      @click="dialog = true"
    />

    <q-card flat bordered>
      <q-list separator>
        <div v-if="catalog.categories.length === 0" class="q-pa-md text-grey-7">
          No tienes categorías.
        </div>
        <q-item v-for="category in catalog.categories" :key="category.id">
          <q-item-section avatar>
            <q-avatar
              :color="category.color || 'primary'"
              text-color="white"
              icon="label"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>
              {{ category.name }}
              <q-icon
                v-if="category.is_system"
                name="lock"
                size="2em"
                color="grey-6"
              >
                <q-tooltip>Sistema, no modificable</q-tooltip>
              </q-icon>
            </q-item-label>
            <q-item-label v-if="category.hidden" caption> Oculta </q-item-label>
          </q-item-section>
          <q-item-section v-if="!category.is_system" side>
            <q-btn flat round dense icon="edit" @click="openEdit(category)" />
            <q-btn
              flat
              round
              dense
              color="grey-7"
              icon="delete"
              @click="onDelete(category.id)"
            />
          </q-item-section>
        </q-item>
      </q-list>
    </q-card>

    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 320px">
        <q-card-section class="text-h6">
          {{ editingId ? "Editar categoría" : "Nueva categoría" }}
        </q-card-section>
        <q-card-section>
          <q-input v-model="form.name" filled label="Nombre" autofocus />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" no-caps @click="closeDialog" />
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
import { ref } from "vue";
import { useCatalogStore } from "@/stores/catalog";
import type { Category } from "@/types/api";

const $q = useQuasar();
const catalog = useCatalogStore();

const dialog = ref(false);
const editingId = ref<string | null>(null);
const form = ref({ name: "" });
const saving = ref(false);

void catalog.load();

function openEdit(category: Category): void {
  editingId.value = category.id;
  form.value = { name: category.name };
  dialog.value = true;
}

function closeDialog(): void {
  dialog.value = false;
  editingId.value = null;
  form.value = { name: "" };
}

async function onSave(): Promise<void> {
  if (!form.value.name.trim()) {
    $q.notify({ type: "negative", message: "Ingresa un nombre" });
    return;
  }
  saving.value = true;
  try {
    if (editingId.value) {
      await catalog.updateCategory(editingId.value, {
        name: form.value.name.trim()
      });
    } else {
      await catalog.addCategory({ name: form.value.name.trim() });
    }
    closeDialog();
  } catch {
    $q.notify({ type: "negative", message: "No se pudo guardar" });
  } finally {
    saving.value = false;
  }
}

async function onDelete(id: string): Promise<void> {
  try {
    await catalog.deleteCategory(id);
  } catch {
    $q.notify({
      type: "negative",
      message: "No se pudo eliminar. ¿Tiene movimientos?"
    });
  }
}
</script>
