<script setup>
import InsightsGrid from '@/components/event/cfp/InsightsGrid.vue'
import SubmissionsList from '@/components/event/cfp/SubmissionsList.vue'
import SubmissionDrawer from '@/components/event/cfp/SubmissionDrawer.vue'
import { createListResource, createResource, LoadingIndicator } from 'frappe-ui'
import { ref, reactive, inject } from 'vue'
import { useRoute } from 'vue-router'

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
  selectedSubmission.value = submission.name
  showDrawer.value = true
}
</script>

<template>
  <div class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <Suspense>
      <InsightsGrid />
    </Suspense>
    <Suspense>
      <SubmissionsList @open:submission="handleOpenSubmission($event)"></SubmissionsList>
      <template #fallback>
        <LoadingIndicator class="w-5 h-5" />
      </template>
    </Suspense>
  </div>
  <SubmissionDrawer
    v-model:show="showDrawer"
    :submission-id="selectedSubmission"
  ></SubmissionDrawer>
</template>
