<template>
  <div
    class="grid gap-4 md:gap-2 items-center justify-between px-6 py-4 border rounded md:divide-x-2 *:px-6"
    :class="avgScore !== null ? 'grid-cols-4' : 'grid-cols-3'"
  >
    <div
      v-for="(value, key) in stats"
      :key="key"
      class="flex flex-col justify-center md:justify-normal items-center md:items-start"
    >
      <div class="flex gap-1 items-center text-xl font-medium first:px-0" :class="getColor(key)">
        {{ value }}
      </div>
      <span class="text-sm text-ink-gray-4">{{ key }}</span>
    </div>
    <div v-if="avgScore !== null" class="flex flex-col justify-center md:justify-normal items-center md:items-start">
      <div class="flex gap-1 items-center text-xl font-medium text-ink-blue-3">
        {{ avgScore }}
      </div>
      <span class="text-sm text-ink-gray-4">Avg. Score</span>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'

const props = defineProps({
  reviews: {
    type: Array,
    required: true,
  },
})

const stats = computed(() => {
  let _stats = {
    Approvals: 0,
    Rejections: 0,
    'Not Sure': 0,
  }

  props.reviews.forEach((review) => {
    if (review.to_approve === 'Yes') {
      _stats.Approvals += 1
    } else if (review.to_approve === 'No') {
      _stats.Rejections += 1
    } else if (review.to_approve === 'Maybe') {
      _stats['Not Sure'] += 1
    }
  })

  return _stats
})

const avgScore = computed(() => {
  const scoredReviews = props.reviews.filter((r) => r.total_score && r.total_score > 0)
  if (!scoredReviews.length) return null
  const sum = scoredReviews.reduce((acc, r) => acc + (r.total_score || 0), 0)
  return (sum / scoredReviews.length).toFixed(1)
})

const getColor = (key) => {
  switch (key) {
    case 'Approvals':
      return 'text-ink-green-3'
    case 'Rejections':
      return 'text-ink-red-4'
    case 'Not Sure':
      return 'text-ink-amber-3'
    default:
      return 'text-ink-gray-5'
  }
}
</script>
