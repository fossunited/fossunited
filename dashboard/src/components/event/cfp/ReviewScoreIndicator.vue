<script setup>
import { Popover } from 'frappe-ui'
import { computed } from 'vue'

const props = defineProps({
  submission: {
    type: Object,
    required: true,
  },
})

const scoreTableItems = computed(() => {
  return [
    {
      label: 'Approved',
      value: props.submission.approved_percent,
      color: 'bg-green-400',
    },
    {
      label: 'Rejected',
      value: props.submission.rejected_percent,
      color: 'bg-red-400',
    },
    {
      label: 'Unsure',
      value: props.submission.unsure_percent,
      color: 'bg-orange-400',
    },
  ]
})

const hasScores = computed(() => {
  return (
    props.submission.approved_percent > 0 ||
    props.submission.rejected_percent > 0 ||
    props.submission.unsure_percent > 0
  )
})
</script>
<template>
  <Popover trigger="hover">
    <template #target>
      <div v-if="hasScores" class="flex flex-col items-start gap-1 w-32 text-xs p-2">
        <div class="w-full h-1 flex *:rounded">
          <div :style="{ width: `${submission.approved_percent}%` }" class="bg-green-400"></div>
          <div :style="{ width: `${submission.rejected_percent}%` }" class="bg-red-400"></div>
          <div :style="{ width: `${submission.unsure_percent}%` }" class="bg-orange-400"></div>
        </div>
      </div>
      <span v-else class="text-ink-gray-5 ml-2">Not yet reviewed</span>
    </template>
    <template #body-main>
      <div class="p-4 bg-surface-white rounded flex flex-col gap-2">
        <div
          v-for="scoreItem in scoreTableItems"
          :key="scoreItem.label"
          class="flex gap-2 last:border-t last:pt-2"
        >
          <div class="h-4 w-4" :class="scoreItem.color"></div>
          <span class="text-sm font-medium">{{ scoreItem.label }}</span>
          <span class="text-sm font-medium">{{ scoreItem.value }}%</span>
        </div>
      </div>
    </template>
  </Popover>
</template>
