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
          <div
            class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 items-center"
          >
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
          </div>
        </div>

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
      user: session.user,
      filters: filters,
    }
  },
  auto: true,
  debounce: 500,
})
</script>
