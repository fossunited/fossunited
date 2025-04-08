<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Sold T-shirt Details',
    }"
    role="dialog"
    aria-modal="true"
    aria-labelledby="dialog-title"
  >
    <template #body-content>
      <div class="text-sm">
        <h2 id="dialog-title" class="sr-only">Sold T-shirt Details</h2>
        <p class="mb-2">T-shirts sold for this event.</p>
      </div>
      <table class="w-3/4 table-fixed text-center" role="table" aria-describedby="dialog-title">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
          <tr role="row">
            <th class="p-2 border" role="columnheader" scope="col">Size</th>
            <th class="p-2 border" role="columnheader" scope="col">Quantity</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(quantity, size) in insight.tshirt_size_count" :key="size" role="row">
            <td class="p-2 text-base border" role="cell">{{ size }}</td>
            <td class="p-2 text-base border" role="cell">{{ quantity }}</td>
          </tr>
          <tr role="row">
            <td class="p-2 text-base font-semibold" role="rowheader">Total</td>
            <td class="p-2 text-base font-semibold" role="cell">{{ insight.tshirts_sold }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </Dialog>
  <div class="flex flex-col w-full border rounded-sm p-4">
    <div class="text-sm flex gap-2 items-center uppercase font-semibold">
      <IconShirtFilled class="w-5 h-5" aria-hidden="true" />
      <span> T-shirts Sold </span>
    </div>
    <div class="flex gap-2 items-end justify-between mt-6">
      <div class="prose">
        <h2 id="total-tshirts" class="text-lg font-bold">{{ insight.tshirts_sold }}</h2>
      </div>
      <Button class="w-fit" label="View Details" @click="showDialog = true" aria-labelledby="dialog-title" />
    </div>
  </div>
</template>

<script setup>
import { Dialog } from 'frappe-ui'
import { defineProps, ref } from 'vue'
import { IconShirtFilled } from '@tabler/icons-vue'

const showDialog = ref(false)

const props = defineProps({
  insight: {
    type: Object,
    required: true,
  },
})
</script>
