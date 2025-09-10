<template>
  <div class="min-h-screen flex md:items-center justify-center bg-white">
    <div class="w-full max-w-md p-4 md:p-6">
      <!-- Header Section -->
      <div v-if="event.data" class="mb-10">
        <EventHeader :event="event.data" />
      </div>

      <h1 class="text-[2em] font-bold mb-2 text-center">Quick Check-In</h1>
      <p class="text-sm text-gray-600 mb-10 text-center">
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
            class="absolute right-2 top-[17px] bg-gray-800 text-white rounded py-2 px-2 hover:bg-red-500 text-lg"
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
          class="btn btn-primary bg-green-500 text-white rounded py-2 px-4 w-full"
          :disabled="loading || !ticketId.trim()"
          @click="handleTicketInput"
        >
          Check-In
        </button>

        <!-- Scan QR button -->
        <button
          class="btn btn-primary bg-gray-800 text-white rounded py-2 px-4 w-full"
          :disabled="loading"
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
        class="mt-4 text-sm font-medium text-red-600"
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
      />
    </div>
  </div>
</template>

<script setup>
import EventHeader from '@/components/EventHeader.vue'
import { ref, provide, onBeforeUnmount, watch } from 'vue'
import { call, createResource, FormControl } from 'frappe-ui'
import CheckinConfirmationDialog from '@/components/event/CheckinConfirmationDialog.vue'
import { useRoute } from 'vue-router'
import QRTicketScanner from '@/components/event/QRTicketScanner.vue'

// State
const ticketId = ref('')
const showScanner = ref(false)
const showConfirmDialog = ref(false)
const selectedAttendee = ref(null)
const message = ref('')
const loading = ref(false)

// Dummy attendee resource object to satisfy CheckinConfirmationDialog prop
const attendeeResource = {
  data: [],
  fetch: () => {},
}

function extractTicketId(input) {
  const s = String(input || '').trim()
  if (!s) return ''
  try {
    const u = new URL(s)
    // Try common locations first
    const q =
      u.searchParams.get('ticket_id') ||
      u.searchParams.get('ticket') ||
      u.searchParams.get('id') ||
      u.searchParams.get('name')
    if (q) return q
    const parts = u.pathname.split('/').filter(Boolean)
    return parts[parts.length - 1] || s
  } catch {
    // Not a URL; assume it's already an ID
    return s
  }
}

function handleScan(scannedId) {
  // Normalize & immediately close scanner to avoid repeat scans
  ticketId.value = extractTicketId(scannedId)
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
  message.value = ''
  const raw = ticketId.value.trim()
  const normalizedId = extractTicketId(raw)
  if (!normalizedId) {
    showError('Ticket ID is required')
    loading.value = false
    return
  }

  try {
    const res = await call('fossunited.api.checkins.get_attendee_with_checkin_data', {
      event_id: route.params.id,
      filters: {
        name: normalizedId,
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
</script>
