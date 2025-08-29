<template>
  <div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-col gap-4 mt-5">
      <div class="flex items-center justify-between">
        <div class="font-semibold text-gray-800">
          Attendees
          <span class="text-gray-700 text-base font-normal">
            ({{ submissions.data.length }}/{{ rsvp_form.data.max_rsvp_count }})
          </span>
        </div>
        <Button size="md" icon-left="download" @click="downloadAttendeeList2">Download</Button>
      </div>

      <ListView
        :columns="listColumns"
        :rows="submissions.data"
        row-key="name"
        :options="{
          selectable: false,
          resizeColumn: true,
          emptyState: {
            description: 'No one has RSVPed for the event yet.',
          },
        }"
      />
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { inject, ref, computed } from 'vue'
import { createListResource, createResource, ListView, Button } from 'frappe-ui'

const route = useRoute()
const session = inject('$session')

const rsvp_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event RSVP',
    fields: ['*'],
    filters: {
      event: route.params.id,
    },
  },
  auto: true,
})

const isEventLead = ref(false)
const event_lead = createResource({
  url: 'fossunited.api.chapter.check_if_event_lead',
  makeParams() {
    return {
      event: route.params.id,
    }
  },
  onSuccess(data) {
    isEventLead.value = data
  },
  auto: true,
})

const submissions = createResource({
  url: 'fossunited.api.chapter.get_submissions_with_answers',
  params: {
    event_id: route.params.id,
    full: false,
  },
  auto: true,
})

const listColumns = computed(() => {
  const baseKeys = ['name1', 'email', 'im_a']
  const columns = baseKeys.map((key) => {
    const labelMap = { name1: 'Name', email: 'Email', im_a: 'I am a' }
    return {
      label: labelMap[key] || key,
      key,
    }
  })

  if (isEventLead.value && Array.isArray(submissions.data) && submissions.data.length > 0) {
    const customFields = new Set()
    const labels = {}
    submissions.data.forEach((submission) => {
      Object.keys(submission).forEach((key) => {
        if (key.startsWith('cf_')) customFields.add(key)
      })
      if (submission._answers) {
        Object.assign(labels, submission._answers)
      }
    })
    Array.from(customFields)
      .sort()
      .forEach((key) => {
        columns.push({ label: labels[key] || key, key })
      })
  }

  return columns
})

const downloadAttendeeList2 = () => {
  const eventId = route.params.id
  window.open(
    `/api/method/fossunited.api.chapter.download_attendee_list_csv?event_id=${eventId}`,
    '_self',
  )
}
</script>
