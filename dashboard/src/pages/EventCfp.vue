<template>
  <div v-if="event.doc" class="w-full z-0 min-h-screen">
    <div class="flex gap-3 items-end px-4 py-8 md:p-8">
      <EventHeader
        class=""
        :event="event"
        :form_exists="new Boolean(has_cfp.data)"
        :form="event_cfp"
      />
    </div>
    <TabsWithRoute :tabs="tabs.options" />
    <RouterView @cfp-created="cfpCreated" :event_cfp="event_cfp" />
  </div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import { createDocumentResource, createResource, Badge } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import TabsWithRoute from '@/components/TabsWithRoute.vue'
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
      route: `/event/${route.params.id}/cfp`,
    },
  ],
})

const has_cfp = createResource({
  url: 'frappe.client.get_count',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP',
      filters: {
        event: route.params.id,
      },
    }
  },
  auto: true,
  onSuccess(data) {
    resetTabs()
    if (data > 0) {
      event_cfp.fetch()
      tabs.options.push(...[
        {
          label: 'Web Form',
          route: `/event/${route.params.id}/cfp/edit`,
        },
        {
          label: 'Insights',
          route: `/event/${route.params.id}/cfp/insights`,
        },
      ])
      return
    }
    tabs.options.push({
      label: 'Web Form',
      route: `/event/${route.params.id}/cfp/create`,
    })
  },
})

const event_cfp = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event CFP',
    filters: {
      event: route.params.id,
    },
  },
})

const resetTabs = () => {
  tabs.options = [
    {
      label: 'Overview',
      route: `/event/${route.params.id}/cfp`,
    },
  ]
}

const cfpCreated = () => {
  has_cfp.fetch()
  router.replace(`/event/${route.params.id}/cfp`)
}
</script>
