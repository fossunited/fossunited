<!-- eslint-disable vue/no-mutating-props -->
<template>
  <Dialog v-model:open="showDialog" class="z-50" title="Confirm Attendee Check In?">
    <template v-if="selectedAttendee">
      <div class="flex flex-col py-2">
        <p class="text-base">
          Are you sure you want to check in
          <span class="font-semibold">{{ selectedAttendee.full_name }}</span
          >?
        </p>
        <div class="my-2 rounded-1 bg-surface-gray-1 p-2 font-mono text-base">
          <p class="text-base-medium leading-6 text-ink-gray-9">
            <strong>Name:</strong> {{ selectedAttendee.full_name }}<br />
            <strong>Ticket ID:</strong> {{ selectedAttendee.name }}<br />
            <strong>Tier:</strong> {{ selectedAttendee.tier }}<br />
            <strong>Organization:</strong> {{ selectedAttendee.organization }}<br />

            <!-- Tshirt section starts -->
            <template v-if="selectedAttendee.wants_tshirt && selectedAttendee.tshirt_delivered">
              <strong>Has T-shirt Add-on:</strong>
              <span class="font-semibold text-ink-green-6">Delivered already!</span><br />
            </template>

            <template
              v-else-if="selectedAttendee.wants_tshirt && !selectedAttendee.tshirt_delivered"
            >
              <strong>Has T-shirt Add-on:</strong>
              <span
                class="rounded-4 bg-surface-amber-2 px-2 py-0.5 font-semibold text-ink-amber-6"
              >
                YES </span
              ><br />
              <strong>T-shirt Size:</strong>
              {{ selectedAttendee.tshirt_size || 'Unknown' }}<br />
            </template>

            <template v-else>
              <strong>Has T-shirt Add-on:</strong>
              <span class="rounded-4 bg-surface-red-2 px-2 py-0.5 font-semibold text-ink-red-8">
                NO </span
              ><br />
            </template>

            <strong>Check-in Log:</strong>
          </p>

          <ul class="mt-1 list-inside list-disc font-mono text-sm">
            <li v-if="!selectedAttendee.checkin_data?.length" class="text-ink-gray-4">
              No check-ins yet
            </li>
            <li
              v-for="(log, index) in selectedAttendee.checkin_data"
              :key="log.name || log.id || log.check_in_time || index"
              :class="{
                'text-3xl font-semibold uppercase text-ink-red-8': isToday(log.check_in_time),
              }"
            >
              {{ formatCheckinLog(log.check_in_time) }}
            </li>
          </ul>
        </div>

        <div v-if="selectedAttendee.wants_tshirt && !selectedAttendee.tshirt_delivered">
          <hr class="my-4" />
          <div class="text-sm-medium mb-2 uppercase">Assign T‑shirt</div>
          <Checkbox v-model="assignTshirt" label="Confirm T‑shirt Assignment" />
          <p class="mt-1 text-sm leading-5 text-ink-gray-5">
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
          class="!bg-surface-green-9 hover:!bg-surface-green-10"
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
import dayjs from 'dayjs'
import { createResource, Dialog, Checkbox } from 'frappe-ui'
import { defineProps, defineModel, inject, ref } from 'vue'
import { toast } from 'vue-sonner'
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
const emit = defineEmits(['updated', 'update:selectedAttendee'])

const showDialog = defineModel({
  type: Boolean,
})

const checkinAttendee = createResource({
  url: 'fossunited.api.checkins.checkin_attendee',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: { name: props.selectedAttendee?.name },
      assign_tshirt: assignTshirt.value,
    }
  },
  onSuccess() {
    emit('updated')
    emit('update:selectedAttendee', null)
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
