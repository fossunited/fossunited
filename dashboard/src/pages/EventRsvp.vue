<template>
  <div v-if="event.doc" class="w-full z-0 min-h-screen">
    <EventHeader
      class="px-4 py-8 md:p-8"
      :event="event.doc"
      :form_exists="Boolean(has_rsvp.data)"
      :form="event_rsvp"
    />
    <TabsWithRoute :tabs="tabs.options" />
    <RouterView
      :event_rsvp="event_rsvp"
      @rsvp-created="rsvpCreated"
    />
  </div>
</template>
<script setup>
import TabsWithRoute from '@/components/TabsWithRoute.vue'
import EventHeader from '@/components/EventHeader.vue'
import { createDocumentResource, createResource } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import { reactive, ref, watch } from 'vue'

const route = useRoute()
const router = useRouter()

const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const tabs = reactive({
  options: [
    {
      label: 'Overview',
      route: `/event/${route.params.id}/rsvp`,
    },
  ],
})

const has_rsvp = createResource({
  url: 'frappe.client.get_count',
  makeParams() {
    return {
      doctype: 'FOSS Event RSVP',
      filters: {
        event: route.params.id,
      },
    }
  },
  auto: true,
  onSuccess(data) {
    resetTabs()
    if (data > 0) {
      event_rsvp.fetch()
      tabs.options.push({
        label: 'Web Form',
        route: `/event/${route.params.id}/rsvp/edit`,
      })
      tabs.options.push({
        label: 'Insights',
        route: `/event/${route.params.id}/rsvp/insights`,
      })
      return
    }
    tabs.options.push({
      label: 'Web Form',
      route: `/event/${route.params.id}/rsvp/create`,
    })
  },
})

const event_rsvp = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Event RSVP',
      filters: {
        event: route.params.id,
      },
    }
  },
})

const resetTabs = () => {
  tabs.options = [
    {
      label: 'Overview',
      route: `/event/${route.params.id}/rsvp`,
    },
  ]
}

const rsvpCreated = () => {
  has_rsvp.fetch()
  router.replace(`/event/${route.params.id}/rsvp`)
}
</script>
