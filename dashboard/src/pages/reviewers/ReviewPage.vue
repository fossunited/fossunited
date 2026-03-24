<template>
  <div class="flex flex-col md:flex-row">
    <Sidebar>
      <template #pre-nav-items>
        <Button
          class="w-fit"
          label="Go Back"
          icon-left="arrow-left"
          variant="ghost"
          route="/review"
        />
        <h4 class="text-sm uppercase font-medium text-ink-gray-6">Proposal Review</h4>
        <p class="text-sm text-ink-gray-5">Review the session proposals for this event.</p>
      </template>
    </Sidebar>
    <div class="flex-1 min-w-0 flex">
      <div
        v-if="event.data"
        class="w-full shrink-0 md:basis-2/5 p-6 border-r space-y-6 md:overflow-y-scroll max-h-svh"
      >
        <div>
          <Breadcrumb :items="breadcrumbItems" />
          <div class="prose">
            <h2>{{ event.data.event_name }}</h2>
          </div>
          <span class="text-sm text-ink-gray-6">
            {{ dayjs(event.data.event_start_date).format('D MMM YYYY') }}
          </span>
        </div>
        <Suspense>
          <ProposalList :event="event.data.name" @open:submission="handleOpenSubmission($event)" />
          <template #fallback>
            <LoadingIndicator class="w-4 h-4 place-self-center" />
          </template>
        </Suspense>
      </div>
      <div v-if="!isSmallScreen" class="flex w-full basis-3/5 shrink-0">
        <ProposalDetails v-if="selectedSubmission" v-model:submission-id="selectedSubmission" />
        <div v-else class="w-full h-svh flex items-center justify-center text-base text-ink-gray-5">
          Select a submission to view details.
        </div>
      </div>
      <ProposalDetailsDrawer
        v-else
        v-model:show="showDrawer"
        :submission-id="selectedSubmission"
      ></ProposalDetailsDrawer>
    </div>
  </div>
</template>
<script setup>
import { createResource, usePageMeta, LoadingIndicator } from 'frappe-ui'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import ProposalDetailsDrawer from '@/components/reviewers/ProposalDetailsDrawer.vue'
import ProposalList from '@/components/reviewers/ProposalsList.vue'
import Sidebar from '@/components/NewAppSidebar.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import ProposalDetails from '@/components/reviewers/ProposalDetails.vue'
import dayjs from 'dayjs'

const route = useRoute()

const selectedSubmission = ref('')
const showDrawer = ref(false)

const isSmallScreen = computed(() => window.innerWidth < 768)

const handleOpenSubmission = (submission) => {
  selectedSubmission.value = submission

  if (isSmallScreen.value) {
    showDrawer.value = true
  }
}

const event = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Chapter Event',
      filters: {
        name: route.params.id,
      },
      fields: ['name', 'event_name', 'route', 'event_start_date', 'event_end_date'],
    }
  },
  auto: true,
  onSuccess(data) {
    breadcrumbItems.value.push({
      label: data.event_name,
      link: `${window.location.origin}/${data.route}`,
    })
  },
})

const breadcrumbItems = ref([
  {
    label: 'CFP Review',
    route: '/review',
  },
])

usePageMeta(() => {
  return {
    title: `Review | ${event.data?.event_name}`,
  }
})
</script>
