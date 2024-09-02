<template>
  <Header />
  <div v-if="event.loading" class="mb-8">
    <LoadingText class="text-lg" text="Loading Proposals..." />
  </div>
  <div v-else class="container mx-auto px-4">
    <!-- Back button -->
    <Breadcrumb class="mt-2" :items="breadcrumb_items" />
    <EventHeader
      :event="event.data"
      class="my-4 border-b border-gray-900 pb-4"
    />

    <div v-if="cfp.data && proposals.data && proposalLikes.data">
      <AllProposalsBanner :event="event.data" :cfp="cfp.data" />

      <!-- Search and filters -->
      <div class="flex flex-col gap-y-3 justify-between mb-6 md:flex-row">
        <div class="md:w-1/2">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by proposal title"
            class="w-full px-4 py-2 border rounded-sm bg-gray-300"
          />
        </div>
        <div class="flex gap-x-2 items-center">
          <div class="relative w-40">
            <button
              @click="toggleSessionTypeDropdown"
              class="px-4 py-2 flex gap-x-1 justify-between items-center border rounded-sm bg-gray-800 text-white w-40"
            >
              <p>{{ selectedSessionType || 'Session Type' }}</p>
              <ChevronDown />
            </button>
            <div
              v-if="showSessionTypeDropdown"
              class="absolute z-10 mt-1 w-full bg-white border rounded-sm shadow-lg"
            >
              <div
                v-for="type in sessionTypes"
                :key="type"
                @click="selectSessionType(type)"
                class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
              >
                {{ type }}
              </div>
            </div>
          </div>
          <div class="relative w-40">
            <button
              @click="toggleStatusDropdown"
              class="px-4 py-2 flex gap-x-1 justify-between items-center border rounded-sm bg-gray-800 text-white w-40"
            >
              <p>{{ selectedStatus || 'Status' }}</p>
              <ChevronDown />
            </button>
            <div
              v-if="showStatusDropdown"
              class="absolute z-10 mt-1 w-full bg-white border rounded-sm shadow-lg"
            >
              <div
                v-for="status in statuses"
                :key="status"
                @click="selectStatus(status)"
                class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
              >
                {{ status }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Talk proposals list -->
      <div class="space-y-4">
        <div v-if="filteredProposals.length != 0"
          v-for="(proposal, index) in filteredProposals"
          :key="index"
          class="border-b-2 py-4"
        >
          <ProposalBlock
            :proposal="proposal"
            :proposalLikes="proposalLikes.data[proposal.name]"
          />
        </div>
        <div v-else>
          <h3>No proposals</h3>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { createResource, usePageMeta, LoadingText } from 'frappe-ui'
import { redirectRouteToSameWindow } from '@/helpers/utils'
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import AllProposalsBanner from '../../components/proposals/AllProposalsBanner.vue'
import ProposalBlock from '../../components/proposals/ProposalBlock.vue'
import EventHeader from '../../components/schedule/EventHeader.vue'
import ChevronDown from '../../components/icons/ChevronDown.vue'

const route = useRoute()
const eventPermalink = route.params.permalink

const event = createResource({
  url: 'fossunited.api.dashboard.get_event_from_permalink',
  params: {
    permalink: eventPermalink,
    fields: [
      'chapter',
      'chapter_name',
      'event_name',
      'event_start_date',
      'event_end_date',
      'event_location',
      'event_bio',
      'is_external_event',
      'external_event_url',
      'event_logo',
      'route',
    ],
  },
  auto: true,
  onSuccess() {
    cfp.fetch()
    proposals.fetch()
  },
})

const cfp = createResource({
  url: 'fossunited.api.dashboard.get_cfp_details_from_eventname',
  makeParams() {
    return {
      eventname: event.data.event_name,
      fields: ['route', 'proposal_page_description'],
    }
  },
})


const proposals = createResource({
  url: 'fossunited.api.dashboard.get_proposal_list_from_eventname',
  makeParams() {
    return {
      eventname: event.data.event_name,
      fields: [
        'name',
        'route',
        'talk_title',
        'session_type',
        'full_name',
        'status',
      ],
    }
  },
  auto: false,
  onSuccess(data) {
    console.log(data)
    proposalLikes.fetch()
  },
})

usePageMeta(() => ({
  title: event.data
    ? `${event.data.event_name} | Proposals`
    : 'Loading Proposals...',
}))

const breadcrumb_items = computed(() => {
  if (!event.data) return []
  return [
    {
      label: event.data.event_name,
      link: event.data.is_external_event
        ? event.data.external_event_url
        : redirectRouteToSameWindow(event.data.route),
    },
    {
      label: 'All Proposals',
    },
  ]
})

const proposalLikes = createResource({
  url: 'fossunited.api.proposal.get_likes',
  makeParams() {
    const proposalIDs = proposals.data?.map((proposal) => proposal.name) || []
    return {
      proposals: proposalIDs,
    }
  },
})

const searchQuery = ref('')

const selectedSessionType = ref('')
const selectedStatus = ref('')
const showSessionTypeDropdown = ref(false)
const showStatusDropdown = ref(false)

// Define session types and statuses
// : TODO - this can be dynamic again - fetch session types from backend
const sessionTypes = ['Talk', 'Lightning Talk', 'Workshop', 'Panel', 'All']
const statuses = ['Approved', 'Rejected', 'Screening', 'All']

// Toggle functions for dropdowns
const toggleSessionTypeDropdown = () => {
  showSessionTypeDropdown.value = !showSessionTypeDropdown.value
  showStatusDropdown.value = false
}

const toggleStatusDropdown = () => {
  showStatusDropdown.value = !showStatusDropdown.value
  showSessionTypeDropdown.value = false
}

// Selection functions for dropdowns
const selectSessionType = (type) => {
  selectedSessionType.value = type === 'All' ? '' : type
  showSessionTypeDropdown.value = false
}

const selectStatus = (status) => {
  selectedStatus.value = status === 'All' ? '' : status
  showStatusDropdown.value = false
}

// Computed function for monitoring search-filter
const filteredProposals = computed(() => {
  if (!proposals.data) return []

  return proposals.data.filter((proposal) => {
    const matchesSearch = proposal.talk_title
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase())
    const matchesSessionType =
      !selectedSessionType.value ||
      proposal.session_type === selectedSessionType.value
    const matchesStatus =
      !selectedStatus.value || proposal.status === selectedStatus.value

    return matchesSearch && matchesSessionType && matchesStatus
  })
})
</script>
