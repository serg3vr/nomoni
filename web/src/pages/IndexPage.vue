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
          <div class="offset-9 col-3 text-right">
            <q-btn
              outline
              color="primary"
              class="bg-white"
              label="Add"
              icon="add"
              @click="addTransactionModal = true"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="row q-mt-md">
      <div class="col-12">
        <q-table
          flat
          :rows="rows"
          :columns="columns"
          row-key="id"
          hide-header
        />
      </div>
    </div>

    <q-dialog v-model="addTransactionModal">
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Add {{ fieldsType }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section style="max-height: 66vh" class="scroll">
           <div class="row">
            <div class="col-12">
              <q-radio v-model="fields.type" val="1" label="Income" />
              <q-radio v-model="fields.type" val="2" label="Outcome" />
            </div>
            <div class="col-12">
              <q-input filled v-model="fields.date">
                <template v-slot:prepend>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="fields.date" mask="YYYY-MM-DD HH:mm">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>

                <template v-slot:append>
                  <q-icon name="access_time" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="fields.date" mask="YYYY-MM-DD HH:mm" format24h>
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-time>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
            <div class="col-12">
              <q-input v-model="fields.amount" label="Amount" />
            </div>
           </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <!-- <q-btn flat label="Decline" color="primary" v-close-popup /> -->
          <q-btn flat label="Accept" color="primary" v-close-popup @click="loadTransactions" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
// import type { Ref } from 'vue'
import { api } from 'src/boot/axios'

const addTransactionModal = ref(false)
const fields = reactive({
  type: '2',
  date: '2019-02-01 12:44',
  amont: null
})

const fieldsType = computed(() => {
  return ['', 'income', 'outcome'][fields.type]
})

const rows = ref([])

const columns = [
  { name: 'date', align: 'left', label: 'Date', field: 'date', sortable: false },
  { name: 'amount', align: 'left', label: 'Amount', field: 'amount', sortable: false },
  { name: 'description', align: 'left', label: '', field: 'description', sortable: false }
]

const loadTransactions = () => {
  api.get('transactions').then(({ data }) => {
    rows.value = data
  }).catch(error => error)
}

loadTransactions()
</script>
