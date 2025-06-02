<template>
  <Filter v-model="filters" :docfields="docfields.data" />
  <div v-if="cfpSubmissions.data" class="flex flex-col">
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
import { defineProps, watch } from 'vue'
import { createResource } from 'frappe-ui'
import Filter from '../ui/Filter.vue'
import { getCfpFilterFields, filterSubmissions } from '@/helpers/cfp'
import { useRoute } from 'vue-router'
import { useStorage } from '@vueuse/core'

const route = useRoute()

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

const filters = useStorage(`review-filters:${route.params.id}`, {})
const docfields = await getCfpFilterFields(route.params.id)

const cfpSubmissions = createResource({
  url: 'fossunited.api.reviewer.get_cfp_submissions',
  params: {
    event: props.event,
  },
  auto: true,
  onSuccess(data) {
    if (filters.value) {
      cfpSubmissions.data = filterSubmissions(data, filters.value)
    }
  },
  transform(data) {
    cfpSubmissions.originalData = data
  },
})

watch(
  () => filters.value,
  () => {
    cfpSubmissions.data = filterSubmissions(cfpSubmissions.originalData, filters.value)
  },
  { deep: true },
)

const handleOpenSubmission = (submission) => {
  submission._is_seen = true
  emit('open:submission', submission.name)
}
</script>
