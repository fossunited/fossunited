<template>
  <div
    class="border-t border-b py-4 px-2 gap-4 flex flex-col hover:bg-surface-gray-1 focus:bg-surface-gray-2 focus:outline-none hover:cursor-pointer transition-colors duration-300"
  >
    <ProposalBadgeGroup
      :session-type="submission.session_type"
      :intended-audience="submission.intended_audience"
      :is-first-talk="submission.is_first_talk"
    />
    <h4 class="text-base transition-colors" :class="{ 'text-ink-gray-5': submission._is_seen }">
      {{ submission.talk_title }}
    </h4>
    <div class="flex gap-2 items-center !text-sm flex-wrap">
      <Badge :label="submission.status" :theme="getStatusBadgeTheme(submission.status)" />
      <Badge v-if="submission._is_reviewed === 'Yes'" label="Reviewed" theme="blue" />
      <Badge :label="submission._likes_count" variant="ghost" class="!text-ink-gray-4">
        <template #prefix>
          <IconHeart size="14" />
        </template>
      </Badge>
      <span class="text-ink-gray-5">{{ dayjs(submission.creation).fromNow() }} </span>
    </div>
    <div v-if="submission.talk_license" class="flex items-center gap-1 text-xs text-ink-gray-5">
      <IconScale size="12" />
      <span>{{ submission.talk_license }}</span>
    </div>
  </div>
</template>
<script setup>
import { inject } from 'vue'
import { Badge } from 'frappe-ui'
import { IconHeart, IconScale } from '@tabler/icons-vue'
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
