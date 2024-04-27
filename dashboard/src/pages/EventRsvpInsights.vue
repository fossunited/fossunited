<template>
  <div
    v-if="submissions.data && rsvp_form.data"
    class="px-4 py-8 md:p-8 flex flex-col gap-4"
  >
    <div class="flex flex-col gap-4 mt-5">
      <div class="flex items-center justify-between">
        <div class="font-semibold text-gray-800">
          Attendees

          <span class="text-gray-700 text-base font-normal"
            >({{ submissions.data.length }}/{{
              rsvp_form.data.max_rsvp_count
            }})</span
          >
        </div>
        <Button size="md" icon-left="download" @click="downloadAttendeeList"
          >Download</Button
        >
      </div>
      <ListView
        :columns="[
          { label: 'Name', key: 'name1' },
          { label: 'Email', key: 'submitted_by' },
          { label: 'I am a', key: 'im_a' },
        ]"
        :rows="submissions.data"
        row-key="name"
        :options="{
          selectable: false,
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
import { createListResource, createResource, ListView, Button } from 'frappe-ui'

const route = useRoute()

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

const submissions = createListResource({
  doctype: 'FOSS Event RSVP Submission',
  fields: ['*'],
  filters: {
    event: route.params.id,
  },
  pageLength: 99999,
  auto: true,
  transform(data) {
    data.forEach((submission) => {
      submission.submitted_by = submission.submitted_by.replace(
        /(?<=.{3}).(?=[^@]*?@)/g,
        '*',
      )
    })
  },
})

const downloadAttendeeList = () => {
  const csv = submissions.data
    .map((submission) => {
      return [submission.name1, submission.submitted_by, submission.im_a].join(
        ',',
      )
    })
    .join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `Attendee List-${rsvp_form.data.event_name}-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
