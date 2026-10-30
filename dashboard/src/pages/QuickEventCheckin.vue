<template>
  <div class="flex min-h-screen justify-center bg-surface-base md:items-center">
    <div class="w-full max-w-md p-4 md:p-6">
      <!-- Header Section -->
      <div v-if="event.data" class="mb-10">
        <EventHeader :event="event.data" />
      </div>

      <h1 class="mb-2 text-center text-[2em] font-bold">Quick Check-In</h1>
      <p class="mb-10 text-center text-sm text-ink-gray-5">
        Scan or enter a ticket to check in attendee.
      </p>

      <!-- Form Section with vertical spacing -->
      <div class="flex flex-col items-center space-y-10">
        <!-- Ticket ID input -->
        <div class="relative w-full">
          <FormControl
            v-model="ticketId"
            label="Ticket ID"
            placeholder="Enter Ticket ID"
            class="pr-10"
            autocomplete="off"
            @keyup.enter="handleTicketInput"
          />
          <button
            type="button"
            class="absolute right-2 top-[17px] rounded-4 bg-surface-gray-9 px-2 py-2 text-md text-ink-base hover:bg-surface-red-7"
            title="Clear"
            aria-label="Clear ticket ID"
            :disabled="!ticketId"
            @click="ticketId = ''"
          >
            &times;
          </button>
        </div>

        <!-- Manual Check-In Button -->
        <button
          type="button"
          class="btn btn-primary w-full rounded-4 bg-surface-green-9 px-4 py-2 font-medium text-ink-base hover:bg-surface-green-10 focus-visible:ring-2 focus-visible:ring-outline-gray-5 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="loading || !ticketId.trim()"
          @click="handleTicketInput"
        >
          Check-In
        </button>

        <!-- Scan QR button -->
        <button
          type="button"
          class="btn btn-primary w-full rounded-4 bg-surface-gray-9 px-4 py-2 text-ink-base"
          :disabled="loading || showConfirmDialog"
          @click="showScanner = !showScanner"
        >
          {{ showScanner ? 'Close Scanner' : 'Scan QR' }}
        </button>
      </div>

      <!-- QR Code Scanner -->
      <QRTicketScanner v-model="showScanner" @scanned="handleScan" />

      <!-- Error message -->
      <div
        v-if="message"
        class="text-sm-medium mt-4 text-ink-red-8"
        role="alert"
        aria-live="polite"
      >
        {{ message }}
      </div>

      <!-- Confirmation Dialog -->
      <CheckinConfirmationDialog
        v-model="showConfirmDialog"
        :selected-attendee="selectedAttendee"
        :attendees="attendeeResource"
        @update:selected-attendee="onSelectedAttendeeUpdate"
      />
    </div>
  </div>
</template>

<script setup>
import { call, createResource, FormControl } from 'frappe-ui'
import { ref, provide, onBeforeUnmount, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'

import CheckinConfirmationDialog from '@/components/event/CheckinConfirmationDialog.vue'
import QRTicketScanner from '@/components/event/QRTicketScanner.vue'
import EventHeader from '@/components/EventHeader.vue'

// State
const ticketId = ref('')
const showScanner = ref(false)
const showConfirmDialog = ref(false)
const selectedAttendee = ref(null)
const message = ref('')
const loading = ref(false)

// Minimal reactive resource for CheckinConfirmationDialog
const attendeeResource = reactive({
  data: [],
  fetch: () => {},
})

function handleScan(scannedId) {
  // Close scanner and proceed (QRTicketScanner already normalizes/validates)
  ticketId.value = scannedId
  showScanner.value = false
  handleTicketInput()
}

watch(showScanner, (val) => {
  if (val) {
    ticketId.value = ''
  }
})

const route = useRoute()
provide('route', route)

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

// Fetch attendee and open confirmation dialog
async function handleTicketInput() {
  if (loading.value) return
  loading.value = true
  // Prevent background scans from racing with manual submission
  if (showScanner.value) showScanner.value = false
  message.value = ''
  const raw = ticketId.value.trim()
  if (!raw) {
    showError('Ticket ID is required')
    loading.value = false
    return
  }

  try {
    const res = await call('fossunited.api.checkins.get_attendee_with_checkin_data', {
      event_id: route.params.id,
      filters: {
        name: raw,
      },
    })

    const attendee = Array.isArray(res) && res.length > 0 ? res[0] : null

    if (!attendee) {
      showError('No attendee found with this Ticket ID')
      return
    }

    // Set attendee and open dialog
    selectedAttendee.value = attendee
    attendeeResource.data = [attendee]
    showConfirmDialog.value = true
  } catch (err) {
    showError(err.message || 'Failed to fetch attendee')
  } finally {
    loading.value = false
  }
}

// near other state
let clearMsgTimer

onBeforeUnmount(() => {
  if (clearMsgTimer) clearTimeout(clearMsgTimer)
})

// Show error message
function showError(msg) {
  message.value = msg
  if (clearMsgTimer) clearTimeout(clearMsgTimer)
  clearMsgTimer = setTimeout(() => {
    // Only clear if no newer message replaced it
    if (message.value === msg) message.value = ''
  }, 3000)
}

function onSelectedAttendeeUpdate(val) {
  selectedAttendee.value = val
  if (val == null) {
    ticketId.value = ''
    toast.success('Checked in successfully')
  }
  showConfirmDialog.value = false
}
</script>
