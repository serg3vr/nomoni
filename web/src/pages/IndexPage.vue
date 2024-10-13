<template>
  <q-page class="row items-center justify-evenly">
    <!-- <example-component
      title="Example component"
      active
      :todos="todos"
      :meta="meta"
    ></example-component> -->
    <pre>{{ txs }}</pre>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Ref } from 'vue'
// import { Todo, Meta } from 'components/models';
// import ExampleComponent from 'components/ExampleComponent.vue';

import { createClient } from '@supabase/supabase-js'

// Create a single supabase client for interacting with your database
const supabase = createClient(
  '',
  ''
)
console.log(supabase)

interface ITxs {
  int: number,
  date: string,
  amount: number
}

const txs: Ref<ITxs[]> = ref([])

/* const showTransaction = async () => {
  console.info(supabase)
  let { data: transactions, error } = await supabase
    .from('transactions')
    .select('id, date, amount')
    console.error(error)
  txs.value = transactions
} */


// defineOptions({
//   name: 'IndexPage'
// });

// const todos = ref<Todo[]>([
//   {
//     id: 1,
//     content: 'ct1'
//   },
//   {
//     id: 2,
//     content: 'ct2'
//   },
//   {
//     id: 3,
//     content: 'ct3'
//   },
//   {
//     id: 4,
//     content: 'ct4'
//   },
//   {
//     id: 5,
//     content: 'ct5'
//   }
// ]);

// const meta = ref<Meta>({
//   totalCount: 1200
// });
</script>
