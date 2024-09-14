<template>
  <div v-if="proposal" class="flex justify-between">
    <div class="flex flex-col gap-3 justify-between">
      <h3 class="text-xl font-semibold">
        <a
          :href="createAbsoluteUrlFromRoute(proposal.route)"
          class="hover:text-green-500 transition-colors duration-300 cursor-pointer"
        >
          {{ proposal.talk_title }}
        </a>
      </h3>
      <div class="flex flex-col gap-3 items-start mt-1 md:flex-row md:items-center">
        <div class="flex items-center text-xs font-semibold">
          <span class="bg-gray-200 px-2 py-1 text-gray-600 rounded-sm mr-2">{{
            proposal.session_type.toUpperCase()
          }}</span>
          <div>
            <span
              class="px-2 py-1 rounded-sm md:hidden"
              :class="getStatusClass(proposal.status)"
              >{{ proposal.status.toUpperCase() }}</span
            >
          </div>
        </div>
        <div v-if="proposal.full_name != ''" class="flex text-sm">
          <SpeakerIcon />
          <span>
            {{ proposal.full_name }}
          </span>
        </div>
      </div>
    </div>
    <div class="flex flex-col gap-3 items-end">
      <div class="flex items-center gap-1 bg-gray-200 px-1.5 py-1 rounded-sm">
        <LikesIcon />
        <span class="text-xs font-semibold">{{ proposal.likes }}</span>
      </div>
      <div class="mt-2">
        <span
          class="px-2 py-1 rounded-sm text-xs font-semibold hidden md:block"
          :class="getStatusClass(proposal.status)"
          >{{ proposal.status.toUpperCase() }}</span
        >
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import SpeakerIcon from '../../components/icons/SpeakerIcon.vue'
import LikesIcon from '../../components/icons/LikesIcon.vue'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'

const props = defineProps({
  proposal: {
    type: Object,
    required: true,
  },
})

const getStatusClass = (status) => {
  switch (status) {
    case 'Approved':
      return 'bg-green-100 text-green-800'
    case 'Rejected':
      return 'bg-red-100 text-red-800'
    case 'Screening':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-yellow-100 text-yellow-800'
  }
}
</script>
