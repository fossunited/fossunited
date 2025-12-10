<template>
  <div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <!-- Check-In Section -->
    <div v-if="checkedInData.data?.show_checkins" class="flex flex-col gap-4 mt-1">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="font-semibold text-gray-800">
          Event Check-Ins
          <span class="ml-2 text-sm font-normal text-gray-600">
            ({{ checkedInData.data.total_checked_in }} / {{ checkedInData.data.total_accepted }}
            confirmed attendees)
          </span>
        </div>
        <Button size="md" icon-left="refresh-cw" @click="checkedInData.reload()"> Refresh </Button>
      </div>

      <SearchListView
        class="h-[500px]"
        :rows="checkinGroups"
        :columns="checkinColumns"
        row-key="name"
        search-placeholder="Search check-in attendees..."
        item-label="attendees"
        :export-filename="`event-checkins-${route.params.id}`"
        :export-columns="checkinExportColumns"
        :options="listOptions"
      >
        <template #group-header="{ group }">
          <span class="text-base font-medium leading-6 text-ink-gray-9">
            {{ formatDate(group.group) }} - {{ group.rows.length }} check-ins
          </span>
        </template>

        <template #cell="{ item, row, column }">
          <span v-if="column.key === 'check_in_time'" class="text-sm text-gray-700">
            {{ formatTime(item) }}
          </span>
          <span v-else class="text-base">{{ item }}</span>
        </template>
      </SearchListView>
    </div>

    <!-- Attendance Status Section -->
    <div class="flex flex-col gap-4 mt-1">
      <div v-if="rsvp_form.data?.requires_host_approval" class="text-sm text-gray-600">
        Note: Host approval is enabled, attendees will receive an email notification when you
        accept or reject their RSVP.
      </div>

      <div class="font-semibold text-gray-800">Attendance Status</div>

      <SearchListView
        class="h-[500px]"
        :rows="attendeeGroups"
        :columns="attendeeColumns"
        row-key="name"
        search-placeholder="Search attendees..."
        item-label="attendees"
        :export-filename="`rsvp-submissions-${route.params.id}`"
        :export-columns="attendeeExportColumns"
        :options="listOptions"
      >
        <template #group-header="{ group }">
          <span class="text-base font-medium leading-6 text-ink-gray-9">
            {{ group.group }} ({{ group.rows.length }})
          </span>
        </template>

        <template #cell="{ item, row, column }">
          <span
            v-if="column.key === 'confirm_attendance'"
            class="px-2 py-1 rounded text-sm font-medium"
            :class="item ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
          >
            {{ item ? 'Yes' : 'No' }}
          </span>

          <div v-else-if="column.key === 'actions'" class="flex gap-2">
            <Button
              size="sm"
              label="Accept"
              variant="solid"
              :disabled="row.status === 'Accepted'"
              @click="updateRsvpStatus(row, 'Accepted')"
            />
            <Button
              size="sm"
              label="Reject"
              theme="red"
              :disabled="row.status === 'Rejected'"
              @click="confirmReject(row)"
            />
          </div>

          <span v-else class="text-base" :title="item">{{ truncate(item, 30) }}</span>
        </template>
      </SearchListView>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed, ref, watchEffect } from 'vue'
import { createResource, Button } from 'frappe-ui'
import SearchListView from '@/components/ui/SearchListView.vue'
import { toast } from 'vue-sonner'

const route = useRoute()

// Reactive group states
const checkinGroups = ref([])
const attendeeGroups = ref([])

// Resources
const rsvp_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event RSVP',
    fields: ['*'],
    filters: { event: route.params.id },
  },
  auto: true,
})

const submissions = createResource({
  url: 'fossunited.api.chapter.get_submissions_with_answers',
  params: { event_id: route.params.id },
  auto: true,
})

const checkedInData = createResource({
  url: 'fossunited.api.chapter.get_checked_in_attendees',
  params: { event_id: route.params.id },
  auto: true,
})

// Shared list options
const listOptions = {
  selectable: false,
  showTooltip: true,
  resizeColumn: true,
  emptyState: {
    title: 'No data',
    description: 'No records found.',
  },
}

// Check-in columns & groups
const checkinColumns = [
  { key: 'name1', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'im_a', label: 'Im a' },
  { key: 'check_in_time', label: 'Checked-in Time' },
]

const checkinExportColumns = [{ key: 'date', label: 'Date' }, ...checkinColumns]

// Build check-in groups reactively (preserves collapsed state)
watchEffect(() => {
  const byDate = checkedInData.data?.by_date || {}
  const dates = Object.keys(byDate)

  // Preserve existing collapsed states
  const existingStates = Object.fromEntries(checkinGroups.value.map((g) => [g.group, g.collapsed]))

  checkinGroups.value = dates.map((date) => ({
    group: date,
    collapsed: existingStates[date] ?? false,
    rows: byDate[date].attendees.map((a) => ({ date, ...a })),
  }))
})

// Attendee columns & groups
const attendeeColumns = computed(() => {
  const baseColumns = [
    { label: 'Name', key: 'name1', width: '200px' },
    { label: 'Email', key: 'email', width: '250px' },
    { label: 'Im a', key: 'im_a', width: '150px' },
    { label: 'Confirmed', key: 'confirm_attendance', width: '120px' },
  ]

  const customFields = submissions.data?.custom_fields || []
  const customColumns = customFields.map((field) => ({
    label: truncate(field, 20),
    key: field,
    width: '300px',
  }))

  const columns = [...baseColumns, ...customColumns]

  if (rsvp_form.data?.requires_host_approval) {
    columns.push({ label: 'Actions', key: 'actions', width: '200px' })
  }

  return columns
})

const attendeeExportColumns = computed(() => {
  const data = submissions.data?.submissions?.[0]
  if (!data) return []
  return Object.keys(data)
    .filter(
      (key) => key !== 'name' && !(key === 'status' && rsvp_form.data?.requires_host_approval),
    )
    .map((key) => ({
      label: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
      key,
    }))
})

// Build attendee groups reactively (preserves collapsed state)
watchEffect(() => {
  const rows = submissions.data?.submissions || []
  const requiresApproval = rsvp_form.data?.requires_host_approval

  const pending = []
  const accepted = []
  const rejected = []
  const notAttending = []

  rows.forEach((row) => {
    const confirmed = Boolean(row.confirm_attendance)
    const status = row.status || ''

    if (requiresApproval) {
      if (status === 'Pending') pending.push(row)
      else if (status === 'Accepted' && confirmed) accepted.push(row)
      else if (status === 'Rejected') rejected.push(row)
      else notAttending.push(row)
    } else {
      if (confirmed) accepted.push(row)
      else notAttending.push(row)
    }
  })

  const existingStates = Object.fromEntries(
    attendeeGroups.value.map((g) => [g.group, g.collapsed]),
  )

  attendeeGroups.value = requiresApproval
    ? [
        {
          group: 'Pending requests',
          collapsed: existingStates['Pending requests'] ?? false,
          rows: pending,
        },
        {
          group: 'Attending event',
          collapsed: existingStates['Attending event'] ?? false,
          rows: accepted,
        },
        {
          group: 'Not attending',
          collapsed: existingStates['Not attending'] ?? true,
          rows: notAttending,
        },
        {
          group: 'Rejected attendees',
          collapsed: existingStates['Rejected attendees'] ?? true,
          rows: rejected,
        },
      ]
    : [
        {
          group: 'Attending event',
          collapsed: existingStates['Attending event'] ?? false,
          rows: accepted,
        },
        {
          group: 'Not attending',
          collapsed: existingStates['Not attending'] ?? true,
          rows: notAttending,
        },
      ]
})

// Utilities
const truncate = (text, maxLength = 30) => {
  if (!text) return ''
  const str = String(text).trim()
  return str.length > maxLength ? str.substring(0, maxLength) + '…' : str
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const formatTime = (datetime) => {
  if (!datetime) return ''
  return new Date(datetime).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// RSVP Actions
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
</script>
