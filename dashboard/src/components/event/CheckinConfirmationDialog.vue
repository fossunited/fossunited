<!-- eslint-disable vue/no-mutating-props -->
<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Confirm Attendee Check In',
    }"
  >
    <template v-if="selectedAttendee" #body-content>
      <div class="flex flex-col py-2 gap-3">
        <p class="text-base">
          Are you sure you want to check in
          <span class="font-semibold">{{ selectedAttendee.full_name }}</span
          >?
        </p>
        <div class="bg-surface-gray-1 text-sm p-3 rounded-md font-mono space-y-1">
          <p class="leading-6 text-ink-gray-9">
            <strong>Name:</strong> {{ selectedAttendee.full_name }}<br />
            <strong>Ticket ID:</strong> {{ selectedAttendee.name }}<br />
            <strong>Tier:</strong> {{ selectedAttendee.tier }}<br />
            <strong v-if="selectedAttendee.organization">Organization:</strong> {{ selectedAttendee.organization }}<br v-if="selectedAttendee.organization" />

            <!-- Tshirt section -->
            <template v-if="selectedAttendee.wants_tshirt && selectedAttendee.tshirt_delivered">
              <strong>T-shirt Status:</strong>
              <span class="text-ink-green-3 font-semibold"> Delivered already</span><br />
            </template>

            <template
              v-else-if="selectedAttendee.wants_tshirt && !selectedAttendee.tshirt_delivered"
            >
              <strong>T-shirt Status:</strong>
              <span class="bg-surface-amber-2 text-ink-amber-3 font-semibold px-2 py-0.5 rounded text-xs">
                PENDING HANDOUT
              </span><br />
              <strong>Size:</strong>
              <span class="font-bold text-ink-gray-9">{{ selectedAttendee.tshirt_size || 'Not Selected' }}</span><br />
            </template>

            <template v-else>
              <strong>T-shirt:</strong>
              <span class="text-ink-gray-5">None</span><br />
            </template>

            <strong>Check-in Log:</strong>
          </p>

          <ul class="text-xs font-mono mt-1 list-disc list-inside space-y-0.5">
            <li v-if="!selectedAttendee.checkin_data?.length" class="text-ink-gray-4">
              No previous check-ins
            </li>
            <li
              v-for="(log, index) in selectedAttendee.checkin_data"
              :key="log.name || log.id || log.check_in_time || index"
              :class="{
                'text-ink-green-3 font-semibold': isToday(log.check_in_time),
              }"
            >
              {{ formatCheckinLog(log.check_in_time) }}
              <span v-if="log.checked_in_by" class="text-ink-gray-5"> (by {{ log.checked_in_by }})</span>
            </li>
          </ul>
        </div>

        <!-- T-shirt Assignment Section -->
        <div v-if="selectedAttendee.wants_tshirt && !selectedAttendee.tshirt_delivered" class="p-3 border rounded-md bg-surface-white space-y-2">
          <div class="text-xs uppercase font-bold text-ink-gray-7">T‑shirt Handout at Counter</div>
          <Checkbox v-model="assignTshirt" label="Hand over T‑shirt now during check-in" />

          <!-- Size selection if size is missing -->
          <div v-if="assignTshirt && !selectedAttendee.tshirt_size" class="mt-2">
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">Select Size for Attendee:</label>
            <select
              v-model="chosenTshirtSize"
              class="w-full border rounded px-2 py-1.5 text-sm bg-surface-white border-outline-gray-2"
            >
              <option value="" disabled>-- Choose Size --</option>
              <option v-for="sz in AVAILABLE_SIZES" :key="sz" :value="sz">{{ sz }}</option>
            </select>
          </div>

          <p class="text-xs leading-5 text-ink-gray-5">
            Check this only if the T-shirt is physically handed over right now.
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
import { defineProps, defineModel, inject, ref, watch } from 'vue'
import { createResource, Dialog, Checkbox, Button } from 'frappe-ui'
import dayjs from 'dayjs'

const isToday = (datetime) => dayjs(datetime).isSame(dayjs(), 'day')

const formatCheckinLog = (datetime) => {
  if (isToday(datetime)) {
    return `Today at ${dayjs(datetime).format('hh:mm A')}`
  } else {
    return dayjs(datetime).format('DD MMM YYYY, hh:mm A')
  }
}

const AVAILABLE_SIZES = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL']

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
const chosenTshirtSize = ref('')
const emit = defineEmits(['updated', 'update:selectedAttendee'])

const showDialog = defineModel({
  type: Boolean,
})

watch(
  () => props.selectedAttendee,
  (att) => {
    assignTshirt.value = false
    chosenTshirtSize.value = att?.tshirt_size || ''
  },
)

const checkinAttendee = createResource({
  url: 'fossunited.api.checkins.checkin_attendee',
  makeParams() {
    return {
      event_id: route.params.id,
      attendee: { name: props.selectedAttendee?.name },
      assign_tshirt: assignTshirt.value,
      tshirt_size: chosenTshirtSize.value || props.selectedAttendee?.tshirt_size || null,
    }
  },
  onSuccess() {
    toast.success(`${props.selectedAttendee?.full_name || 'Attendee'} checked in successfully!`)
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
