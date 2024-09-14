<template>
  <div class="flex flex-col w-full border rounded-sm p-4">
    <div class="text-sm uppercase font-semibold">{{ tier.title }}</div>
    <div class="flex gap-2 items-end justify-between mt-6">
      <div>
        <div class="prose">
          <h2 class="">{{ tier.total_sold }}</h2>
        </div>
        <span v-if="tier.tier_capacity" class="text-sm text-gray-600 mb-1"
          >out of {{ tier.tier_capacity }}</span
        >
      </div>
      <div
        class="flex items-center gap-1 text-sm mt-1 font-medium p-1 w-fit rounded-sm px-2"
        :class="
          tier.tickets_sold_today === 0
            ? 'bg-gray-100 text-gray-600'
            : 'bg-green-100 text-green-600'
        "
      >
        <svg
          v-if="tier.tickets_sold_today"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler w-4 h-4 -mx-1 icons-tabler-outline icon-tabler-arrow-narrow-up"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M12 5l0 14" />
          <path d="M16 9l-4 -4" />
          <path d="M8 9l4 -4" />
        </svg>
        <span>{{ tier.tickets_sold_today }}</span>
        <span>sold today</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  tier: {
    type: Object,
    required: true,
  },
})
</script>
