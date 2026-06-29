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

function verdictRing(u) {
  return {
    'opacity-40 dark:opacity-75 ring-2 ring-outline-gray-3 dark:ring-outline-gray-4':
      !u._review_verdict,
    'ring-2 ring-green-500': u._review_verdict === 'Yes',
    'ring-2 ring-red-500': u._review_verdict === 'No',
    'ring-2 ring-orange-400': u._review_verdict === 'Maybe',
  }
}

const dayjs = inject('$dayjs')
dayjs.extend(relativeTime)

const props = defineProps({
  submission: {
    type: Object,
    required: true,
  },
  sortBy: {
    type: String,
    default: 'creation_desc',
  },
})

function sortMeta(submission, sortBy) {
  switch (sortBy) {
    case 'review_count_desc':
      return `${submission._review_count ?? 0} review${(submission._review_count ?? 0) !== 1 ? 's' : ''}`
    case 'assigned_count_desc':
      return `${submission._assigned_users?.length ?? 0} assigned`
    default:
      return dayjs(submission.creation).fromNow()
  }
}

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
        <Tooltip text="Proposal status managed event organizer" placement="top">
          <Badge :label="submission.status" :theme="getStatusBadgeTheme(submission.status)" />
        </Tooltip>
        <Tooltip
          v-if="submission._is_reviewed === 'Yes'"
          text="You've added your review"
          placement="top"
        >
          <Badge label="Reviewed" theme="blue" />
        </Tooltip>
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
        <span class="text-ink-gray-5">{{ sortMeta(submission, sortBy) }}</span>
        <ReviewScoreIndicator :submission="submission" />
      </div>
      <div v-if="submission.talk_license" class="flex items-center gap-1 text-xs text-ink-gray-5">
        <IconScale size="12" />
        <span>{{ submission.talk_license }}</span>
      </div>
      <div v-if="submission._assigned_users?.length" class="flex items-center gap-2">
        <Tooltip
          v-for="u in submission._assigned_users"
          :key="u.user"
          :text="verdictLabel(u)"
          placement="top"
        >
          <!-- can be LazyObserved, but since we've Only ~15-30 unique reviewers across all proposals
               URL repeats and the browser cache fetches each once. -->
          <Avatar
            :image="u.user_image"
            :label="u.full_name"
            size="sm"
            class="rounded-full"
            :class="verdictRing(u)"
          />
        </Tooltip>
      </div>
    </div>
  </div>
</template>
