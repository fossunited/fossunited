<template>
  <div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <DocsInfo
      v-if="rsvp_form.data?.requires_host_approval"
      message="Host approval is enabled, attendees will receive an email notification when you accept or reject their RSVP."
      docs-url="https://docs.fossunited.org/event-rsvp/#restrictive-access-to-event"
    />

    <!-- Main Section Header -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="font-semibold text-ink-gray-8">
        {{ sectionTitle }}
        <span v-if="currentView === 'checkins'" class="ml-2 text-sm font-normal text-ink-gray-5">
          ({{ checkins.data?.length || 0 }} checked-in out of
          {{ eventStats.data?.total_accepted || 0 }} confirmed attendees)
        </span>
      </div>

      <div class="flex items-center gap-2">
        <!-- View Toggle - Only show when check-ins are available -->
        <div class="flex items-center gap-1 bg-surface-gray-2 rounded-lg p-1">
          <button
            class="px-3 py-1.5 text-sm rounded-md transition-colors"
            :class="
              currentView === 'attendees'
                ? 'bg-surface-white text-ink-gray-9 font-medium shadow-sm'
                : 'text-ink-gray-5 hover:text-ink-gray-9'
            "
            @click="currentView = 'attendees'"
          >
            Attendees
          </button>
          <button
            class="px-3 py-1.5 text-sm rounded-md transition-colors"
            :class="
              currentView === 'checkins'
                ? 'bg-surface-white text-ink-gray-9 font-medium shadow-sm'
                : 'text-ink-gray-5 hover:text-ink-gray-9'
            "
            @click="currentView = 'checkins'"
          >
            Check-ins
          </button>
        </div>

        <Button
          v-if="currentView === 'checkins'"
          size="md"
          icon-left="refresh-cw"
          @click="refreshCheckins"
        >
          Refresh
        </Button>
      </div>
    </div>

    <DocsInfo
      v-if="!showCheckins && currentView === 'checkins'"
      message="You can check-in attendees during the event days."
      docs-url="https://docs.fossunited.org/event-rsvp/#event-check-ins"
    />

    <!-- Check-Ins View -->
    <CheckInsTable
      v-if="currentView === 'checkins'"
      :checkins="checkins.data || []"
      name-field="name1"
      docs-message="You can check-in attendees during the event days"
      docs-url="https://docs.fossunited.org/event-rsvp/#event-check-ins"
      :export-filename="`event-checkins-${route.params.id}`"
      :additional-columns="[{ key: 'im_a', label: 'Im a', width: '200px' }]"
    />

    <!-- Attendees View -->
    <SearchListView
      v-else
      :rows="attendeeGroups"
      :columns="attendeeColumns"
      search-placeholder="Search attendees..."
      item-label="attendees"
      :export-filename="`rsvp-submissions-${route.params.id}`"
      :export-columns="attendeeExportColumns"
      row-drawer
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
          :class="item ? 'bg-surface-green-2 text-ink-green-3' : 'bg-surface-red-2 text-ink-red-3'"
        >
          {{ item ? 'Yes' : 'No' }}
        </span>

        <div
          v-else-if="column.key === 'checkin_action' && row.is_attending === true"
          class="flex gap-2"
          @click.stop
        >
          <!-- Check-in button - disabled before event with tooltip -->
          <div class="relative group">
            <Button
              v-if="!row.has_checked_in_today"
              size="sm"
              label="Check-in"
              variant="solid"
              :disabled="!showCheckins"
              @click="checkInAttendee(row)"
            />
            <Button
              v-else
              size="sm"
              label="Checked-in today"
              theme="green"
              variant="outline"
              :disabled="!showCheckins"
              @click="confirmUndoCheckIn(row)"
            />

            <!-- Tooltip for disabled state -->
            <div
              v-if="!showCheckins"
              class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-surface-gray-7 text-ink-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10"
            >
              Check-in will be available during event days
              <div
                class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"
              ></div>
            </div>
          </div>
        </div>

        <div v-else-if="column.key === 'actions'" class="flex gap-2" @click.stop>
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

        <!-- Check type → disabled checkbox -->
        <input
          v-else-if="questionTypeMap[column.key] === 'Check'"
          type="checkbox"
          :checked="!!item && item !== '0'"
          disabled
          class="w-4 h-4 accent-ink-gray-7 cursor-default"
        />

        <div v-else class="text-sm truncate cursor-pointer w-full" :title="String(item ?? '')">{{ item }}</div>
      </template>

      <template #drawer-cell="{ column, item }">
        <!-- confirm_attendance badge -->
        <span
          v-if="column.key === 'confirm_attendance'"
          class="px-2 py-0.5 rounded text-sm font-medium w-fit"
          :class="item ? 'bg-surface-green-2 text-ink-green-3' : 'bg-surface-red-2 text-ink-red-3'"
        >
          {{ item ? 'Yes' : 'No' }}
        </span>
        <!-- Check type → checkbox + label -->
        <div v-else-if="questionTypeMap[column.key] === 'Check'" class="flex items-center gap-2">
          <input
            type="checkbox"
            :checked="!!item && item !== '0'"
            disabled
            class="w-4 h-4 accent-ink-gray-7"
          />
          <span class="text-sm text-ink-gray-7">{{ (!!item && item !== '0') ? 'Yes' : 'No' }}</span>
        </div>
        <!-- Long text / Text Editor: full text, no truncation -->
        <p
          v-else-if="['Long Text', 'Text Editor'].includes(questionTypeMap[column.key])"
          class="text-sm text-ink-gray-7 whitespace-pre-wrap"
        >{{ item || '—' }}</p>
        <span v-else class="text-sm text-ink-gray-7 break-words">{{ item ?? '—' }}</span>
      </template>
    </SearchListView>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed, ref, watchEffect } from 'vue'
import { createResource, Button, frappeRequest } from 'frappe-ui'
import SearchListView from '@/components/ui/SearchListView.vue'
import CheckInsTable from '@/components/ui/CheckInsTable.vue'
import { toast } from 'vue-sonner'
import DocsInfo from '@/components/DocsInfo.vue'

const route = useRoute()

// Current view toggle
const currentView = ref('attendees')

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

// Show check-ins tab and enable buttons only during event dates
const showCheckins = computed(() => shouldShowCheckins.data === true)

// Dynamic section title
const sectionTitle = computed(() => {
  if (currentView.value === 'checkins') {
    return 'Event Check-Ins'
  }

  if (rsvp_form.data?.requires_host_approval) {
    return 'Attendee Requests'
  }

  return 'Attendees List'
})

// Maps question label → field type for type-aware cell rendering
const questionTypeMap = computed(() => {
  const map = {}
  for (const q of rsvp_form.data?.custom_questions || []) {
    map[q.question] = q.type
  }
  return map
})

const attendeeColumns = computed(() => {
  const baseColumns = [
    { label: 'Name', key: 'name1', width: '250px' },
    { label: 'Email', key: 'email', width: '200px' },
    { label: 'Im a', key: 'im_a', width: '150px' },
    { label: 'Confirmed', key: 'confirm_attendance', width: '120px' },
  ]

  // Get custom field names from rsvp_form
  const cq = rsvp_form.data?.custom_questions || []
  cq.forEach((q) => {
    baseColumns.push({
      label: q.question,
      key: q.question,
      width: '200px',
    })
  })

  baseColumns.push({ label: 'Check-in', key: 'checkin_action', width: '180px', drawer: false })

  if (rsvp_form.data?.requires_host_approval) {
    baseColumns.push({ label: 'Actions', key: 'actions', width: '200px', drawer: false })
  }

  return baseColumns
})

const attendeeExportColumns = computed(() => {
  const data = submissions.data?.[0]
  if (!data) return []
  return Object.keys(data)
    .filter(
      (key) =>
        key !== 'name' &&
        key !== 'has_checked_in_today' &&
        !(key === 'status' && !rsvp_form.data?.requires_host_approval),
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
  const checkedInSubmissions = new Set()
  const today = new Date().toISOString().split('T')[0]

  const pending = []
  const accepted = []
  const rejected = []
  const notAttending = []

  ;(checkins.data || []).forEach((c) => {
    const date = new Date(c.check_in_time).toISOString().split('T')[0]
    if (date === today) {
      checkedInSubmissions.add(c.parent)
    }
  })

  // Update all rows with check-in status
  rows.forEach((row) => {
    row.has_checked_in_today = checkedInSubmissions.has(row.name)
  })

  rows.forEach((row) => {
    const confirmed = Boolean(row.confirm_attendance)
    const status = row.status || ''
    row.is_attending = requiresApproval ? row.status === 'Accepted' && confirmed : confirmed

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

// Actions
const refreshCheckins = () => {
  checkins.reload()
  eventStats.reload()
}

const updateRsvpStatus = async (row, status) => {
  if (!row?.name) return

  try {
    await frappeRequest({
      url: 'frappe.client.set_value',
      params: {
        doctype: 'FOSS Event RSVP Submission',
        name: row.name,
        fieldname: {
          status,
          confirm_attendance: status === 'Accepted' ? 1 : 0,
        },
      },
    })
    toast.success(`RSVP ${status}`)
    submissions.fetch()
    eventStats.reload()
  } catch (err) {
    toast.error(err.messages?.[0] || err.message)
  }
}

const confirmReject = (row) => {
  if (confirm(`Are you sure you want to reject ${row.name1 || 'this attendee'}?`)) {
    updateRsvpStatus(row, 'Rejected')
  }
}

const checkInAttendee = async (row) => {
  try {
    await frappeRequest({
      url: 'fossunited.chapters.doctype.foss_event_rsvp_submission.foss_event_rsvp_submission.self_check_in',
      params: { submission_name: row.name },
    })
    toast.success(`Checked in ${row.name1}`)
    submissions.fetch()
    checkins.reload()
    eventStats.reload()
  } catch (err) {
    toast.error(err.messages?.[0] || err.message)
  }
}

const confirmUndoCheckIn = (row) => {
  if (confirm(`Remove today's check-in for ${row.name1 || 'this attendee'}?`)) {
    undoCheckIn(row)
  }
}

const undoCheckIn = async (row) => {
  try {
    await frappeRequest({
      url: 'fossunited.chapters.doctype.foss_event_rsvp_submission.foss_event_rsvp_submission.remove_checkin_for_today',
      params: { submission_name: row.name },
    })

    toast.success('Check-in removed')
    submissions.reload()
    checkins.reload()
    eventStats.reload()
  } catch (err) {
    toast.error(err.messages?.[0] || err.message)
  }
}
</script>
