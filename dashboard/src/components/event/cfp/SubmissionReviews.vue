<script setup>
import { Badge } from 'frappe-ui'
import { IconStar } from '@tabler/icons-vue'
import { cleanedHTML } from '@/helpers/utils'
import ReviewStatsComponent from '@/components/reviewers/ReviewStatsComponent.vue'
defineProps({
  reviews: {
    type: Array,
    required: true,
  },
})

const getLabel = (status) => {
  switch (status) {
    case 'Maybe':
      return 'Maybe'
    case 'Yes':
      return 'Approved'
    case 'No':
      return 'Rejected'
    default:
      return status
  }
}

const getTheme = (status) => {
  switch (status) {
    case 'Maybe':
      return 'orange'
    case 'Yes':
      return 'green'
    case 'No':
      return 'red'
    default:
      return 'gray'
  }
}
</script>
<template>
  <div class="flex flex-col gap-4">
    <ReviewStatsComponent :reviews="reviews" />

    <div class="flex flex-col">
      <div v-for="review in reviews" :key="review.name" class="flex flex-col gap-1 border-b py-3">
        <div class="flex justify-between items-center gap-4">
          <div
            v-if="review.remarks"
            class="prose prose-sm"
            v-html="cleanedHTML(review.remarks)"
          ></div>
          <span v-else class="text-base text-ink-gray-5">No Remarks</span>
        </div>
        <div class="flex gap-2 items-center">
          <span class="text-sm">Reviewer #{{ review.idx }}</span>
          <Badge :label="getLabel(review.to_approve)" :theme="getTheme(review.to_approve)" />
          <IconStar
            v-if="review.must_have"
            class="w-4 h-4 text-yellow-500"
            fill="currentColor"
          />
        </div>
        <p
          v-if="review.private_comment"
          class="text-sm text-ink-gray-7 whitespace-pre-wrap"
        >
          {{ review.private_comment }}
        </p>
      </div>
    </div>
  </div>
</template>
