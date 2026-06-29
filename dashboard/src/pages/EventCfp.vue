<template>
  <div v-if="event.doc" class="w-full z-0 min-h-screen">
    <div class="flex gap-3 items-end px-4 py-8 md:p-8">
      <EventHeader
        class=""
        :event="event.doc"
        :form-exists="Boolean(hasCfp.data)"
        :form="eventCfp"
      />
    </div>
    <TabsWithRoute :tabs="tabs.options" />
    <RouterView :event-cfp="eventCfp" @cfp-created="cfpCreated" />
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

const cfpBase = `/event/${route.params.id}/cfp`

const tabs = reactive({ options: [] })

const hasCfp = createResource({
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
    const exists = data > 0
    if (exists) {
      eventCfp.fetch()
      tabs.options = [
        { label: 'Web Form', route: `${cfpBase}/edit` },
        { label: 'Insights', route: `${cfpBase}/insights` },
      ]
    } else {
      tabs.options = [{ label: 'Web Form', route: `${cfpBase}/create` }]
    }
    // Web Form is the default landing: redirect the bare /cfp path to edit or create.
    if (route.path === cfpBase || route.path === `${cfpBase}/`) {
      router.replace(exists ? `${cfpBase}/edit` : `${cfpBase}/create`)
    }
  },
})

const eventCfp = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event CFP',
    filters: {
      event: route.params.id,
    },
  },
})

const cfpCreated = () => {
  hasCfp.fetch()
  router.replace(`${cfpBase}/edit`)
}
</script>
