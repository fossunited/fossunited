<template>
  <div v-if="event.doc" class="w-full z-0 min-h-screen">
    <div class="flex gap-3 items-end px-4 py-8 md:p-8">
      <EventHeader
        class=""
        :event="event"
        :form_exists="cfp_exists"
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

let tabs = reactive({
  options: [
    {
      label: 'Overview',
      route: `/event/${route.params.id}/cfp`,
    },
    {
      label: 'Web Form',
      route: `/event/${route.params.id}/cfp/create`,
    },
  ],
})

const replaceCreateOption = () => {
  tabs.options = tabs.options.filter((d) => d.label !== 'Web Form')

    if (!tabs.options.find((d) => d.label === 'Web Form')){
        tabs.options.push({
            label: 'Web Form',
            route: `/event/${route.params.id}/cfp/edit`
        })
    }

    if (!tabs.options.find((d) => d.label === 'Insights')){
        tabs.options.push({
            label: 'Insights',
            route: `/event/${route.params.id}/cfp/insights`
        })
    }
}

let cfp_exists = ref(false)
let event_cfp = reactive({})

watch(event, (newEvent) => {
  event_cfp = createResource({
    url: 'frappe.client.get',
    params: {
      doctype: 'FOSS Event CFP',
      filters: {
        event: newEvent.doc.name,
      },
    },
    auto: true,
    onError(error) {
      if (error.response.status === 404) {
        cfp_exists.value = false
      }
    },
    onSuccess(response) {
      cfp_exists.value = true
    },
  })
  if (cfp_exists.value) {
    replaceCreateOption()
  }
})

const cfpCreated = () => {
  replaceCreateOption()
  router.replace(`/event/${route.params.id}/cfp/edit`)
}
</script>
