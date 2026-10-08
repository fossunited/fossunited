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
          <div class="bg-surface-gray-1 text-sm p-3 rounded-sm font-mono">
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
              <span>Tshirt Size: {{ selectedAttendee.tshirt_size || 'Not Selected' }}</span>
              <br />
              <span
                >Tshirt Assigned:
                <span
                  :class="
                    selectedAttendee.tshirt_delivered ? 'text-ink-green-3 font-semibold' : 'text-ink-red-4 font-semibold'
                  "
                >
                  {{ selectedAttendee.tshirt_delivered ? 'Yes' : 'No' }}
                </span>
              </span>
            </p>
            <div class="border-b-2 border-dashed border-gray-600 my-3"></div>
            <div class="flex flex-col gap-2">
              <div class="text-sm uppercase font-medium">Check-ins</div>
              <div v-if="!selectedAttendee.checkin_data?.length" class="text-xs text-ink-gray-5">
                No check-in logs found.
              </div>
              <div
                v-for="(data, index) in selectedAttendee.checkin_data"
                :key="index"
                class="flex flex-col text-xs"
              >
                <div class="flex items-center gap-1.5">
                  <span>-></span>
                  <span class="font-semibold">
                    {{ dayjs(data.check_in_time).format('DD MMM YYYY, h:mm A') }}
                  </span>
                  <span v-if="data.checked_in_by" class="text-ink-gray-5">
                    (by {{ data.checked_in_by }})
                  </span>
                </div>
              </div>
            </div>
          </div>
          <Button
            v-if="isCheckedInToday(selectedAttendee)"
            class="!text-sm border-outline-orange-1 hover:border-orange-400 text-ink-amber-3 mt-2"
            icon-left="alert-triangle"
            label="Undo Check-In for Today"
            size="sm"
            variant="outline"
            @click="undoAttendeeCheckin.fetch()"
          />
        </div>
        <div v-if="selectedAttendee.wants_tshirt && !selectedAttendee.tshirt_delivered" class="border p-3 rounded bg-surface-white">
          <div class="text-sm uppercase font-medium">Assign T-shirt</div>
          <p class="text-xs leading-5 mt-1 text-ink-gray-6">
            <span class="text-ink-amber-3 font-semibold">Pending</span> T-shirt assignment.
            Click below when you have handed over the T-shirt.
          </p>

          <div v-if="!selectedAttendee.tshirt_size" class="mt-3">
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">Select Size for Attendee:</label>
            <select
              v-model="chosenTshirtSize"
              class="w-full border rounded px-2 py-1.5 text-sm bg-surface-white border-outline-gray-2"
            >
              <option value="" disabled>-- Choose Size --</option>
              <option v-for="sz in AVAILABLE_SIZES" :key="sz" :value="sz">{{ sz }}</option>
            </select>
          </div>

          <Button
            class="mt-3"
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
import { defineProps, defineModel, inject, ref, watch } from 'vue'
import { Dialog, Button, createResource } from 'frappe-ui'
import dayjs from 'dayjs'
import { toast } from 'vue-sonner'

const AVAILABLE_SIZES = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL']

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

const chosenTshirtSize = ref('')

watch(
  () => props.selectedAttendee,
  (att) => {
    chosenTshirtSize.value = att?.tshirt_size || ''
  },
)

const session = inject('$session')
const route = inject('route')
const isCheckedInToday = inject('isCheckedInToday')
const emit = defineEmits(['updated'])

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
      tshirt_size: chosenTshirtSize.value || props.selectedAttendee?.tshirt_size || null,
    }
  },
  onSuccess(data) {
    const index = props.attendees.data.findIndex(
      (item) => item.name === props.selectedAttendee.name,
    )
    if (index !== -1) {
      props.attendees.data[index].tshirt_delivered = true
      if (data?.tshirt_size) {
        props.attendees.data[index].tshirt_size = data.tshirt_size
      }
    }
    toast.success('T-shirt assigned successfully!')
    emit('updated')
  },
  onError(error) {
    toast.error(error?.message || 'Failed to assign T-shirt')
  },
})

const undoAttendeeCheckin = createResource({
  url: 'fossunited.api.checkins.undo_attendee_checkin',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: props.selectedAttendee,
    }
  },
  onSuccess() {
    const index = props.attendees.data.findIndex(
      (data) => data.name === props.selectedAttendee.name,
    )
    if (index !== -1) {
      props.attendees.data[index].checkin_data.pop()
    }
    props.selectedAttendee = null
    showDialog.value = false
    toast.success('Check-in undone')
    emit('updated')
  },
  onError(error) {
    toast.error(error?.message || 'Failed to undo check-in')
  },
})
</script>
