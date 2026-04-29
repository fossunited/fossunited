<template>
  <div class="flex flex-col md:flex-row">
    <Sidebar :menu-items="sidebarMenuItems" />
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
          <div class="flex items-center justify-between mt-1">
            <span class="text-sm text-ink-gray-6">
              {{ dayjs(event.data.event_start_date).format('D MMM YYYY') }}
            </span>
            <Button
              :label="viewMode === 'grid' ? 'List View' : 'Grid View'"
              @click="viewMode = viewMode === 'grid' ? 'list' : 'grid'"
              variant="outline"
              size="sm"
            />
          </div>
          <div v-if="currentEventStats && currentEventStats.submission_count > 0" class="mt-4">
            <div class="w-full bg-surface-gray-2 rounded-full h-2">
              <div class="bg-surface-gray-7 h-2 rounded-full transition-all duration-500" :style="{ width: (currentEventStats.reviewed_count / currentEventStats.submission_count * 100) + '%' }"></div>
            </div>
            <div class="text-xs text-ink-gray-5 mt-1">Review progress: {{ currentEventStats.reviewed_count }} / {{ currentEventStats.submission_count }}</div>
          </div>
          <div v-if="currentEventStats?.active_phase" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
            <div class="font-medium mb-1">Active Phase: {{ currentEventStats.active_phase.name }}</div>
            <ul class="list-disc list-inside opacity-90">
              <li v-if="currentEventStats.active_phase.proposal_visibility === 'Only Assigned'">You can only see proposals assigned to you.</li>
              <li v-else>You can see all proposals.</li>
              <li v-if="currentEventStats.active_phase.can_see_other_reviews === 'After Review'">You will see other reviews after submitting your own.</li>
              <li v-else-if="currentEventStats.active_phase.can_see_other_reviews === 'Never'">You cannot see other reviews.</li>
              <li v-else>You can see all other reviews.</li>
            </ul>
          </div>
        </div>
        
        <div v-if="viewMode === 'grid'" class="mt-6">
          <ReviewGrid :event="route.params.id" />
        </div>
        <Suspense v-else>
          <ProposalList ref="proposalListRef" :key="`${route.params.id}-${reloadReviewed}`" :event="route.params.id" @open:submission="handleOpenSubmission($event)" />
          <template #fallback>
            <LoadingIndicator class="w-4 h-4 place-self-center" />
          </template>
        </Suspense>
      </div>
      <div v-if="!isSmallScreen && viewMode === 'list'" class="flex w-full basis-3/5 shrink-0">
        <ProposalDetails v-if="selectedSubmission" :key="selectedSubmission" v-model:submission-id="selectedSubmission" @review:submitted="reloadReviewed++" @next="goToNextSubmission" />
        <div v-else class="w-full h-svh flex items-center justify-center text-base text-ink-gray-5">
          Select a submission to view details.
        </div>
      </div>
      <ProposalDetailsDrawer
        v-else-if="viewMode === 'list'"
        v-model:show="showDrawer"
        :submission-id="selectedSubmission"
      ></ProposalDetailsDrawer>
    </div>
  </div>
</template>
<script setup>
import { createResource, usePageMeta, LoadingIndicator } from 'frappe-ui'
import { computed, ref, watch, provide } from 'vue'
import { useRoute } from 'vue-router'
import { isSmallScreen } from '@/helpers/utils'
import ProposalDetailsDrawer from '@/components/reviewers/ProposalDetailsDrawer.vue'
import ProposalList from '@/components/reviewers/ProposalsList.vue'
import ReviewGrid from '@/components/reviewers/ReviewGrid.vue'
import Sidebar from '@/components/NewAppSidebar.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import ProposalDetails from '@/components/reviewers/ProposalDetails.vue'
import dayjs from 'dayjs'

const route = useRoute()

// 1. State Refs
const viewMode = ref('list')
const reloadReviewed = ref(0)
const selectedSubmission = ref('')
const showDrawer = ref(false)
const proposalListRef = ref(null)
const breadcrumbItems = ref([
  {
    label: 'CFP Review',
    route: '/review',
  },
])

// 2. Resource Definitions (Must come before any code that uses them)
const eventCategories = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    const cfpId = allCfpEvents.data?.find((e) => e.event === route.params.id)?.cfp
    return {
      doctype: 'CFP Score Category',
      filters: { event_cfp: cfpId, active: 1 },
      fields: ['*'],
      limit: 99,
    }
  },
})

const allCfpEvents = createResource({
  url: 'fossunited.api.reviewer.get_events_by_open_cfp',
  auto: true,
  onSuccess() {
    eventCategories.fetch()
  }
})

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

// 3. Computed Properties
const currentEventStats = computed(() => {
  return allCfpEvents.data?.find((e) => e.event === route.params.id)
})

const sidebarMenuItems = computed(() => {
  const items = [
    {
      items: [{ icon: 'arrow-left', label: 'Go Back', route: '/review' }],
    },
  ]

  if (allCfpEvents.data?.length) {
    items.push({
      parent_label: 'Open CFPs',
      items: allCfpEvents.data.map((e) => ({
        label: e.event_name,
        route: `/review/${e.event}`,
      })),
    })
  }

  return items
})

// 4. Injections / Provides
provide('currentEventStats', currentEventStats)
provide('eventCategories', eventCategories)

// 5. Action Handlers
const handleOpenSubmission = (submission) => {
  selectedSubmission.value = submission

  if (isSmallScreen.value) {
    showDrawer.value = true
  }
}

const goToNextSubmission = () => {
  const nextId = proposalListRef.value?.getNextSubmission(selectedSubmission.value)
  if (nextId) {
    selectedSubmission.value = nextId
  }
}

// 6. Watches
watch(
  () => route.params.id,
  () => {
    selectedSubmission.value = ''
    showDrawer.value = false
    breadcrumbItems.value = [{ label: 'CFP Review', route: '/review' }]
    event.reload()
  },
)

// 7. Page Metadata
usePageMeta(() => {
  return {
    title: `Review | ${event.data?.event_name}`,
  }
})
</script>
