<template>
  <Header />
  <div class="container mx-auto px-4">
    <!-- Back button -->
    <Breadcrumb
      v-if="event.data"
      class="flex gap-1 items-center mt-2"
      :items="breadcrumb_items"
    />

    <!-- Banner -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex flex-col gap-y-4 lg:w-3/4">
        <div v-if="event.data" class="flex flex-col gap-y-2">
          <h3 class="font-semibold text-gray-600">
            {{ event.data.event_name }}
          </h3>
          <p class="text-sm font-medium">
            {{ event.data.event_location }} |
            <span
              v-if="
                dayjs(event.event_start_date).date() !=
                dayjs(event.event_end_date).date()
              "
            >
              {{ dayjs(event.event_start_date).format('Do') }} -
            </span>
            <span>{{ dayjs(event.event_end_date).format('Do MMM YYYY') }}</span>
          </p>
        </div>

        <!-- Loading state -->
        <div v-else-if="event.loading" class="mb-8">
          <p>Loading event details...</p>
        </div>

        <!-- Talk Proposals section -->
        <div class="flex flex-col gap-y-2">
          <h1 class="text-3xl font-semibold">Talk Proposals</h1>
          <p class="text-gray-700 font-semibold">
            <span v-if="cfp.data?.proposal_page_description">
              {{ cfp.data.proposal_page_description }}
            </span>

            <span v-else-if="event.data?.event_name">
              Explore the proposals for {{ event.data.event_name }}, that offers
              a wide array of sessions.
            </span>
          </p>
        </div>
      </div>
      <AllProposalsBannerImage class="hidden md:block" />
    </div>

    <!-- Search and filters -->
    <div class="flex flex-col gap-y-3 justify-between mb-6 md:flex-row">
      <div class="md:w-1/2">
        <input
          type="text"
          placeholder="Search"
          class="w-full px-4 py-2 border rounded-sm bg-gray-300"
        />
      </div>
      <div class="space-x-2">
        <select class="px-4 py-2 border rounded-sm bg-gray-800 text-white">
          <option>Session Type</option>
        </select>
        <select class="px-4 py-2 border rounded-sm bg-gray-800 text-white">
          <option>Status</option>
        </select>
      </div>
    </div>

    <!-- Talk proposals list -->
    <div v-if="proposals.data && proposalLikes.data" class="space-y-4">
      <div
        v-for="(proposal, index) in proposals.data"
        :key="index"
        class="border-b-2 py-4"
      >
        <div class="flex justify-between items-start">
          <div class="flex flex-col gap-y-3.5">
            <h3 class="text-xl font-semibold">
              {{ proposal.talk_title }}
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
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { createResource, createListResource, usePageMeta } from 'frappe-ui'
import dayjs from 'dayjs'
import advancedFormat from 'dayjs/plugin/advancedFormat'
import { redirectRouteToSameWindow } from '@/helpers/utils'
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import AllProposalsBannerImage from '@/components/proposals/AllProposalsBannerImage.vue'
import SpeakerIcon from '../../components/icons/SpeakerIcon.vue'
import LikesIcon from '../../components/icons/LikesIcon.vue'

const route = useRoute()
const eventPermalink = route.params.permalink
dayjs.extend(advancedFormat)

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
