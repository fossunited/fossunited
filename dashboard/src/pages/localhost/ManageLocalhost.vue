<template>
  <div v-if="localhost.data && requests.data">
    <div class="flex items-center justify-between mt-4">
      <div class="text-base-medium">Manage Localhost</div>

      <RouterLink :to="{ name: 'LocalhostEdit', params: { id: route.params.id } }">
        <Button label="Edit Details" :icon-left="IconEdit" />
      </RouterLink>
    </div>

    <LocalhostHeader :localhost="localhost.data" />

    <div class="grid grid-cols-1 md:grid-cols-2">
      <div class="rounded-1 border-2 border-dashed border-outline-gray-3 p-4 my-2">
        <div class="text-sm-medium uppercase">Current Status</div>
        <div class="flex items-center justify-between w-full">
          <div
            class="flex items-center gap-2 text-md-medium pt-4"
            :class="localhost.data.is_accepting_attendees ? 'text-ink-green-6' : ''"
          >
            <span v-if="localhost.data.is_accepting_attendees" class="relative flex h-3 w-3">
              <span
                class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
              ></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-surface-green-3"></span>
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
            :label="localhost.data.is_accepting_attendees ? 'Disable' : 'Enable'"
            @click="toggleAcceptingAttendees"
          />
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-5 mt-6 mb-4 gap-4">
      <div class="flex flex-col gap-2 bg-surface-gray-1 w-full p-4 rounded-4 border">
        <div class="text-base-medium">Total Requests</div>
        <div class="text-2xl">
          {{ requests.originalData.length }}
        </div>
      </div>
      <div class="flex flex-col gap-2 w-full p-4 rounded-4 border">
        <div class="text-base-medium">Pending Requests</div>
        <div class="text-2xl text-ink-amber-6">
          {{ requests.data['Pending'].length }}
        </div>
      </div>
      <div class="flex flex-col gap-2 w-full p-4 rounded-4 border">
        <div class="text-base-medium">Pending Confirmation</div>
        <div class="text-2xl text-ink-blue-5">
          {{ requests.data['Pending Confirmation'].length }}
        </div>
      </div>
      <div class="flex flex-col gap-2 w-full p-4 rounded-4 border">
        <div class="text-base-medium">Accepted Participants</div>
        <div class="text-2xl text-ink-green-6">
          {{ requests.data['Accepted'].length }}
        </div>
      </div>
      <div class="flex flex-col gap-2 w-full p-4 rounded-4 border">
        <div class="text-base-medium">Rejected Participants</div>
        <div class="text-2xl text-ink-red-8">
          {{ requests.data['Rejected'].length }}
        </div>
      </div>
    </div>

    <hr />

    <div class="flex flex-col gap-2 py-4">
      <AttendeeRequestList :localhost="localhost" @update-request="requests.reload()" />
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { createListResource, createResource, usePageMeta } from 'frappe-ui'
import { IconEdit } from '@tabler/icons-vue'
import AttendeeRequestList from '@/components/localhost/AttendeeRequestList.vue'

const route = useRoute()

usePageMeta(() => {
  return {
    title: 'Manage Localhost',
  }
})

const requests = createListResource({
  doctype: 'FOSS Hackathon Participant',
  fields: ['*'],
  filters: {
    localhost: route.params.id,
  },
  auto: true,
  transform(data) {
    data = data.reduce((acc, curr) => {
      if (!acc[curr.localhost_request_status]) {
        acc[curr.localhost_request_status] = []
      }
      acc[curr.localhost_request_status].push(curr)
      return acc
    }, {})
    if (!data['Pending']) data['Pending'] = []
    if (!data['Accepted']) data['Accepted'] = []
    if (!data['Rejected']) data['Rejected'] = []
    if (!data['Pending Confirmation']) data['Pending Confirmation'] = []
    return data
  },
  pageLength: 99999,
})

const localhost = createResource({
  url: 'frappe.client.get',
  auto: true,
  makeParams() {
    return {
      doctype: 'FOSS Hackathon LocalHost',
      name: route.params.id,
      fields: ['*'],
    }
  },
})

const toggleAcceptingAttendees = () => {
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
