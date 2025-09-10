<!-- eslint-disable vue/no-mutating-props -->
<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Confirm Attendee Check In?',
    }"
  >
    <template v-if="selectedAttendee" #body-content>
      <div class="flex flex-col py-2">
        <p class="text-base">
          Are you sure you want to check in
          <span class="font-semibold">{{ selectedAttendee.full_name }}</span
          >?
        </p>
        <div class="bg-gray-50 text-sm p-2 my-2 rounded-sm font-mono">
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
            <span v-if="selectedAttendee.wants_tshirt"
              >Tshirt Size: {{ selectedAttendee.tshirt_size }}</span
            >
            <br />
            Check-in Log:
          </p>
          <ul class="text-sm font-mono mt-1 list-disc list-inside">
            <li v-if="!selectedAttendee.checkin_data?.length" class="text-gray-500">
              No check-ins yet
            </li>
            <li
              v-for="(log, index) in selectedAttendee.checkin_data"
              :key="log.check_in_time || index"
              :class="{
                'text-red-600 font-semibold text-2xl uppercase': isToday(log.check_in_time),
              }"
            >
              {{ formatCheckinLog(log.check_in_time) }}
            </li>
          </ul>
        </div>

        <div v-if="selectedAttendee.wants_tshirt && !selectedAttendee.tshirt_delivered">
          <hr class="my-4" />
          <div class="text-sm uppercase font-medium mb-2">Assign T-shirt</div>
          <Checkbox v-model="assignTshirt" label="Confirm Tshirt Assignment" />
          <p class="text-sm leading-5 mt-1 text-gray-600">
            Only check this if you are providing the T-shirt to the attendee at the time of
            check-in.
          </p>
        </div>
      </div>
    </template>
    <template #actions>
      <div class="grid grid-cols-2 gap-2">
        <Button
          label="Cancel"
          @click="
            () => {
              showDialog = false
              // Parent manages selectedAttendee; avoid prop mutation
            }
          "
        />
        <Button
          label="Check In"
          variant="solid"
          theme="green"
          :loading="checkinAttendee.loading"
          loading-text="Checking in..."
          @click="checkinAttendee.fetch()"
        />
      </div>
    </template>
  </Dialog>
</template>

<!-- eslint-disable vue/no-mutating-props -->
<script setup>
import { toast } from 'vue-sonner'
import { defineProps, defineModel, inject, ref } from 'vue'
import { createResource, Dialog, Checkbox } from 'frappe-ui'

import dayjs from 'dayjs'
const isToday = (datetime) => dayjs(datetime).isSame(dayjs(), 'day')

const formatCheckinLog = (datetime) => {
  if (isToday(datetime)) {
    // "Today at 05:56 PM"
    return `Today at ${dayjs(datetime).format('hh:mm A')}`
  } else {
    // "09 Sep 2025, 05:56 PM"
    return dayjs(datetime).format('DD MMM YYYY, hh:mm A')
  }
}

const props = defineProps({
  selectedAttendee: {
    type: Object,
    default: () => null,
  },
  attendees: {
    type: Object,
    default: () => ({}),
  },
})

const route = inject('route')
const assignTshirt = ref(false)
const emit = defineEmits(['update:selectedAttendee'])

const showDialog = defineModel({
  type: Boolean,
})

const checkinAttendee = createResource({
  url: 'fossunited.api.checkins.checkin_attendee',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: props.selectedAttendee,
      assign_tshirt: assignTshirt.value,
    }
  },
  onSuccess() {
    // Prefer refetch to get authoritative server time and avoid prop mutation
    props.attendees.fetch?.()
    emit?.('update:selectedAttendee', null)
    assignTshirt.value = false
    showDialog.value = false
  },
  onError(error) {
    const msg =
      error?.message || 'Failed to check in attendee. The attendee may already be checked in.'
    toast.error(msg)
  },
})
</script>
