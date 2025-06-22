<script setup>
import NarrowLayout from '@/layout/desktop/NarrowLayout.vue'
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import EventHeader from '@/components/common/EventHeader.vue'
import ProposalLogo from '@/components/cfp-public/ProposalLogo.vue'
import SubmissionsListView from '@/components/cfp-public/SubmissionsListView.vue'
import { createResource, LoadingIndicator, usePageMeta } from 'frappe-ui'
import { cleanedHTML } from '@/helpers/utils'
import { useRoute } from 'vue-router'
import { ref } from 'vue'
import FormCard from '../../components/cfp-public/FormCard.vue'
import InsightsGrid from '../../components/event/cfp/InsightsGrid.vue'

const route = useRoute()

const cfpData = createResource({
  url: 'fossunited.api.cfp.get_cfp_from_route',
  makeParams() {
    return {
      route: route.params.route,
    }
  },
  auto: true,
  onSuccess(data) {
    submissions.fetch()
    breadcrumb_items.value[1].label = data.event_name
  },
})

const submissions = createResource({
  url: 'fossunited.api.proposal.get_event_proposals',
  makeParams() {
    return {
      event: cfpData.data.event.name,
    }
  },
})

const breadcrumb_items = ref([
  {
    label: 'Events',
    link: '/events',
  },
  {
    label: cfpData.data?.event_name,
    link: `/c/${route.params.route}`,
  },
  {
    label: 'Talk Proposals',
  },
])

usePageMeta(() => {
  return {
    title: 'All Proposals | ' + cfpData.data?.event_name,
  }
})
</script>
<template>
  <Header></Header>
  <Suspense>
    <NarrowLayout v-if="submissions.data">
      <Breadcrumb :items="breadcrumb_items" />
      <div class="w-full space-y-4">
        <h1 class="text-3xl font-bold">Talk Proposals</h1>
        <EventHeader :event="cfpData.data.event">
          <template #logo>
            <ProposalLogo></ProposalLogo>
          </template>
          <template #description>
            <div
              class="prose prose-sm prose-h1:text-xl prose-h2:text-xl prose-h3:text-lg prose-h4:text-base prose-h5:text-sm prose-h1:font-semibold prose-h2:font-semibold prose-h3:font-semibold prose-h4:font-medium prose-h5:font-medium max-w-full"
              v-html="cleanedHTML(cfpData.data.event.event_description)"
            ></div>
          </template>
        </EventHeader>
      </div>
      <FormCard :cfp="cfpData.data" />
      <InsightsGrid :event-id="cfpData.data.event.name" />
      <SubmissionsListView :event-id="cfpData.data.event.name" />
    </NarrowLayout>
    <template #fallback>
      <LoadingIndicator class="w-5 h-5" />
    </template>
  </Suspense>
</template>
