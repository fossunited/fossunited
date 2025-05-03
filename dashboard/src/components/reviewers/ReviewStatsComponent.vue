<template>
  <div
    class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-2 items-center justify-between px-6 py-4 border rounded md:divide-x-2 *:px-6"
  >
    <div
      v-for="(value, key) in stats"
      :key="key"
      class="flex flex-col justify-center md:justify-normal items-center md:items-start"
    >
      <div class="flex gap-1 items-center text-xl font-medium first:px-0" :class="getColor(key)">
        {{ value }} <span v-if="key == 'Approvability'">%</span>
      </div>
      <span class="text-sm text-gray-500">{{ key }}</span>
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
    Approvability: 0,
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

  if (_stats.Approvals + _stats.Rejections > 0) {
    _stats.Approvability = Math.round(
      (_stats.Approvals / (_stats.Approvals + _stats.Rejections)) * 100,
    )
  }

  return _stats
})

const getColor = (key) => {
  switch (key) {
    case 'Approvals':
      return 'text-green-600'
    case 'Rejections':
      return 'text-red-600'
    case 'Not Sure':
      return 'text-orange-600'
    case 'Approvability':
      return 'text-blue-600'
    default:
      return 'text-gray-600'
  }
}
</script>
