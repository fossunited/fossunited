<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Manage Attendee',
    }"
  >
    <template v-if="selectedAttendee" #body-content>
      <div class="flex flex-col gap-4">
        <div class="space-y-2">
          <div class="text-sm uppercase font-medium">Details</div>
          <div class="bg-gray-50 text-sm p-2 rounded-sm font-mono">
            <p class="leading-5">
              Name: {{ selectedAttendee.full_name }}
              <br />
              Ticket ID: {{ selectedAttendee.name }}
              <br />
              Tier: {{ selectedAttendee.tier }}
              <br />
              Has Tshirt Add-on:
              {{ selectedAttendee.wants_tshirt ? 'Yes' : 'No' }}
              <br />
            </p>
            <p v-if="selectedAttendee.wants_tshirt" class="leading-5">
              <span>Tshirt Size: {{ selectedAttendee.tshirt_size }}</span>
              <br />
              <span
                >Tshirt Assigned:
                <span
                  :class="selectedAttendee.tshirt_delivered ? 'text-green-600' : 'text-red-600'"
                >
                  {{ selectedAttendee.tshirt_delivered ? 'Yes' : 'No' }}
                </span>
              </span>
            </p>
            <div class="border-b-2 border-dashed border-gray-600 my-3"></div>
            <div class="flex flex-col gap-2">
              <div class="text-sm uppercase font-medium">Check-ins</div>
              <div
                v-for="(data, index) in selectedAttendee.checkin_data"
                :key="index"
                class="flex gap-2"
              >
                <span>-></span>
                <span>
                  {{ dayjs(data.check_in_time).format('DD MMM YYYY, h:mm A') }}
                </span>
              </div>
            </div>
          </div>
          <Button
            v-if="isCheckedInToday(selectedAttendee)"
            class="!text-sm border-orange-600 hover:border-orange-400 text-orange-600"
            icon-left="alert-triangle"
            label="Undo Check-In for Today"
            size="sm"
            variant="outline"
            @click="undoAttendeeCheckin.fetch()"
          />
        </div>
        <div v-if="selectedAttendee.wants_tshirt && !selectedAttendee.tshirt_delivered">
          <hr class="mb-4" />
          <div class="text-sm uppercase font-medium">Assign T-shirt</div>
          <p class="text-sm leading-5 mt-1">
            <span class="text-orange-600">Pending</span> T-shirt assignment.
            <br />
            Click the button below when you have assigned a T-shirt to the attendee.
          </p>
          <Button
            class="mt-2"
            label="Mark as Assigned"
            size="sm"
            variant="solid"
            :loading="assignTshirt.loading"
            loading-text="Assigning..."
            @click="assignTshirt.fetch()"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<!-- eslint-disable vue/no-mutating-props -->
<script setup>
import { defineProps, defineModel, inject } from 'vue'
import { Dialog, createResource } from 'frappe-ui'
import dayjs from 'dayjs'

const props = defineProps({
  attendees: {
    type: Object,
    required: true,
  },
  selectedAttendee: {
    type: Object,
    default: () => ({}),
  },
})

const session = inject('$session')
const route = inject('route')
const isCheckedInToday = inject('isCheckedInToday')

const showDialog = defineModel({
  type: Boolean,
  default: false,
})

const assignTshirt = createResource({
  url: 'fossunited.api.checkins.assign_tshirt',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: props.selectedAttendee,
      user: session.user,
    }
  },
  onSuccess() {
    const index = props.attendees.data.findIndex(
      (data) => data.name === props.selectedAttendee.name,
    )
    props.attendees.data[index].tshirt_delivered = true
  },
})

const undoAttendeeCheckin = createResource({
  url: 'fossunited.api.checkins.undo_attendee_checkin',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: props.selectedAttendee,
      user: session.user,
    }
  },
  onSuccess() {
    const index = props.attendees.data.findIndex(
      (data) => data.name === props.selectedAttendee.name,
    )
    props.attendees.data[index].checkin_data.pop()
    props.selectedAttendee = null
    showDialog.value = false
  },
})
</script>
