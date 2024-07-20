<template>
  <Dialog
    class="z-50"
    v-model="showDialog"
    :options="{
      title: 'Error',
      message: dialogMessage,
    }"
  />
  <Header />
  <div
    class="w-full p-4 flex items-center justify-center"
    v-if="localhost.data && requests.data"
  >
    <div class="max-w-screen-xl w-full">
      <div class="text-base font-medium mt-4">Manage LocalHost</div>
      <LocalhostHeader :localhost="localhost.data" />
      <div class="grid grid-cols-1 md:grid-cols-2">
        <div class="rounded-sm border-2 border-dashed border-gray-400 p-4 my-2">
          <div class="text-sm uppercase font-medium">Current Status</div>
          <div class="flex items-center justify-between w-full">
            <div
              class="flex items-center gap-2 text-lg font-medium pt-4"
              :class="
                localhost.data.is_accepting_attendees ? 'text-green-700' : ''
              "
            >
              <span
                v-if="localhost.data.is_accepting_attendees"
                class="relative flex h-3 w-3"
              >
                <span
                  class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
                ></span>
                <span
                  class="relative inline-flex rounded-full h-3 w-3 bg-green-500"
                ></span>
              </span>
              <span>
                {{
                  localhost.data.is_accepting_attendees
                    ? 'Accepting Participants'
                    : 'Not Accepting Participants'
                }}
              </span>
            </div>
            <Button
              :label="
                localhost.data.is_accepting_attendees ? 'Disable' : 'Enable'
              "
              @click="toggleAcceptingAttendees"
            />
          </div>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2">
        <div class="rounded-sm border-2 border-dashed border-gray-400 p-4 my-2">
          <div class="text-sm uppercase font-medium">Current Status</div>
          <div class="flex items-center justify-between w-full">
            <div class="flex items-center gap-2 text-lg font-medium pt-4" :class="localhost.doc.is_accepting_attendees ? 'text-green-700': ''">
              <span v-if="localhost.doc.is_accepting_attendees" class="relative flex h-3 w-3">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
              </span>
              <span>
                {{  localhost.doc.is_accepting_attendees ? 'Accepting Participants' : 'Not Accepting Participants' }}
              </span>
            </div>
            <Button
              :label="localhost.doc.is_accepting_attendees ? 'Disable' : 'Enable'"
              @click="toggleAcceptingAttendees"
            />
          </div>
        </div>
      </div>
      <div
        class="grid grid-cols-1 sm:grid-cols-5 mt-6 mb-4 gap-4"
        v-if="requests.data"
      >
        <div class="flex flex-col gap-2 bg-gray-50 w-full p-4 rounded border">
          <div class="text-base font-medium">Total Requests</div>
          <div class="text-2xl">
            {{ requests.originalData.length }}
          </div>
        </div>
        <div class="flex flex-col gap-2 w-full p-4 rounded border">
          <div class="text-base font-medium">Pending Requests</div>
          <div class="text-2xl text-orange-600">
            {{ requests.data['Pending'].length }}
          </div>
        </div>
        <div class="flex flex-col gap-2 w-full p-4 rounded border">
          <div class="text-base font-medium">Pending Confirmation</div>
          <div class="text-2xl text-blue-600">
            {{ requests.data['Pending Confirmation'].length }}
          </div>
        </div>
        <div class="flex flex-col gap-2 w-full p-4 rounded border">
          <div class="text-base font-medium">Accepted Participants</div>
          <div class="text-2xl text-green-600">
            {{ requests.data['Accepted'].length }}
          </div>
        </div>
        <div class="flex flex-col gap-2 w-full p-4 rounded border">
          <div class="text-base font-medium">Rejected Participants</div>
          <div class="text-2xl text-red-600">
            {{ requests.data['Rejected'].length }}
          </div>
        </div>
      </div>
      <hr />
      <div class="flex flex-col gap-2 py-4">
        <AttendeeRequestList
          :localhost="localhost"
          @update-request="requests.reload()"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import {
  createDocumentResource,
  createListResource,
  createResource,
  usePageMeta,
  Dialog,
} from 'frappe-ui'
import { onMounted, ref } from 'vue'
import AttendeeRequestList from '@/components/localhost/AttendeeRequestList.vue'
import LocalhostHeader from '@/components/localhost/LocalhostHeader.vue'
import Header from '@/components/Header.vue'

const route = useRoute()

usePageMeta(() => {
  return {
    title: 'Manage Localhost',
  }
})

onMounted(() => {
  validateSessionUser()
})

const dialogMessage = ref('')
const showDialog = ref(false)

const validateSessionUser = () => {
  createResource({
    url: 'fossunited.api.hackathon.validate_user_as_localhost_member',
    params: {
      localhost_id: route.params.id,
    },
    auto: true,
    onSuccess(data) {
      localhost.fetch()
      requests.fetch()
    },
    onError(error) {
      dialogMessage.value = error.messages
      showDialog.value = true
      setTimeout(() => {
        window.location.href = '/dashboard'
      }, 2000)
    },
  })
}

const requests = createListResource({
  doctype: 'FOSS Hackathon Participant',
  fields: ['*'],
  filters: {
    localhost: route.params.id,
  },
  transform(data) {
    data = data.reduce((acc, curr) => {
      if (!acc[curr.localhost_request_status]) {
        acc[curr.localhost_request_status] = []
      }
      acc[curr.localhost_request_status].push(curr)
      return acc
    }, {})
    if (!data['Pending']) {
      data['Pending'] = []
    }
    if (!data['Accepted']) {
      data['Accepted'] = []
    }
    if (!data['Rejected']) {
      data['Rejected'] = []
    }
    if (!data['Pending Confirmation']) {
      data['Pending Confirmation'] = []
    }
    return data
  },
  pageLength: 99999,
})

const localhost = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Hackathon LocalHost',
      name: route.params.id,
      fields: ['*'],
    }
  },
})

const toggleAcceptingAttendees = () => {

  localhost.setValue.submit({
    is_accepting_attendees: !localhost.doc.is_accepting_attendees,
  })
}

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon LocalHost',
      name: route.params.id,
      fieldname: 'is_accepting_attendees',
      value: !localhost.data.is_accepting_attendees,
    },
    onSuccess() {
      localhost.fetch()
    },
    auto: true,
  })
}
</script>
