<script setup>
import { inject } from 'vue'
import { IconHeart } from '@tabler/icons-vue'
import { getStatusBadgeTheme } from '@/helpers/reviewer'
import { Badge } from 'frappe-ui'
import ReviewScoreIndicator from './ReviewScoreIndicator.vue'
import ProposalBadgeGroup from '@/components/reviewers/ProposalBadgeGroup.vue'
import relativeTime from 'dayjs/plugin/relativeTime'

const dayjs = inject('$dayjs')
dayjs.extend(relativeTime)

defineProps({
  submission: {
    type: Object,
    required: true,
  },
})

defineEmits(['open:submission'])
</script>

<template>
  <div
    class="border-t border-b py-4 px-2 flex justify-between items-center gap-4 hover:bg-gray-50 focus:bg-gray-50 hover:cursor-pointer transition-colors duration-300"
    @click="$emit('open:submission', submission)"
  >
    <div class="flex flex-col gap-4">
      <ProposalBadgeGroup
        :session-type="submission.session_type"
        :intended-audience="submission.intended_audience"
        :is-first-talk="submission.is_first_talk"
      />
      <h4 class="text-base transition-colors text-wrap">
        {{ submission.talk_title }}
      </h4>
      <div class="flex gap-2 items-center !text-sm">
        <Badge :label="submission.status" :theme="getStatusBadgeTheme(submission.status)" />
        <Badge :label="submission._likes_count" variant="ghost" class="!text-gray-500">
          <template #prefix>
            <IconHeart size="14" />
          </template>
        </Badge>
        <span class="text-gray-600">{{ dayjs(submission.creation).fromNow() }} </span>
        <ReviewScoreIndicator :submission="submission" />
      </div>
    </div>
  </div>
</template>
