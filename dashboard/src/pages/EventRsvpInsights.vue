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
        <Button size="md" icon-left="download" @click="downloadAttendeeList">Download</Button>
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
      >
        <template #cell="{ item }">
          <span>
            {{ truncate(item, 30) }}
          </span>
        </template>
      </ListView>
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

const all_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event RSVP Submission',
    fields: ['*'],
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
  },
  auto: true,
})

function truncate(text, length = 20) {
  return text?.length > length ? text.slice(0, length) + '…' : text || ''
}

const listColumns = computed(() => {
  const baseKeys = ['name1', 'email', 'im_a']
  const columns = baseKeys.map((key) => {
    const labelMap = { name1: 'Name', email: 'Email', im_a: 'I am a' }
    return {
      label: labelMap[key] || key,
      key,
    }
  })

  if (isEventLead.value && Array.isArray(submissions.data)) {
    const customFields = new Set()

    submissions.data.forEach((submission) => {
      Object.keys(submission).forEach((key) => {
        // Exclude base keys AND 'name' (internal doctype name)
        if (!baseKeys.includes(key) && key !== 'name') {
          customFields.add(key)
        }
      })
    })

    Array.from(customFields)
      .sort()
      .forEach((question) => {
        columns.push({
          label: question.length > 40 ? question.slice(0, 40) + '…' : question,
          key: question,
        })
      })
  }

  return columns
})

const downloadAttendeeList = () => {
  if (!Array.isArray(submissions.data)) return

  const columns = listColumns.value

  // Build header row using column labels
  const headers = columns.map((col) => col.label)
  const csvRows = [headers.join(',')]

  // Build each row using column keys
  submissions.data.forEach((submission) => {
    const row = columns.map(({ key }) => {
      const val = submission[key]
      if (typeof val === 'string' || typeof val === 'number') {
        return `"${val}"`
      }
      if (typeof val === 'object' && val?.answer) {
        return `"${val.answer}"`
      }
      return ''
    })

    csvRows.push(row.join(','))
  })

  // Download the CSV
  const csv = csvRows.join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `Attendee List - ${rsvp_form.data.event_name} - ${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
