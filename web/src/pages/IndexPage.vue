<template>
  <q-page class="q-pa-md bg-grey-3">

    <div class="row">
      <div class="col-xs-12 col-sm-6">

        <div class="row q-col-gutter-md">
          <div class="col-4">
            <div class="row bg-white q-pa-sm">
              <div class="col-12">
                Total balance
              </div>
              <div class="col-12">
                <span class="text-weight-medium text-h6">$ 999,999.99</span>
              </div>
            </div>
          </div>
          <div class="col-4">
            <div class="row bg-white q-pa-sm">
              <div class="col-12">
                Income
              </div>
              <div class="col-12">
                <span class="text-weight-medium text-h6">$ 999,999.99</span>
              </div>
            </div>
          </div>
          <div class="col-4">
            <div class="row bg-white q-pa-sm">
              <div class="col-12">
                Outcome
              </div>
              <div class="col-12">
                <span class="text-weight-medium text-h6">$ 999,999.99</span>
              </div>
            </div>
          </div>

        </div>

      </div>

      <div class="col-xs-12 col-sm-6">
        <div class="row">
          <div class="offset-9 col-3">
            <q-select
              filled
              v-model="model"
              :options="options"
              label="Month"
              emit-value
              map-options
            />
          </div>
        </div>
      </div>
    </div>
    <!-- <div class="row bg-white">
      <div class="col-12">
        <div class="row">
          <div class="col-12">
            Total balance
          </div>
          <div class="col-12">
            <span class="text-weight-medium text-h6">$ 999,999.99</span>
          </div>
        </div>
      </div>
    </div> -->
    <!-- </div> -->
    <!-- <example-component
      title="Example component"
      active
      :todos="todos"
      :meta="meta"
    ></example-component> -->

    <div class="row q-mt-md">
      <div class="col-12">
        <q-table
          title="Treats"
          :rows="rows"
          :columns="columns"
          row-key="id"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
// import type { Ref } from 'vue'

const model = ref('Oct')
const options = [{ label: 'Oct', value: 'Oct' }]
const rows = [
  { id: 1, date: 'Y-m-d H:i:s', amount: 99999.99, type: 1, action: 1, description: 'Something' },
  { id: 2, date: 'Y-m-d H:i:s', amount: 99999.99, type: 1, action: -1, description: 'Something' },
  { id: 3, date: 'Y-m-d H:i:s', amount: 99999.99, type: 1, action: 1, description: 'Something' }
]

const columns = [
  { name: 'date', align: 'left', label: 'Date', field: 'date', sortable: true },
  { name: 'amount', align: 'left', label: 'Amount', field: 'amount', sortable: true },
  { name: 'description', align: 'left', label: '', field: 'description', sortable: true }
]



</script>
