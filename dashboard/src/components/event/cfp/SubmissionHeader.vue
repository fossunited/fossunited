<script setup>
import ProposalBadgeGroup from '@/components/reviewers/ProposalBadgeGroup.vue'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'
import { IconArrowUpRight } from '@tabler/icons-vue'
import { inject } from 'vue'

const submission = inject('curr_submission')
</script>
<template>
  <div class="flex flex-col gap-2">
    <ProposalBadgeGroup
      :session-type="submission.data.session_type"
      :intended-audience="submission.data.intended_audience"
      :is-first-talk="submission.data.is_first_talk"
    />
    <div class="prose-sm">
      <h2 class="font-semibold">{{ submission.data.talk_title }}</h2>
    </div>
    <a
      class="flex gap-1 items-center text-sm text-gray-600 hover:cursor-pointer hover:text-gray-800 transition-colors"
      :href="createAbsoluteUrlFromRoute(submission.data.route)"
      target="_blank"
    >
      <span> View Public Page </span>
      <IconArrowUpRight class="w-4 h-4" />
    </a>
  </div>
</template>
