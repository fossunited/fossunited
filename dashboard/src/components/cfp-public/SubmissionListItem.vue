<script setup>
import ProposalBadgeGroup from '@/components/reviewers/ProposalBadgeGroup.vue'
import { getStatusBadgeTheme } from '@/helpers/reviewer'
import { statusIndicatorColor } from '@/helpers/cfp'
import { IconHeart } from '@tabler/icons-vue'
import { Badge, Avatar } from 'frappe-ui'
defineProps({
  submission: {
    type: Object,
    required: true,
  },
})
</script>
<template>
  <a
    :href="`/${submission.route}`"
    target="_blank"
    class="p-2 md:p-6 bg-surface-white rounded border flex gap-3 h-fit hover:border-outline-gray-4 transition-colors ease-in-out duration-200"
  >
    <!-- Status colour bar -->
    <div
      class="w-1 self-stretch rounded-full shrink-0"
      :class="'bg-' + statusIndicatorColor(submission.status)"
    />

    <div class="flex flex-col gap-2 min-w-0 flex-1">
      <!-- Top row: session type left, likes right -->
      <div class="flex items-center justify-between gap-2">
        <Badge
          :label="submission.session_type"
          class="w-fit rounded-sm uppercase font-medium shrink-0"
        />
        <Badge size="sm" variant="ghost" class="gap-1 shrink-0 ml-auto">
          <IconHeart
            size="13"
            aria-hidden="true"
            :class="submission._is_liked_by_user ? 'fill-red-400 stroke-red-400' : ''"
          />
          <span>{{ submission._likes }}</span>
        </Badge>
      </div>

      <h4 class="text-base md:text-lg font-medium leading-snug">{{ submission.talk_title }}</h4>

      <div v-if="submission._speaker" class="flex flex-wrap gap-x-4 gap-y-2 mt-1">
        <div
          v-for="speaker in submission._speaker"
          :key="speaker.full_name"
          class="text-sm flex items-center gap-1.5 text-ink-gray-6 min-w-0"
        >
          <Avatar :image="speaker.photo" :label="speaker.full_name" size="xs" class="shrink-0" />
          <span class="truncate max-w-[120px] sm:max-w-none">{{ speaker.full_name }}</span>
        </div>
      </div>

      <div class="flex items-center justify-end mt-1">
        <Badge
          class="rounded-sm uppercase font-medium"
          :label="submission.status"
          :theme="getStatusBadgeTheme(submission.status)"
        />
      </div>
    </div>
  </a>
</template>
