<template>
  <div v-if="cfpSubmissions.data" class="flex flex-col">
    <ProposalListFilters @search="filterSubmissions($event)" />
    <ProposalListItem
      v-for="submission in cfpSubmissions.data"
      :key="submission.name"
      :submission="submission"
      tabindex="0"
      @click="handleOpenSubmission(submission)"
    />
  </div>
  <div
    v-else-if="cfpSubmissions.loading"
    class="w-full h-[480px] flex items-center justify-center"
  >
    <LoadingIndicator class="w-6 h-6" />
  </div>
  <div v-else class="w-full h-[480px] flex items-center justify-center">
    <div class="text-sm text-gray-500">No submissions found.</div>
  </div>
</template>
<script setup>
import ProposalListItem from './ProposalListItem.vue'
import ProposalListFilters from './ProposalListFilters.vue'
import { defineProps, watch } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
  event: {
    type: String,
    required: true,
  },
  justReviewed: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['open:submission'])

const cfpSubmissions = createResource({
  url: 'fossunited.api.reviewer.get_cfp_submissions',
  params: {
    event: props.event,
  },
  auto: true,
  transform(data) {
    cfpSubmissions.originalData = data
    return data.map((d) => {
      if (d.status == 'Approved') {
        d.status = 'Accepted'
      } else if (d.status == 'Rejected') {
        d.status = 'Declined'
      } else {
        d.status = 'Not Yet Decided'
      }
      return d
    })
  },
})

const handleOpenSubmission = (submission) => {
  submission._is_seen = true
  emit('open:submission', submission.name)
}

const filterSubmissions = (filters) => {
  if (
    !filters.talk_title &&
    !filters.only_show_unreviewed &&
    !filters.session_type &&
    !filters.intended_audience &&
    !filters.status
  ) {
    cfpSubmissions.data = cfpSubmissions.originalData
    return
  }

  cfpSubmissions.data = cfpSubmissions.originalData.filter((submission) => {
    let match = true

    if (filters.talk_title) {
      match = submission.talk_title.toLowerCase().includes(filters.talk_title.toLowerCase())
      if (!match) return false
    }

    if (filters.only_show_unreviewed) {
      match = !submission._is_reviewed
      if (!match) return false
    }

    if (filters.session_type) {
      match = submission.session_type === filters.session_type
      if (!match) return false
    }

    if (filters.intended_audience) {
      match = submission.intended_audience === filters.intended_audience
      if (!match) return false
    }

    if (filters.status) {
      match = submission.status === filters.status
      if (!match) return false
    }

    return match
  })
}
</script>
