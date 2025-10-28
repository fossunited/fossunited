<template>
  <div
    class="border-t border-b py-4 px-2 gap-4 flex flex-col hover:bg-gray-50 focus:bg-gray-50 hover:cursor-pointer transition-colors duration-300"
  >
    <ProposalBadgeGroup
      :session-type="submission.session_type"
      :intended-audience="submission.intended_audience"
      :is-first-talk="submission.is_first_talk"
    />
    <h4 class="text-base transition-colors" :class="{ 'text-gray-600': submission._is_seen }">
      {{ submission.talk_title }}
    </h4>
    <div class="flex gap-2 items-center !text-sm">
      <Badge
        :label="submission._is_reviewed === 'Yes' ? 'Reviewed' : submission.status"
        :theme="getStatusBadgeTheme(submission._is_reviewed || submission.status)"
      />
      <Badge :label="submission._likes_count" variant="ghost" class="!text-gray-500">
        <template #prefix>
          <IconHeart size="14" />
        </template>
      </Badge>
      <span class="text-gray-600">{{ dayjs(submission.creation).fromNow() }} </span>
    </div>
  </div>
</template>
<script setup>
import { inject } from 'vue'
import { Badge } from 'frappe-ui'
import { IconHeart } from '@tabler/icons-vue'
import relativeTime from 'dayjs/plugin/relativeTime'
import ProposalBadgeGroup from './ProposalBadgeGroup.vue'
import { getStatusBadgeTheme } from '@/helpers/reviewer'

const dayjs = inject('$dayjs')
dayjs.extend(relativeTime)

defineProps({
  submission: {
    type: Object,
    required: true,
  },
})
</script>
