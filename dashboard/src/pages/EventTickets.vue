<template>
  <div v-if="event.data" class="w-full z-0">
    <EventHeader :event="event.doc" v-if="event.doc" class="p-4 md:p-8" />
    <TabsWithRoute :tabs="tabs" />
    <RouterView class="p-4 md:p-8" :event="event" />
  </div>
  <div v-else class="w-full h-[220px] flex items-center justify-center">
    <LoadingIndicator class="w-5 h-5" />
  </div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import TabsWithRoute from '@/components/TabsWithRoute.vue'
import { createResource, LoadingIndicator } from 'frappe-ui'
import { useRoute } from 'vue-router'

const route = useRoute()

const event = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Chapter Event',
      name: route.params.id,
      fields: ['*'],
    }
  },
  onSuccess(data) {
    event.doc = data
  },
  auto: true,
})

const tabs = [
  {
    label: 'Manage',
    route: `/event/${route.params.id}/tickets`,
  },
  {
    label: 'Insights',
    route: `/event/${route.params.id}/tickets/insights`,
  },
]
</script>
