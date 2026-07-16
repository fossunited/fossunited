<template>
  <div v-if="event.doc" class="w-full z-0 min-h-screen">
    <EventHeader
      class="px-4 py-8 md:p-8"
      :event="event.doc"
      :form-exists="Boolean(has_rsvp.data)"
      :form="event_rsvp"
    />
    <DocsInfo
      class="ml-4"
      message="Please find docs for knowing how RSVP works"
      docs-url="https://docs.fossunited.org/event-rsvp"
    />

    <TabsWithRoute :tabs="tabs.options" />

    <RouterView :event_rsvp="event_rsvp" @rsvp-created="rsvpCreated" />
  </div>
</template>
<script setup>
import TabsWithRoute from '@/components/TabsWithRoute.vue'
import EventHeader from '@/components/EventHeader.vue'
import { createDocumentResource, createResource } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import { reactive, ref, watch } from 'vue'
import DocsInfo from '@/components/DocsInfo.vue'

const route = useRoute()
const router = useRouter()

const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const rsvpBase = `/event/${route.params.id}/rsvp`

const tabs = reactive({ options: [] })

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
    const exists = data > 0
    if (exists) {
      event_rsvp.fetch()
      tabs.options = [
        { label: 'Web Form', route: `${rsvpBase}/edit` },
        { label: 'Insights', route: `${rsvpBase}/insights` },
      ]
    } else {
      tabs.options = [{ label: 'Web Form', route: `${rsvpBase}/create` }]
    }
    // Web Form is the default landing: redirect the bare /rsvp path to edit or create.
    if (route.path === rsvpBase || route.path === `${rsvpBase}/`) {
      router.replace(exists ? `${rsvpBase}/edit` : `${rsvpBase}/create`)
    }
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

const rsvpCreated = () => {
  has_rsvp.fetch()
  router.replace(`${rsvpBase}/edit`)
}
</script>
