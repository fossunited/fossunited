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
          </p>
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
              selectedAttendee = null
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

const session = inject('$session')
const route = inject('route')
const assignTshirt = ref(false)

const showDialog = defineModel({
  type: Boolean,
})

const checkinAttendee = createResource({
  url: 'fossunited.api.checkins.checkin_attendee',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: props.selectedAttendee,
      user: session.user,
      assign_tshirt: assignTshirt.value,
    }
  },
  onSuccess() {
    makeChangesToAttendeeDict(props.selectedAttendee)
    props.selectedAttendee = null
    assignTshirt.value = false
    showDialog.value = false
  },
  onError(error) {
    toast.error('Failed to check in attendee')
  },
})

const makeChangesToAttendeeDict = (attendee) => {
  const index = props.attendees.data.findIndex((data) => data.name === attendee.name)
  props.attendees.data[index].checkin_data.push({
    check_in_time: new Date(),
  })
  if (assignTshirt.value) {
    props.attendees.data[index].tshirt_delivered = true
  }
}
</script>
