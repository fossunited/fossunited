<template>
  <div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <!-- Check-In Section -->
    <div v-if="showCheckins" class="flex flex-col gap-4 mt-1">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="font-semibold text-gray-800">
          Event Check-Ins
          <span class="ml-2 text-sm font-normal text-gray-600">
            ({{ uniqueCheckedInCount }} / {{ eventStats.data?.total_accepted || 0 }} confirmed
            attendees)
          </span>
        </div>
        <Button size="md" icon-left="refresh-cw" @click="refreshCheckins"> Refresh </Button>
      </div>

      <SearchListView
        class="h-[500px]"
        :rows="checkinGroups"
        :columns="checkinColumns"
        search-placeholder="Search check-in attendees..."
        item-label="check-ins"
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

// Reactive states for collapse
const checkinGroups = ref([])
const attendeeGroups = ref([])

// Resources
const rsvp_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event RSVP',
    fields: ['requires_host_approval', 'custom_questions'],
    filters: { event: route.params.id },
  },
  auto: true,
})

const submissions = createResource({
  url: 'fossunited.api.rsvp.get_submissions_with_answers',
  params: { event_id: route.params.id },
  auto: true,
})

const checkins = createResource({
  url: 'fossunited.api.rsvp.get_rsvp_checkins',
  params: { event_id: route.params.id },
  auto: true,
})

const shouldShowCheckins = createResource({
  url: 'fossunited.api.rsvp.if_rsvp_show_checkins',
  params: { event_id: route.params.id },
  auto: true,
})

const eventStats = createResource({
  url: 'fossunited.api.rsvp.get_rsvp_checkin_stats',
  params: { event_id: route.params.id },
  auto: true,
})

const showCheckins = computed(() => shouldShowCheckins.data === true)

const uniqueCheckedInCount = computed(() => {
  const list = checkins.data || []
  const unique = new Set(list.map((c) => c.email))
  return unique.size
})

const listOptions = {
  selectable: false,
  showTooltip: true,
  resizeColumn: true,
  emptyState: {
    title: 'No data',
    description: 'No records found.',
  },
}

// Check-in columns
const checkinColumns = [
  { key: 'name1', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'im_a', label: 'Im a' },
  { key: 'check_in_time', label: 'Checked-in Time' },
]

const checkinExportColumns = [{ key: 'date', label: 'Date' }, ...checkinColumns]

// Group check-ins by date
watchEffect(() => {
  const list = checkins.data || []
  const byDate = {}

  list.forEach((checkin) => {
    const date = new Date(checkin.check_in_time).toISOString().split('T')[0]
    if (!byDate[date]) byDate[date] = []
    byDate[date].push({ ...checkin, date })
  })

  const dates = Object.keys(byDate).sort().reverse()
  const existingStates = Object.fromEntries(checkinGroups.value.map((g) => [g.group, g.collapsed]))

  checkinGroups.value = dates.map((date) => ({
    group: date,
    collapsed: existingStates[date] ?? false,
    rows: byDate[date],
  }))
})

const attendeeColumns = computed(() => {
  const baseColumns = [
    { label: 'Name', key: 'name1', width: '200px' },
    { label: 'Email', key: 'email', width: '250px' },
    { label: 'Im a', key: 'im_a', width: '150px' },
    { label: 'Confirmed', key: 'confirm_attendance', width: '120px' },
  ]

  // Get custom field names from rsvp_form
  const cq = rsvp_form.data?.custom_questions || []
  cq.forEach((q) => {
    baseColumns.push({
      label: q.question,
      key: q.question,
      width: '300px',
    })
  })
  if (rsvp_form.data?.requires_host_approval) {
    baseColumns.push({ label: 'Actions', key: 'actions', width: '200px' })
  }

  return baseColumns
})

const attendeeExportColumns = computed(() => {
  const data = submissions.data?.[0]
  if (!data) return []
  return Object.keys(data)
    .filter(
      (key) => key !== 'name' && !(key === 'status' && !rsvp_form.data?.requires_host_approval),
    )
    .map((key) => ({
      label: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
      key,
    }))
})

// Group attendees by status
watchEffect(() => {
  const rows = submissions.data || []
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

// Actions
const refreshCheckins = () => {
  checkins.reload()
  eventStats.reload()
}

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
