<script setup>
import { inject } from 'vue'
import { IconHeart, IconScale } from '@tabler/icons-vue'
import { getStatusBadgeTheme } from '@/helpers/reviewer'
import { Avatar, Badge, Tooltip } from 'frappe-ui'
import ReviewScoreIndicator from './ReviewScoreIndicator.vue'
import ProposalBadgeGroup from '@/components/reviewers/ProposalBadgeGroup.vue'
import relativeTime from 'dayjs/plugin/relativeTime'

function verdictLabel(u) {
  if (!u._review_verdict) return `${u.full_name} - Review Pending`
  if (u._review_verdict === 'Yes') return `${u.full_name} - Approved ✓`
  if (u._review_verdict === 'No') return `${u.full_name} - Rejected ✗`
  return `${u.full_name} - Not Sure`
}

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
    role="button"
    tabindex="0"
    class="border-t border-b py-4 px-2 flex justify-between items-center gap-4 hover:bg-surface-gray-1 focus:bg-surface-gray-2 focus:outline-none hover:cursor-pointer transition-colors duration-300"
    @click="$emit('open:submission', submission)"
    @keydown.enter="$emit('open:submission', submission)"
    @keydown.space.prevent="$emit('open:submission', submission)"
  >
    <div class="flex flex-col gap-4">
      <ProposalBadgeGroup
        :session-type="submission.session_type"
        :intended-audience="submission.intended_audience"
        :is-first-talk="submission.is_first_talk"
      />
      <h4
        class="text-base transition-colors text-wrap"
        :class="{ 'text-ink-gray-5': submission._is_seen }"
      >
        {{ submission.talk_title }}
      </h4>
      <div class="flex gap-2 items-center !text-sm flex-wrap">
        <Badge :label="submission.status" :theme="getStatusBadgeTheme(submission.status)" />
        <Badge v-if="submission._is_reviewed === 'Yes'" label="Reviewed" theme="blue" />
        <Badge
          :label="submission._likes_count"
          variant="ghost"
          class="!text-ink-gray-4"
          :aria-label="`${submission._likes_count} people like this proposal`"
        >
          <template #prefix>
            <IconHeart size="14" aria-hidden="true" />
          </template>
        </Badge>
        <span class="text-ink-gray-5">{{ dayjs(submission.creation).fromNow() }}</span>
        <ReviewScoreIndicator :submission="submission" />
      </div>
      <div v-if="submission.talk_license" class="flex items-center gap-1 text-xs text-ink-gray-5">
        <IconScale size="12" />
        <span>{{ submission.talk_license }}</span>
      </div>
      <div v-if="submission._assigned_users?.length" class="flex items-center gap-1">
        <Tooltip
          v-for="u in submission._assigned_users"
          :key="u.user"
          :text="verdictLabel(u)"
          placement="top"
        >
          <Avatar
            :image="u.user_image"
            :label="u.full_name"
            size="xs"
            class="rounded-full"
            :class="[
              !u._review_verdict && 'opacity-40',
              u._review_verdict === 'Yes' && 'ring-2 ring-green-500',
              u._review_verdict === 'No' && 'ring-2 ring-red-500',
              u._review_verdict === 'Maybe' && 'ring-2 ring-orange-400',
            ]"
          />
        </Tooltip>
      </div>
    </div>
  </div>
</template>
