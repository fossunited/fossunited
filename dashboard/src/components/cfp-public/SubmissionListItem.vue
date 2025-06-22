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
    class="p-6 bg-white rounded border flex gap-3 h-fit hover:border-gray-500 transition-colors ease-in-out duration-200"
  >
    <div
      class="h-full w-1 rounded-full"
      :class="'bg-' + statusIndicatorColor(submission.status)"
    ></div>
    <div class="flex justify-between gap-4 w-full">
      <div class="flex flex-col gap-2">
        <Badge :label="submission.session_type" class="w-fit rounded-sm uppercase font-medium" />
        <h4 class="text-lg font-medium text-wrap">{{ submission.talk_title }}</h4>
        <div v-if="submission._speaker" class="flex gap-4 items-center mt-2">
          <div
            v-for="speaker in submission._speaker"
            :key="speaker.full_name"
            class="text-sm flex items-center gap-2 text-gray-700"
          >
            <Avatar :image="speaker.photo" :label="speaker.full_name" />
            <span>{{ speaker.full_name }}</span>
          </div>
        </div>
      </div>
      <div class="flex flex-col justify-between items-end gap-2">
        <Badge size="lg" variant="ghost">
          <IconHeart
            v-if="submission._is_liked_by_user"
            size="15"
            class="fill-red-400 stroke-red-400"
          />
          <IconHeart v-else size="15" />
          <span>{{ submission._likes }}</span>
        </Badge>
        <Badge
          size="lg"
          class="rounded-sm uppercase font-medium"
          :label="submission.status"
          :theme="getStatusBadgeTheme(submission.status)"
        />
      </div>
    </div>
  </a>
</template>
