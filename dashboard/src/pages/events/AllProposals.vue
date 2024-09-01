<template>
  <Header />
  <div class="container mx-auto px-4">
    <!-- Back button -->
    <Breadcrumb
      v-if="event.data"
      class="flex gap-1 items-center mt-2"
      :items="breadcrumb_items"
    />

    <!-- Event header -->
    <div v-if="event.data" class="mb-8">
      <h3>{{ event.data.event_name }}</h3>
      <p class="text-gray-600">
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
    <div class="mb-8">
      <h1>Talk Proposals</h1>
      <p class="text-gray-700 mb-4">
        <span v-if="cfp.data?.proposal_page_description">
          {{ cfp.data.proposal_page_description }}
        </span>

        <span v-else-if="event.data?.event_name">
          Explore the proposals for {{ event.data.event_name }}, that offers a
          wide array of sessions.
        </span>
      </p>
    </div>

    <!-- Search and filters -->
    <div class="flex justify-between mb-6">
      <div class="w-1/2">
        <input
          type="text"
          placeholder="Search"
          class="w-full px-4 py-2 border rounded-md"
        />
      </div>
      <div class="space-x-2">
        <select class="px-4 py-2 border rounded-md bg-gray-800 text-white">
          <option>Session Type</option>
        </select>
        <select class="px-4 py-2 border rounded-md bg-gray-800 text-white">
          <option>Status</option>
        </select>
      </div>
    </div>

    <!-- Talk proposals list -->
    <div v-if="proposals.data && proposalLikes.data" class="space-y-4">
      <div
        v-for="(proposal, index) in proposals.data"
        :key="index"
        class="border rounded-md p-4"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-xl font-semibold">{{ proposal.talk_title }}</h3>
            <div class="text-sm text-gray-600 mt-1">
              <span class="bg-gray-200 px-2 py-1 rounded-md mr-2">{{
                proposal.session_type
              }}</span>
              <span v-if="proposal.status == `Approved`">
                {{ proposal.full_name }}
              </span>
            </div>
          </div>
          <div class="flex items-center">
            <span class="mr-2">{{ proposalLikes.data[proposal.name] }}</span>
            <span class="text-red-500">❤</span>
          </div>
        </div>
        <div class="mt-2">
          <span
            class="px-2 py-1 rounded-md"
            :class="getStatusClass(proposal.status)"
            >{{ proposal.status.toUpperCase() }}</span
          >
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
