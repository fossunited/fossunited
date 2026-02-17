<template>
  <div class="p-6 space-y-3">
    <h4 class="text-base font-medium text-ink-gray-5 uppercase mb-2">Edit Your Proposal</h4>
    <div class="prose max-w-full">
      <h2>{{ submission.talk_title }}</h2>
    </div>
    <div class="flex gap-2 text-base items-center">
      <span>{{ submission.event_name }}</span>
      <Badge :theme="badgeTheme[submission.status]" :label="submission.status" />
    </div>
    <Button
      label="See Public Page"
      icon-right="arrow-up-right"
      @click="redirectRoute(submission.route)"
    />
  </div>
</template>
<script setup>
import { Badge } from 'frappe-ui'
import { redirectRoute } from '@/helpers/utils'

defineProps({
  submission: {
    type: Object,
    required: true,
  },
})

const badgeTheme = {
  Pending: 'yellow',
  Approved: 'green',
  Rejected: 'red',
  Withdrawn: 'red',
}
</script>
