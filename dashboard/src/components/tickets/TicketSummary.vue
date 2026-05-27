<template>
  <div
    class="bg-surface-white border border-outline-gray-2 rounded-lg p-6 flex flex-col gap-6 w-full"
  >
    <div>
      <p class="font-semibold text-ink-gray-9">Ticket Summary</p>
      <p class="text-xs text-ink-gray-4 mt-1">
        (Invoice/Receipt will be sent to the below details)
      </p>
    </div>

    <div class="flex flex-col gap-3 text-sm text-ink-gray-5">
      <div
        v-for="(count, tierName) in activeTierCounts"
        :key="tierName"
        class="flex justify-between"
      >
        <span>{{ getTierTitle(tierName) }} Ticket x{{ count }}</span>
        <span>₹{{ getTierPrice(tierName) * count }}</span>
      </div>
      <div v-if="tshirtCount > 0" class="flex justify-between">
        <span>T-Shirt x{{ tshirtCount }}</span>
        <span>₹{{ tshirtCount * tshirtPrice }}</span>
      </div>
      <div class="flex justify-between border-t pt-3">
        <span>Sub Total</span>
        <span>₹{{ subTotal }}</span>
      </div>
    </div>

    <div class="flex justify-between font-semibold text-ink-gray-9 border-t pt-4 text-base">
      <span>Total Amount</span>
      <span>₹{{ subTotal }}</span>
    </div>

    <ErrorMessage v-if="errorMessage" :message="errorMessage" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ErrorMessage } from 'frappe-ui'

const props = defineProps({
  activeTierCounts: { type: Object, default: () => ({}) },
  allTiers: { type: Array, default: () => [] },
  tshirtCount: { type: Number, default: 0 },
  tshirtPrice: { type: Number, default: 0 },
  errorMessage: { type: String, default: '' },
})

function getTierTitle(tierName) {
  return props.allTiers.find((t) => t.name === tierName)?.title || tierName
}

function getTierPrice(tierName) {
  return props.allTiers.find((t) => t.name === tierName)?.price || 0
}

const subTotal = computed(() => {
  let total = 0
  for (const [name, count] of Object.entries(props.activeTierCounts)) {
    total += getTierPrice(name) * (count || 0)
  }
  total += props.tshirtCount * props.tshirtPrice
  return total
})
</script>
