<script setup>
import { createResource, LoadingIndicator, TabButtons } from 'frappe-ui'
import { provide, ref, watch, computed, inject } from 'vue'
import SubmissionHeader from './SubmissionHeader.vue'
import SubmissionInfoList from './SubmissionInfoList.vue'
import SubmissionOverview from './SubmissionOverview.vue'
import ProposalSpeakers from '@/components/reviewers/ProposalSpeakers.vue'
import SubmissionReviews from './SubmissionReviews.vue'
import AssignReviewers from './AssignReviewers.vue'

const props = defineProps({
  eventId: { type: String, default: '' },
})
const emit = defineEmits(['reviewers:updated'])
const submissionId = defineModel('submissionId', { type: String, default: '' })
const tabs = ref([
  {
    label: 'Overview',
    value: 0,
  },
  {
    label: 'Speakers',
    value: 1,
  },
  {
    label: 'Reviews',
    value: 2,
  },
])
const activeTab = ref(0)

const submission = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP Submission',
      fields: ['*'],
      filters: { name: submissionId.value },
    }
  },
})

provide('curr_submission', submission)

const event = inject('event')
const showAssignReviewers = computed(() => {
  if (!props.eventId) return false
  if (submission.data?.status !== 'Review Pending') return false
  const startDate = event?.doc?.event_start_date
  if (!startDate) return true
  return new Date() < new Date(startDate)
})

watch(
  () => submissionId.value,
  (newId) => {
    if (newId) {
      activeTab.value = 0
      submission.fetch()
    }
  },
  { immediate: true },
)
</script>
<template>
  <Suspense>
    <div v-if="submission.data" class="w-full p-3 sm:p-6 flex flex-col gap-4 overflow-y-scroll max-h-svh">
      <SubmissionHeader />
      <AssignReviewers v-if="showAssignReviewers" :submission-id="submissionId" :event-id="props.eventId" @reviewers:updated="emit('reviewers:updated', $event)" />
      <SubmissionInfoList />
      <TabButtons v-if="tabs.length > 1" v-model="activeTab" class="w-fit" :buttons="tabs" />
      <SubmissionOverview v-if="activeTab === 0" />
      <ProposalSpeakers v-else-if="activeTab === 1" :speakers="submission.data.speakers" />
      <SubmissionReviews v-else-if="activeTab === 2" :reviews="submission.data.reviews" />
    </div>
    <template #fallback>
      <LoadingIndicator class="w-5 h-5" />
    </template>
  </Suspense>
</template>
