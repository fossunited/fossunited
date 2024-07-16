<template>
  <Dialog
    class="z-50"
    v-model="showDialog"
    :options="{
      title: 'Change Mode of Attendance',
    }"
  >
    <template #body-content>
      <div
        class="flex flex-col gap-2 items-center text-center p-3 rounded w-full bg-orange-50 text-orange-600 border-2 border-dashed border-orange-600 text-xs"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="icon icon-tabler h-6 w-6 icons-tabler-outline icon-tabler-alert-circle"
        >
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
          <path d="M12 8v4" />
          <path d="M12 16h.01" />
        </svg>
        <p>
          <b>Attention!</b> You are about to change your attendance mode for
          this hackathon.<br /><br />
          Please note that requests for in-person attendance are subject to
          approval by the organizers due to limited on-site availability.
        </p>
      </div>
      <FormControl
        label="Mode of Attendance"
        v-model="attendanceMode"
        type="select"
        class="mt-4"
        :options="attendanceModeOptions"
      />
      <FormControl
        v-if="attendanceMode == 'local' || attendanceMode == 'local-pending'"
        label="Select LocalHost"
        :disabled="attendanceMode == 'local'"
        v-model="selectedLocalhost"
        type="select"
        class="mt-4"
        :options="
          localhosts.data.map((localhost) => ({
            label: `${localhost.localhost_name}`,
            value: localhost.name,
          }))
        "
      />
      <ErrorMessage :message="errorMessage" class="mt-2" />
    </template>
    <template #actions>
      <div class="grid grid-cols-2 gap-4">
        <Button
          label="Cancel"
          size="sm"
          theme="gray"
          @click="showDialog = false"
        />
        <Button
          label="Change"
          size="sm"
          theme="green"
          :disabled="handleDisabled()"
          @click="handleAttendanceModeChange"
        />
      </div>
    </template>
  </Dialog>
  <div
    class="flex flex-col gap-1 border-2 rounded border-gray-500 border-dashed min-w-[220px] p-4"
  >
    <h5 class="text-xs text-gray-700 uppercase font-medium">
      Your Mode of attendance
    </h5>
    <div class="flex w-full items-center justify-between">
      <div
        class="text-base font-medium"
        :class="attendanceMode == 'local-pending' ? 'text-orange-600' : ''"
      >
        {{
          attendanceMode == 'remote'
            ? 'Remote'
            : attendanceMode == 'local-pending'
              ? 'On-Site (Pending Request)'
              : 'On-site'
        }}
      </div>
      <Button
        v-if="hackathon.data.has_localhosts"
        label="Change"
        size="sm"
        class="w-fit !text-sm"
        @click="showDialog = true"
      />
    </div>
  </div>
</template>
<script setup>
import {
  createResource,
  createListResource,
  Dialog,
  FormControl,
  ErrorMessage,
} from 'frappe-ui'
import { useRoute } from 'vue-router'
import { defineProps, ref } from 'vue'
import { toast } from 'vue-sonner'

const route = useRoute()
const showDialog = ref(false)
const attendanceMode = ref(null)
const selectedLocalhost = ref(null)
const attendanceModeOptions = [
  {
    label: 'Remote',
    value: 'remote',
  },
]

const originalAttendanceMode = ref(null)
const originalLocalhost = ref(null)

const props = defineProps({
  hackathon: {
    type: Object,
    required: true,
  },
})

const participant = createResource({
  url: 'fossunited.api.hackathon.get_session_participant',
  makeParams() {
    return {
      hackathon: props.hackathon.data.name,
    }
  },
  auto: true,
  onSuccess(data) {
    setAttendanceMode(data)
  },
})

const setAttendanceMode = (data) => {
  if (data.wants_to_attend_locally) {
    selectedLocalhost.value = data.localhost
    if (data.localhost_request_status == 'Accepted') {
      attendanceMode.value = 'local'
      originalAttendanceMode.value = 'local'
      originalLocalhost.value = data.localhost
      attendanceModeOptions.push({
        label: 'On-site',
        value: 'local',
      })
      attendanceModeOptions.push({
        label: 'Request In-Person Attendance',
        value: 'local-pending',
      })
      return
    } else {
      attendanceMode.value = 'local-pending'
      originalAttendanceMode.value = 'local-pending'
      originalLocalhost.value = data.localhost
      attendanceModeOptions.push({
        label: 'Pending On-site Request',
        value: 'local-pending',
      })
      return
    }
  }
  attendanceModeOptions.push({
    label: 'Request In-Person Attendance',
    value: 'local-pending',
  })
  attendanceMode.value = 'remote'
  originalAttendanceMode.value = 'remote'
}

const localhosts = createListResource({
  doctype: 'FOSS Hackathon LocalHost',
  filters: {
    parent_hackathon: props.hackathon.data.name,
    is_enabled: 1,
  },
  fields: ['localhost_name', 'name', 'city', 'state', 'location', 'map_link'],
  auto: true,
})

const handleDisabled = () => {
  if (attendanceMode.value == originalAttendanceMode.value) {
    if (
      attendanceMode.value == 'local' ||
      attendanceMode.value == 'local-pending'
    ) {
      return selectedLocalhost.value == originalLocalhost.value
    }
    return true
  }
  return false
}

const errorMessage = ref('')

const updateParticipantLocalhost = (localhost) => {
  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon Participant',
      name: participant.data.name,
      fieldname: {
        'wants_to_attend_locally': 1,
        'localhost': localhost,
      }
    },
    auto: true,
    onSuccess(data){
      showDialog.value = false
      errorMessage.value = ''
      toast.success('Attendance mode updated successfully!')
    },
    onError(err){
      toast.error('Failed to update attendance mode.' + err.message)
    }
  })
}

const makeParticipantRemote = () => {
  createResource({
      url: 'frappe.client.set_value',
      params: {
        doctype: 'FOSS Hackathon Participant',
        name: participant.data.name,
        fieldname: {
          'wants_to_attend_locally': 0,
          'localhost': null,
        }
      },
      auto: true,
      onSuccess(data){
        showDialog.value = false
        errorMessage.value = ''
        toast.success('Attendance mode updated successfully!')
      },
      onError(err){
        toast.error('Failed to update attendance mode.' + err.message)
      }
    })
}

const handleAttendanceModeChange = () => {
  if (attendanceMode.value == 'local-pending' && selectedLocalhost.value == null) {
    errorMessage.value = 'Please select a LocalHost'
    return
  }

  if (attendanceMode.value == 'local-pending') {
    updateParticipantLocalhost(selectedLocalhost.value)
    return
  }

  if (attendanceMode.value == 'remote') {
    makeParticipantRemote()
  }
}
</script>
