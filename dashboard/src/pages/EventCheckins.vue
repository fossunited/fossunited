<template>
  <!-- Main Section -->
  <div v-if="event.data" class="w-full">
    <EventHeader :event="event.data" class="p-4 md:p-8" />
    <hr />
    <div class="p-4 md:px-8 md:py-6">
      <div class="prose">
        <h2 class="mb-1">Attendee Check-Ins</h2>
        <p class="text-sm">Check in attendees as they arrive at the event.</p>
      </div>
      <div class="flex flex-col my-4 justify-center">
        <!-- Search Fields -->
        <div class="flex flex-col gap-2 mb-4 mt-2">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 items-center">
            <FormControl
              v-model="filters.full_name"
              label="Name"
              type="text"
              placeholder="Search by Name"
              @input="attendees.fetch()"
            />
            <FormControl
              v-model="filters.email"
              label="Email"
              type="text"
              placeholder="Search by Email"
              @input="attendees.fetch()"
            />
            <FormControl
              v-model="filters.name"
              label="Ticket ID"
              placeholder="Search by Ticket ID"
              @input="attendees.fetch()"
            />
            <div>
              <button
                class="w-[150px] btn btn-primary bg-gray-800 text-white rounded mt-4 py-1"
                @click="toggleScanner"
              >
                Scan Ticket QR
              </button>
            </div>
          </div>
        </div>

        <qrcode-stream
          v-if="showScanner"
          class="my-4 mx-auto border border-gray-300"
          :style="{ width: '100%', maxWidth: '24rem' }"
          @detect="onDetect"
        />

        <!-- Attendee List -->
        <CheckinAttendeeList :event="event.data" :attendees="attendees" />
      </div>
    </div>
  </div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import CheckinAttendeeList from '@/components/event/CheckinAttendeeList.vue'
import { createResource, usePageMeta, FormControl } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { inject, reactive, provide } from 'vue'

import { QrcodeStream } from 'vue-qrcode-reader'
import { ref, onBeforeUnmount } from 'vue'

const showScanner = ref(false)

function toggleScanner() {
  showScanner.value = !showScanner.value
}

function onDetect(detectedCodes) {
  const rawValue = detectedCodes[0]?.rawValue

  if (!rawValue) return

  console.log('Scanned:', rawValue)

  try {
    const url = new URL(rawValue)
    const scannedId = url.searchParams.get('id')

    if (scannedId) {
      filters.name = scannedId
      attendees.fetch()
      showScanner.value = false
    } else {
      alert('Invalid QR code')
    }
  } catch (err) {
    alert('Invalid QR code format')
  }
}

function onInit(promise) {
  promise.catch((error) => {
    console.error('Camera error:', error)
    alert('Camera failed: ' + error.message)
    showScanner.value = false
  })
}

// just toggles off
function stopScanner() {
  showScanner.value = false
}

onBeforeUnmount(() => {
  stopScanner()
})

const session = inject('$session')

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

usePageMeta(() => {
  return {
    title: `Check-ins | ${event.data?.event_name}`,
  }
})

const filters = reactive({
  name: '',
  full_name: '',
  email: '',
})

const attendees = createResource({
  url: 'fossunited.api.checkins.get_attendee_with_checkin_data',
  makeParams() {
    return {
      event_id: route.params.id,
      filters: filters,
    }
  },
  auto: true,
  debounce: 500,
})
</script>
