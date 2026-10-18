<template>
  <q-card flat bordered class="q-pa-md">
    <div class="row items-center justify-between">
      <q-avatar size="32px" color="grey-2" text-color="grey-9">
        <q-icon :name="icon" size="22px" />
      </q-avatar>
      <div class="text-subtitle2 text-grey-6">{{ label }}</div>
    </div>
    <div class="text-h4 text-weight-bold q-mt-sm">{{ value }}</div>
    <div class="text-caption text-grey-7 q-mt-xs">{{ caption }}</div>
  </q-card>
</template>

<script setup lang="ts">
defineProps<{
  icon: string;
  label: string;
  value: string;
  caption: string;
}>();
</script>
