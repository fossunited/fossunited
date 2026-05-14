<script setup>
import InsightsGrid from '@/components/event/cfp/InsightsGrid.vue'
import SubmissionsList from '@/components/event/cfp/SubmissionsList.vue'
import SubmissionDrawer from '@/components/event/cfp/SubmissionDrawer.vue'
import SubmissionDetails from '@/components/event/cfp/SubmissionDetails.vue'
import { createResource, LoadingIndicator } from 'frappe-ui'
import { ref, inject, provide } from 'vue'
import { useRoute } from 'vue-router'
import { isSmallScreen } from '@/helpers/utils'

const submissionsListRef = ref(null)
const route = useRoute()
const event = inject('event')

const showDrawer = ref(false)
const selectedSubmission = ref('')

const cfp_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event CFP',
    fields: ['*'],
    filters: {
      event: route.params.id,
    },
  },
  auto: true,
})

const handleOpenSubmission = (submission) => {
  selectedSubmission.value = submission
  if (isSmallScreen.value) {
    showDrawer.value = true
  }
}

const refreshSubmissions = () => {
  submissionsListRef.value?.reloadSubmissions?.()
}
provide('refreshSubmissions', refreshSubmissions)
</script>

<template>
  <div class="flex flex-col md:flex-row">
    <div
      class="w-full md:basis-2/5 shrink-0 p-4 md:p-8 flex flex-col gap-4 border-r md:overflow-y-scroll md:max-h-svh"
    >
      <Suspense>
        <InsightsGrid :event-id="route.params.id" />
      </Suspense>
      <Suspense>
        <SubmissionsList
          ref="submissionsListRef"
          :event="route.params.id"
          @open:submission="handleOpenSubmission($event)"
        />
        <template #fallback>
          <LoadingIndicator class="w-5 h-5" />
        </template>
      </Suspense>
    </div>
    <div v-if="!isSmallScreen" class="flex w-full basis-3/5 shrink-0">
      <SubmissionDetails v-if="selectedSubmission" v-model:submission-id="selectedSubmission" :event-id="route.params.id" />
      <div v-else class="w-full h-svh flex items-center justify-center text-base text-ink-gray-5">
        Select a submission to view details.
      </div>
    </div>
    <SubmissionDrawer v-else v-model:show="showDrawer" :submission-id="selectedSubmission" :event-id="route.params.id" />
  </div>
</template>
