<template>
  <!-- Main Section -->
  <div v-if="event.data" class="w-full">
    <EventHeader :event="event.data" class="p-4 md:p-8" />
    <hr />
    <div class="p-4 md:px-8 md:py-6">
      <div
        v-if="ticket_checkin_insights.data?.daily_data?.length"
        class="flex flex-col gap-4 my-2"
      >
        <div class="prose">
          <h4>Daily Check-in Insights</h4>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <TicketTierInsightCard
            v-for="day in ticket_checkin_insights.data.daily_data"
            :key="day.title"
            :tier="day"
          />
        </div>
      </div>

      <div class="prose">
        <h2 class="mb-1">Attendee Check-Ins</h2>
        <p class="text-sm">Check in attendees as they arrive at the event.</p>
      </div>
      <div class="flex flex-col my-4 justify-center">
        <!-- QR Scanner Toggle -->
        <div class="mb-4">
          <button
            type="button"
            class="w-[150px] btn btn-primary bg-surface-gray-6 text-ink-white rounded py-1"
            :aria-expanded="!!showScanner"
            aria-controls="qr-ticket-scanner"
            @click="showScanner = !showScanner"
          >
            {{ showScanner ? 'Close Scanner' : 'Scan Ticket QR' }}
          </button>
        </div>

        <QRTicketScanner v-model="showScanner" @scanned="handleScan" />

        <!-- Attendee List with Search -->
        <SearchListView
          v-if="!loading"
          :rows="groupedAttendees"
          :columns="columns"
          row-key="name"
          :search-fields="['full_name', 'name']"
          search-placeholder="Search by name or ticket ID…"
          :filter-field="filterField"
          :filter-options="filterOptions"
          :exportable="true"
          export-filename="event-checkins"
          :export-columns="exportColumns"
          item-label="attendees"
          :options="{
            emptyState: {
              title: 'No attendees found',
            },
          }"
        >
          <template #group-header="{ group }">
            <span class="text-base font-medium leading-6 text-ink-gray-9">
              {{ group.group }} ({{ group.rows.length }})
            </span>
          </template>

          <template #cell="{ item, row, column }">
            <template v-if="column.key === 'action'">
              <Button
                v-if="!isCheckedInToday(row)"
                class="w-fit"
                label="Check-in"
                variant="solid"
                @click="handleCheckIn(row)"
              />
              <Button v-else class="w-fit" label="Manage" @click="handleManage(row)" />
            </template>
            <template
              v-else-if="column.key === 'wants_tshirt' || column.key === 'tshirt_delivered'"
            >
              <Checkbox :model-value="Boolean(item)" :disabled="true" class="w-4 h-4" />
            </template>
            <template v-else-if="column.key === 'name'">
              <span class="font-mono text-sm font-semibold text-ink-gray-8 truncate text-wrap">{{
                item
              }}</span>
            </template>
            <template v-else-if="column.key === 'checkin_status'">
              <div class="flex items-center overflow-hidden overflow-x-visible flex-wrap">
                <span
                  v-for="(data, index) in row.checkin_data"
                  :key="index"
                  class="flex items-center p-1 rounded-sm"
                >
                  <Tooltip arrow-class="fill-black" :placement="'top'" :hover-delay="0.5">
                    <template #body>
                      <span
                        class="text-xs bg-surface-gray-7 text-ink-white px-2 py-1 rounded-full"
                      >
                        {{ formatCheckinDateTime(data.check_in_time) }}
                      </span>
                    </template>
                    <Badge
                      :theme="getRelativeTime(data.check_in_time) == 'Today' ? 'green' : 'gray'"
                      class="flex gap-1 items-center"
                    >
                      <IconChecks class="w-4 h-4" />
                      <span>{{ getRelativeTime(data.check_in_time) }}</span>
                    </Badge>
                  </Tooltip>
                </span>
              </div>
            </template>
            <template v-else>
              <span class="text-base truncate text-wrap">
                {{ item }}
              </span>
            </template>
          </template>
        </SearchListView>

        <div v-else>
          <LoadingText />
        </div>
      </div>
    </div>
  </div>

  <CheckinConfirmationDialog
    v-model="showConfirmDialog"
    :selected-attendee="selectedAttendee"
    :attendees="attendees"
    @updated="attendees.fetch()"
  />
  <CheckinManageDialog
    v-model="showManageDialog"
    :selected-attendee="selectedAttendee"
    :attendees="attendees"
    @updated="attendees.fetch()"
  />
</template>

<script setup>
import EventHeader from '@/components/EventHeader.vue'
import SearchListView from '@/components/ui/SearchListView.vue'
import CheckinConfirmationDialog from '@/components/event/CheckinConfirmationDialog.vue'
import CheckinManageDialog from '@/components/event/CheckinManageDialog.vue'
import QRTicketScanner from '@/components/event/QRTicketScanner.vue'
import {
  createResource,
  usePageMeta,
  LoadingText,
  Badge,
  Tooltip,
  Checkbox,
  Button,
} from 'frappe-ui'
import { useRoute } from 'vue-router'
import { inject, provide, ref, computed, watch, watchEffect } from 'vue'
import { IconChecks } from '@tabler/icons-vue'
import dayjs, { formatCheckinDateTime, getRelativeTime, isCheckedInToday } from '@/helpers/date'
import { toast } from 'vue-sonner'

const session = inject('$session')
const route = useRoute()
provide('route', route)

const showScanner = ref(false)
const selectedAttendee = ref(null)
const showConfirmDialog = ref(false)
const showManageDialog = ref(false)
const filterField = ref('checkin_group')
const groupedAttendees = ref([])

const event = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Chapter Event',
      name: route.params.id,
      fields: ['*'],
    }
  },
  auto: true,
})

usePageMeta(() => {
  return {
    title: `Check-ins | ${event.data?.event_name}`,
  }
})

const attendees = createResource({
  url: 'fossunited.api.checkins.get_attendee_with_checkin_data',
  makeParams() {
    return {
      event_id: route.params.id,
      filters: {},
    }
  },
  auto: true,
})

const ticket_checkin_insights = createResource({
  url: 'fossunited.api.tickets.get_checkin_insights',
  makeParams() {
    return {
      event_id: route.params.id,
    }
  },
  loading: true,
  auto: true,
  onError(error) {
    toast.error(error.message)
  },
})

const loading = computed(() => !attendees.data)

// Filter options with available groups
const filterOptions = computed(() => {
  const options = ['All']
  const groups = groupedAttendees.value.map((g) => g.group)
  return [...options, ...groups]
})

// Group attendees by check-in and t-shirt status using watchEffect
watchEffect(() => {
  const rows = attendees.data || []

  const notCheckedIn = []
  const checkedInTshirtPending = []
  const checkedInTshirtDelivered = []
  const checkedInNoTshirt = []

  rows.forEach((attendee) => {
    const hasCheckedIn = attendee.checkin_data?.length > 0

    // Add group identifier for filtering
    if (!hasCheckedIn) {
      attendee.checkin_group = 'Not Checked-in'
      notCheckedIn.push(attendee)
    } else if (attendee.wants_tshirt && !attendee.tshirt_delivered) {
      attendee.checkin_group = 'Checked-in (T-shirt Pending)'
      checkedInTshirtPending.push(attendee)
    } else if (attendee.wants_tshirt && attendee.tshirt_delivered) {
      attendee.checkin_group = 'Checked-in (T-shirt Delivered)'
      checkedInTshirtDelivered.push(attendee)
    } else {
      attendee.checkin_group = 'Checked-in (No T-shirt)'
      checkedInNoTshirt.push(attendee)
    }
  })

  // Preserve existing collapsed states
  const existingStates = Object.fromEntries(
    groupedAttendees.value.map((g) => [g.group, g.collapsed]),
  )

  const groups = []

  if (notCheckedIn.length > 0) {
    groups.push({
      group: 'Not Checked-in',
      collapsed: existingStates['Not Checked-in'] ?? false,
      rows: notCheckedIn,
    })
  }

  if (checkedInTshirtPending.length > 0) {
    groups.push({
      group: 'Checked-in (T-shirt Pending)',
      collapsed: existingStates['Checked-in (T-shirt Pending)'] ?? false,
      rows: checkedInTshirtPending,
    })
  }

  if (checkedInTshirtDelivered.length > 0) {
    groups.push({
      group: 'Checked-in (T-shirt Delivered)',
      collapsed: existingStates['Checked-in (T-shirt Delivered)'] ?? true,
      rows: checkedInTshirtDelivered,
    })
  }

  if (checkedInNoTshirt.length > 0) {
    groups.push({
      group: 'Checked-in (No T-shirt)',
      collapsed: existingStates['Checked-in (No T-shirt)'] ?? true,
      rows: checkedInNoTshirt,
    })
  }

  groupedAttendees.value = groups
})

const columns = [
  { label: 'Name', key: 'full_name', width: '200px' },
  { label: 'Ticket ID', key: 'name', width: '100px' },
  { label: 'Bought T-shirt?', key: 'wants_tshirt', width: '100px' },
  { label: 'T-shirt Delivered?', key: 'tshirt_delivered', width: '100px' },
  { label: 'Check-in Status', key: 'checkin_status', width: '200px' },
  { label: 'Actions', key: 'action', width: '100px' },
]

const exportColumns = [
  { label: 'Name', key: 'full_name' },
  { label: 'Ticket ID', key: 'name' },
  {
    label: 'Bought T-shirt',
    key: 'wants_tshirt',
    exportValue: (row) => (row.wants_tshirt ? 'Yes' : 'No'),
  },
  {
    label: 'T-shirt Delivered',
    key: 'tshirt_delivered',
    exportValue: (row) => (row.tshirt_delivered ? 'Yes' : 'No'),
  },
  {
    label: 'Check-in Status',
    key: 'checkin_data',
    exportValue: (row) => {
      if (!row.checkin_data?.length) return 'Not Checked-in'
      return row.checkin_data
        .map((d) => dayjs(d.check_in_time).format('DD MMM YYYY, hh:mm A'))
        .join('; ')
    },
  },
  {
    label: 'Group',
    key: 'checkin_group',
  },
]

provide('isCheckedInToday', isCheckedInToday)

const handleCheckIn = (row) => {
  selectedAttendee.value = row
  showConfirmDialog.value = true
}

const handleManage = (row) => {
  selectedAttendee.value = row
  showManageDialog.value = true
}

const handleScan = (scannedId) => {
  showScanner.value = false
  const scannedAttendee = attendees.data?.find((a) => a.name === scannedId)
  if (scannedAttendee) {
    handleCheckIn(scannedAttendee)
  }
}

watch(showScanner, (val) => {
  if (val) {
    attendees.fetch()
  }
})
</script>
