<template>
  <div class="p-6 space-y-3">
    <h4 class="text-base font-medium text-ink-gray-5 uppercase mb-2">Edit Your Proposal</h4>
    <div class="prose max-w-full">
      <h2>{{ submission.talk_title }}</h2>
    </div>
    <div class="flex gap-2 text-base items-center">
      <span>{{ submission.event_name }}</span>
      <Badge :theme="badgeTheme[submission.status]" :label="submission.status" />
      <span v-if="readonly" class="flex items-center gap-1 text-ink-gray-5">
        <IconLock class="w-4 h-4" />
        Read-only
      </span>
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
import { IconLock } from '@tabler/icons-vue'
import { redirectRoute } from '@/helpers/utils'

defineProps({
  submission: {
    type: Object,
    required: true,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
})

const badgeTheme = {
  Pending: 'yellow',
  Approved: 'green',
  Rejected: 'red',
  Withdrawn: 'red',
}
</script>
