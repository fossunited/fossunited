<template>
  <Header />
  <div v-if="event.loading" class="mb-8">
    <p>Loading event details...</p>
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
            type="text"
            placeholder="Search"
            class="w-full px-4 py-2 border rounded-sm bg-gray-300"
          />
        </div>
        <div class="flex gap-x-2 items-center">
          <div
            class="px-4 py-2 flex gap-x-1 items-center border rounded-sm bg-gray-800 text-white"
          >
            <p>Session Type</p>
            <ChevronDown />

            <!-- <select class="hidden">
            <option>Session Type</option>
            <option>Talk</option>
          </select> -->
          </div>

          <div
            class="px-4 py-2 flex gap-x-1 items-center border rounded-sm bg-gray-800 text-white"
          >
            <p>Status</p>
            <ChevronDown />
            <!-- <select>
            <option>Session Type</option>
            <option>Talk</option>
          </select> -->
          </div>
        </div>
      </div>

      <!-- Talk proposals list -->
      <div class="space-y-4">
        <div
          v-for="(proposal, index) in proposals.data"
          :key="index"
          class="border-b-2 py-4"
        >
          <div class="flex justify-between items-start">
            <div class="flex flex-col gap-y-3.5">
              <h3 class="text-xl font-semibold">
                <a
                  @click.prevent="
                    redirectRouteToSameWindow(`${proposal.route}`)
                  "
                  class="hover:text-green-500 transition-colors duration-300 cursor-pointer"
                >
                  {{ proposal.talk_title }}
                </a>
              </h3>
              <div
                class="flex flex-col gap-y-3.5 items-start mt-1 md:flex-row md:items-center"
              >
                <div class="flex items-center text-xs font-semibold">
                  <span
                    class="bg-gray-200 px-2 py-1 text-gray-600 rounded-sm mr-2"
                    >{{ proposal.session_type.toUpperCase() }}</span
                  >
                  <div>
                    <span
                      class="px-2 py-1 rounded-sm md:hidden"
                      :class="getStatusClass(proposal.status)"
                      >{{ proposal.status.toUpperCase() }}</span
                    >
                  </div>
                </div>
                <div v-if="proposal.status == `Approved`" class="flex text-sm">
                  <SpeakerIcon />
                  <span>
                    {{ proposal.full_name }}
                  </span>
                </div>
              </div>
            </div>
            <div class="flex flex-col gap-y-3.5 items-end">
              <div
                class="flex items-center gap-1 bg-gray-200 px-1.5 py-1 rounded-sm"
              >
                <LikesIcon />
                <span class="text-xs font-semibold">{{
                  proposalLikes.data[proposal.name]
                }}</span>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { createResource, createListResource, usePageMeta } from 'frappe-ui'
import { redirectRouteToSameWindow } from '@/helpers/utils'
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import SpeakerIcon from '../../components/icons/SpeakerIcon.vue'
import LikesIcon from '../../components/icons/LikesIcon.vue'
import AllProposalsBanner from '../../components/proposals/AllProposalsBanner.vue'
import EventHeader from '../../components/schedule/EventHeader.vue'
import ChevronDown from '../../components/icons/ChevronDown.vue'

const route = useRoute()
const eventPermalink = route.params.permalink

const event = createResource({
  url: 'frappe.client.get_value',
  params: {
    doctype: 'FOSS Chapter Event',
    filters: { event_permalink: eventPermalink },
    fieldname: [
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
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP',
      filters: { event_name: event.data.event_name },
      fieldname: ['route', 'proposal_page_description'],
    }
  },
})

const proposals = createListResource({
  doctype: 'FOSS Event CFP Submission',
  makeFilters() {
    return {
      event_name: event.data.event_name,
    }
  },
  fields: [
    'name',
    'route',
    'talk_title',
    'session_type',
    'full_name',
    'status',
  ],
  auto: false,
  onSuccess() {
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

const proposalLikes = createResource({
  url: 'fossunited.api.proposal.get_likes',
  makeParams() {
    const proposalIDs = proposals.data?.map((proposal) => proposal.name) || []
    return {
      proposals: proposalIDs,
    }
  },
})
</script>
