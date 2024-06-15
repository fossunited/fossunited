<template>
  <Header />
  <div class="w-full p-4 flex items-center justify-center" v-if="localhost.doc">
    <div class="max-w-screen-xl w-full">
      <div class="text-base font-medium mt-4">Manage LocalHost</div>
      <div class="prose mt-4">
        <h2>{{ localhost.doc.localhost_name }}</h2>
      </div>
      <div class="flex gap-2 my-2 text-base font-medium items-center">
        <div class="flex gap-1 items-center">
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
            class="icon w-5 h-5 icon-tabler icons-tabler-outline icon-tabler-map-pin"
          >
            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
            <path d="M9 11a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" />
            <path
              d="M17.657 16.657l-4.243 4.243a2 2 0 0 1 -2.827 0l-4.244 -4.243a8 8 0 1 1 11.314 0z"
            />
          </svg>
          {{ localhost.doc.location }}
        </div>
      </div>
      <div
        class="grid grid-cols-1 sm:grid-cols-4 mt-6 mb-4 gap-4"
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
      <hr>
      <div class="flex flex-col gap-2 py-4">
        <AttendeeRequestList :localhost="localhost"/>
      </div>
    </div>
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import {
  createDocumentResource,
  createListResource,
} from 'frappe-ui'
import AttendeeRequestList from '@/components/localhost/AttendeeRequestList.vue';
import Header from '@/components/Header.vue'

const route = useRoute()

const requests = createListResource({
  doctype: 'FOSS Hackathon Participant',
  fields: ['*'],
  filters: {
    wants_to_attend_locally: 1,
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
    return data
  },
  pageLength: 99999,
  auto: true,
})

const localhost = createDocumentResource({
  doctype: 'FOSS Hackathon LocalHost',
  name: route.params.id,
  auto: true,
})

</script>
