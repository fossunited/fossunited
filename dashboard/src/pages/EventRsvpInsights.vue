<template>
  <div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-col gap-4 mt-5">
      <div class="flex items-center justify-between">
        <div class="font-semibold text-gray-800">Attendees</div>
        <Button size="md" icon-left="download" @click="downloadAttendeeList2">Download</Button>
      </div>

      <ListView
        v-model:rows="groupedRows"
        :columns="listColumns"
        row-key="name"
        :options="{
          selectable: false,
          showTooltip: true,
          resizeColumn: true,
          emptyState: {
            description: 'No one has RSVPed for the event yet.',
          },
        }"
      >
        <template #group-header="{ group }">
          <span class="text-base font-medium leading-6 text-ink-gray-9">
            {{ group.group }} ({{ group.rows.length }})
          </span>
        </template>
      </ListView>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { inject, ref, computed, watchEffect } from 'vue'
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
  url: 'fossunited.api.chapter.check_if_chapter_or_event_core_member',
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
    answers: false,
  },
  auto: true,
})

const listColumns = computed(() => {
  const columns = new Map()

  // Collect keys from all submissions
  if (Array.isArray(submissions.data)) {
    submissions.data.forEach((submission) => {
      Object.keys(submission).forEach((key) => {
        if (key !== 'confirm_attendance' && !columns.has(key)) {
          columns.set(key, { key, label: key }) // Use key as label directly
        }
      })
    })
  }

  return Array.from(columns.values())
})

const groupedRows = ref([])

watchEffect(() => {
  const attending = []
  const notAttending = []

  for (const row of submissions.data) {
    if (row.confirm_attendance) {
      attending.push(row)
    } else {
      notAttending.push(row)
    }
  }

  groupedRows.value = [
    {
      group: 'Attending event',
      collapsed: false,
      rows: attending,
    },
    {
      group: 'Not attending',
      collapsed: true,
      rows: notAttending,
    },
  ]
})

const downloadAttendeeList2 = () => {
  const eventId = route.params.id
  window.open(
    `/api/method/fossunited.api.chapter.download_attendee_list_csv?event_id=${eventId}`,
    '_self',
  )
}
</script>
