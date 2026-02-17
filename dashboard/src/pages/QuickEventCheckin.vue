<template>
  <div class="min-h-screen flex md:items-center justify-center bg-surface-white">
    <div class="w-full max-w-md p-4 md:p-6">
      <!-- Header Section -->
      <div v-if="event.data" class="mb-10">
        <EventHeader :event="event.data" />
      </div>

      <h1 class="text-[2em] font-bold mb-2 text-center">Quick Check-In</h1>
      <p class="text-sm text-ink-gray-5 mb-10 text-center">
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
            class="absolute right-2 top-[17px] bg-surface-gray-6 text-ink-white rounded py-2 px-2 hover:bg-surface-red-5 text-lg"
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
          class="btn btn-primary bg-surface-green-3 text-ink-white rounded py-2 px-4 w-full"
          :disabled="loading || !ticketId.trim()"
          @click="handleTicketInput"
        >
          Check-In
        </button>

        <!-- Scan QR button -->
        <button
          type="button"
          class="btn btn-primary bg-surface-gray-6 text-ink-white rounded py-2 px-4 w-full"
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
        class="mt-4 text-sm font-medium text-ink-red-4"
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
        @update:selectedAttendee="onSelectedAttendeeUpdate"
      />
    </div>
  </div>
</template>

<script setup>
import EventHeader from '@/components/EventHeader.vue'
import { ref, provide, onBeforeUnmount, reactive, watch } from 'vue'
import { call, createResource, FormControl } from 'frappe-ui'
import CheckinConfirmationDialog from '@/components/event/CheckinConfirmationDialog.vue'
import { useRoute } from 'vue-router'
import QRTicketScanner from '@/components/event/QRTicketScanner.vue'
import { toast } from 'vue-sonner'

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
