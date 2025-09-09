<template>
  <div class="min-h-screen flex items-center justify-center bg-white">
    <div class="w-full max-w-sm p-6 text-center">
      <h1 class="text-xl font-bold mb-2">Quick Check-In</h1>
      <p class="text-sm text-gray-600 mb-6">Scan or enter a ticket to check in attendee.</p>

      <!-- Form Section with vertical spacing -->
      <div class="flex flex-col items-center space-y-10">
        <!-- Ticket ID input -->
        <div class="relative w-full">
          <FormControl
            v-model="ticketId"
            label="Ticket ID"
            placeholder="Enter Ticket ID"
            class="pr-10"
            @keyup.enter="handleTicketInput"
          />
          <button
            v-if="ticketId"
            class="absolute right-2 top-[17px] bg-gray-800 text-white rounded py-2 px-2 hover:bg-red-500 text-lg"
            title="Clear"
            @click="ticketId = ''"
          >
            &times;
          </button>
        </div>

        <!-- Manual Check-In Button -->
        <button
          class="btn btn-primary bg-green-500 text-white rounded py-2 px-4 w-full"
          @click="handleTicketInput"
        >
          Check-In
        </button>

        <!-- Scan QR button -->
        <button
          class="btn btn-primary bg-gray-800 text-white rounded py-2 px-4 w-full"
          @click="toggleScanner"
        >
          {{ showScanner ? 'Close Scanner' : 'Scan QR' }}
        </button>
      </div>

      <!-- QR Code Scanner -->
      <qrcode-stream
        v-if="showScanner"
        class="my-6 mx-auto border border-gray-300"
        :style="{ width: '100%', maxWidth: '24rem' }"
        @detect="onDetect"
        @init="onInit"
      />

      <!-- Error message -->
      <div v-if="message" class="mt-4 text-sm font-medium text-red-600">
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
import { ref } from 'vue'
import { call } from 'frappe-ui'
import { QrcodeStream } from 'vue-qrcode-reader'
import { FormControl } from 'frappe-ui'
import CheckinConfirmationDialog from '@/components/event/CheckinConfirmationDialog.vue'
import { useRoute } from 'vue-router'
import { provide } from 'vue'

// State
const ticketId = ref('')
const showScanner = ref(false)
const showConfirmDialog = ref(false)
const selectedAttendee = ref(null)
const message = ref('')

// Dummy attendee resource object to satisfy CheckinConfirmationDialog prop
const attendeeResource = {
  data: [],
  fetch: () => {},
}

// Toggle scanner
function toggleScanner() {
  showScanner.value = !showScanner.value
  if (showScanner.value) {
    ticketId.value = '' // clear input when scanner opens
  }
}

// Handle QR detection
function onDetect(detectedCodes) {
  const rawValue = detectedCodes[0]?.rawValue
  if (!rawValue) return

  try {
    const url = new URL(rawValue)
    const id = url.searchParams.get('id')
    if (id) {
      ticketId.value = id
      handleTicketInput()
      showScanner.value = false
    } else {
      showError('Invalid QR Code')
    }
  } catch (e) {
    showError('Invalid QR Code format')
  }
}

// Handle scanner init error
function onInit(promise) {
  promise.catch((err) => {
    showError('Camera error: ' + err.message)
    showScanner.value = false
  })
}

const route = useRoute()
provide('route', route)

// Fetch attendee and open confirmation dialog
async function handleTicketInput() {
  message.value = ''
  if (!ticketId.value.trim()) {
    showError('Ticket ID is required')
    return
  }

  try {
    const res = await call('fossunited.api.checkins.get_attendee_with_checkin_data', {
      event_id: route.params.id,
      filters: {
        name: ticketId.value.trim(),
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
  }
}

// Show error message
function showError(msg) {
  message.value = msg
  setTimeout(() => {
    message.value = ''
  }, 3000)
}
</script>
