<template>
  <div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <!-- Check-In Section - only visible during event dates -->
    <div v-if="checkedInData.data?.show_checkins" class="flex flex-col gap-4 mt-1">
      <div class="flex items-center justify-between">
        <div class="font-semibold text-gray-800">
          Event Check-Ins
          <span class="ml-2 text-sm font-normal text-gray-600">
            ({{ checkedInData.data.total_checked_in }} attended the event, out of
            {{ checkedInData.data.total_accepted }} confirmed attendees)
          </span>
        </div>
        <div class="flex gap-2">
          <Button size="md" icon-left="download" @click="downloadCheckinCSV"> Download </Button>
          <Button size="md" icon-left="refresh-cw" @click="checkedInData.reload()">
            Refresh
          </Button>
        </div>
      </div>

      <ListView
        v-model:rows="checkedInGroups"
        :columns="checkinColumns"
        row-key="name"
        :options="{
          selectable: false,
          showTooltip: true,
          resizeColumn: true,
          emptyState: {
            description: 'No attendees have checked in yet.',
          },
        }"
      >
        <template #group-header="{ group }">
          <span class="text-base font-medium leading-6 text-ink-gray-9">
            {{ formatDate(group.group) }} - {{ group.rows.length }} check-ins
          </span>
        </template>

        <template #cell="{ item, row, column }">
          <div v-if="column.key === 'check_in_time'">
            <span class="text-sm text-gray-700">
              {{ formatTime(row.check_in_time) }}
            </span>
          </div>
          <div v-else>
            <span class="text-base">{{ item }}</span>
          </div>
        </template>
      </ListView>
    </div>

    <!-- attendance status section -->
    <div class="flex flex-col gap-4 mt-1">
      <div v-if="rsvp_form.data?.requires_host_approval" class="text-sm text-gray-600">
        Note: Host approval is enabled, attendees will receive an email notification when you
        accept or reject their RSVP.
      </div>

      <div class="flex items-center justify-between">
        <div class="font-semibold text-gray-800">Attendance Status</div>
        <Button size="md" icon-left="download" @click="downloadAttendeeList">Download</Button>
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

        <template #cell="{ item, row, column }">
          <div v-if="column.key === 'confirm_attendance'">
            <span
              class="px-2 py-1 rounded text-sm font-medium"
              :class="
                Number(row.confirm_attendance || 0) === 1
                  ? 'bg-green-100 text-green-700'
                  : 'bg-red-100 text-red-700'
              "
            >
              {{ Number(row.confirm_attendance || 0) === 1 ? 'Yes' : 'No' }}
            </span>
          </div>

          <div v-else-if="column.key === 'actions'">
            <div class="flex gap-2">
              <Button
                size="sm"
                label="Accept"
                variant="solid"
                :disabled="row.status === 'Accepted'"
                @click="() => updateRsvpStatus(row, 'Accepted')"
              />
              <Button
                size="sm"
                label="Reject"
                theme="red"
                :disabled="row.status === 'Rejected'"
                @click="() => confirmReject(row)"
              />
            </div>
          </div>

          <div v-else>
            <span class="text-base">{{ item }}</span>
          </div>
        </template>
      </ListView>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { inject, ref, computed, watchEffect } from 'vue'
import { createListResource, createResource, ListView, Button } from 'frappe-ui'
import { toast } from 'vue-sonner'

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
    full_answers: false,
  },
  auto: true,
})

// Check-in data resource
const checkedInData = createResource({
  url: 'fossunited.api.chapter.get_checked_in_attendees',
  params: {
    event_id: route.params.id,
  },
  auto: true,
})

const checkinColumns = [
  { key: 'name1', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'im_a', label: 'Im a' },
  { key: 'check_in_time', label: 'Checked-in Time' },
]

const checkedInGroups = ref([])

watchEffect(() => {
  const byDate = checkedInData.data?.by_date || {}
  const dates = Object.keys(byDate)

  const existingByKey = Object.fromEntries(checkedInGroups.value.map((g) => [g.group, g]))

  checkedInGroups.value = dates.map((date) => {
    const data = byDate[date]
    if (existingByKey[date]) {
      existingByKey[date].rows = data.attendees
      return existingByKey[date]
    }
    return { group: date, collapsed: false, rows: data.attendees, key: date }
  })
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const formatTime = (datetime) => {
  if (!datetime) return ''
  const date = new Date(datetime)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const listColumns = computed(() => {
  const columns = new Map()

  const excludedFields = ['confirm_attendance', 'status', 'name']

  // Collect keys from all submissions
  if (Array.isArray(submissions.data)) {
    submissions.data.forEach((submission) => {
      Object.keys(submission).forEach((key) => {
        if (!excludedFields.includes(key) && !columns.has(key)) {
          columns.set(key, { key, label: key })
        }
      })
    })
  }

  // include confirm_attendance only (status stays hidden)
  const result = [
    { key: 'confirm_attendance', label: 'Attending', icon: 'check-circle' },
    ...Array.from(columns.values()),
  ]

  // host approval column
  if (rsvp_form.data?.requires_host_approval) {
    result.push({ key: 'actions', label: 'Actions' })
  }

  return result
})

const groupedRows = ref([])

const updateRsvpStatus = (row, status) => {
  if (!row?.name) {
    toast.error('Invalid row')
    return
  }

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Event RSVP Submission',
      name: row.name,
      fieldname: {
        status,
        confirm_attendance: status === 'Accepted' ? 1 : 0,
      },
    },
    onSuccess() {
      toast.success(`RSVP ${status}`)
      submissions.fetch()
    },
    onError(err) {
      toast.error(err.message || 'Update failed')
    },
  }).fetch()
}

const confirmReject = (row) => {
  if (confirm(`Are you sure you want to reject ${row.name1 || 'this attendee'}?`)) {
    updateRsvpStatus(row, 'Rejected')
  }
}

watchEffect(() => {
  const rows = Array.isArray(submissions.data) ? submissions.data : []

  const pending = []
  const accepted = []
  const rejected = []
  const notAttending = []

  const requiresHostApproval = Boolean(rsvp_form.data?.requires_host_approval)

  for (const row of rows) {
    const confirm = Number(row?.confirm_attendance || 0) === 1
    const status = String(row?.status || '').trim()

    if (requiresHostApproval) {
      if (status === 'Pending') {
        pending.push(row)
      } else if (status === 'Accepted' && confirm) {
        accepted.push(row)
      } else if (status === 'Rejected') {
        rejected.push(row)
      } else {
        // everything else falls into Not attending (covers accepted but confirm=false,
        // missing status, or other odd cases)
        notAttending.push(row)
      }
    } else {
      // legacy behaviour: grouping based purely on confirm_attendance
      if (confirm) {
        accepted.push(row)
      } else {
        notAttending.push(row)
      }
    }
  }

  if (requiresHostApproval) {
    groupedRows.value = [
      { group: 'Pending requests', collapsed: false, rows: pending },
      { group: 'Attending event', collapsed: false, rows: accepted },
      { group: 'Not attending', collapsed: true, rows: notAttending },
      { group: 'Rejected attendees', collapsed: true, rows: rejected },
    ]
  } else {
    groupedRows.value = [
      { group: 'Attending event', collapsed: false, rows: accepted },
      { group: 'Not attending', collapsed: true, rows: notAttending },
    ]
  }
})

const downloadAttendeeList = () => {
  const eventId = route.params.id
  window.open(
    `/api/method/fossunited.api.chapter.download_attendee_list_csv?event_id=${eventId}`,
    '_self',
  )
}

const downloadCheckinCSV = () => {
  if (!checkedInData.data?.by_date) return

  const rows = []

  // add header
  rows.push(['date', 'name', 'email', 'im_a', 'checkin_time'])

  // Add data grouped by date
  for (const [date, data] of Object.entries(checkedInData.data.by_date)) {
    for (const attendee of data.attendees) {
      rows.push([
        date,
        attendee.name1 || '',
        attendee.email || '',
        attendee.im_a || '',
        attendee.check_in_time || '',
      ])
    }
  }

  // convert to CSV
  const csvContent = rows
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n')

  // Download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `event-checkins-${route.params.id}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>
