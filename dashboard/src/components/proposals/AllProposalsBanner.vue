<template>
  <div v-if="event" class="flex items-end gap-x-4 my-6">
    <AllProposalsBannerImage class="hidden lg:block" />
    <div class="flex flex-col gap-y-4 lg:w-3/4">
      <div class="flex flex-col gap-y-2">
        <h1 class="text-3xl font-semibold">Talk Proposals</h1>
        <p class="text-gray-700 font-medium">
          <span v-if="event.proposal_page_description">
            {{ event.proposal_page_description }}
          </span>
          <span v-else>
            Explore the proposals for {{ event.event_name }}, that offers a wide
            array of sessions.
          </span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import AllProposalsBannerImage from '@/components/proposals/AllProposalsBannerImage.vue'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})
</script>
