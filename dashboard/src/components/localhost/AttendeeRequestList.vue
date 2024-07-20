<template>
  <RequestDetailDialog
    class="z-50 my-5"
    :participant="selectedRequest"
    :showDialog="showDialog"
    @update:showDialog="showDialog = $event"
    @acceptRequest="acceptRequest($event)"
    @rejectRequest="rejectRequest($event)"
  />
  <div class="prose">
    <h4>Requests</h4>
  </div>
  <div class="flex gap-3 flex-wrap items-center">
    <div class="flex gap-1">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.7"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="icon w-4 h-4 icon-tabler icons-tabler-outline icon-tabler-filter"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path
          d="M4 4h16v2.172a2 2 0 0 1 -.586 1.414l-4.414 4.414v7l-6 2v-8.5l-4.48 -4.928a2 2 0 0 1 -.52 -1.345v-2.227z"
        />
      </svg>
      <span class="text-sm font-medium">Filter:</span>
    </div>
    <select
      class="border-none text-sm px-4 rounded w-44 h-fit items-center flex flex-col bg-gray-100 border-2"
      v-model="selectedListFilter"
    >
      <option v-for="(_, label) in FILTERS">
        {{ label }}
      </option>
    </select>
  </div>
  <div class="w-full place-items-center">
    <div class="my-2" v-if="requestByGroup.data">
      <ListView
        class="min-h-[440px]"
        :columns="[
          {
            label: 'Name',
            key: 'full_name',
          },
          {
            label: 'Status',
            key: 'localhost_request_status',
            width: 1,
          },
          {
            label: 'Is Student',
            key: 'is_student',
            width: 1 / 2,
          },
          {
            label: 'Organization / Institute',
            key: 'organization',
          },
          {
            label: 'Project',
            key: 'project_title',
          },
          {
            label: 'Git Profile',
            key: 'git_profile',
          },
          {
            label: 'Actions',
            key: 'actions',
          },
        ]"
        :rows="requestByGroup.data"
        :options="{
          selectable: false,
          showTooltip: true,
          resizeColumn: true,
          onRowClick: (row) => {
            selectedRequest = row
            showDialog = true
          },
          emptyState: {
            title: FILTERS[selectedListFilter].emptyStateText,
          },
        }"
        row-key="name"
      >
        <template #cell="{ item, row, column }">
          <div v-if="column.label == 'Status'">
            <Badge
              :theme="
                row[column.key] === 'Pending'
                  ? 'orange'
                  : row[column.key] === 'Accepted'
                    ? 'green'
                    : row[column.key] === 'Pending Confirmation'
                      ? 'blue'
                      : 'red'
              "
              :label="row[column.key]"
              size="lg"
            />
          </div>
          <div v-else-if="column.label == 'Git Profile'">
            <a
              v-if="row.git_profile"
              :href="row.git_profile"
              target="_blank"
              class="text-sm flex font-semibold hover:underline"
            >
              <span>Open</span
              ><svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="icon w-4 h-4 icon-tabler icons-tabler-outline icon-tabler-arrow-up-right"
              >
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M17 7l-10 10" />
                <path d="M8 7l9 0l0 9" />
              </svg>
            </a>
            <div v-else class="text-sm">No Git Profile</div>
          </div>
          <div v-else-if="column.label == 'Is Student'" class="ml-4">
            <span class="text-sm text-gray-600">{{
              row.is_student ? 'Yes' : 'No'
            }}</span>
          </div>
          <div v-else-if="column.label == 'Actions'">
            <div
              v-if="row.localhost_request_status == 'Pending'"
              class="flex gap-2"
            >
              <Button
                icon="check"
                :label="'Accept'"
                :theme="'green'"
                @click="acceptRequest(row)"
              />
              <Button
                icon="x"
                :label="'Reject'"
                :theme="'red'"
                @click="rejectRequest(row)"
              />
            </div>
          </div>
          <div class="flex" v-else-if="column.label == 'Project'">
            <a
              v-if="row.project_route"
              @click="redirectRoute(row.project_route)"
              class="text-sm flex font-semibold hover:underline"
            >
              <span>{{ truncateStr(row.project_title, 20) }}</span
              ><svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="icon w-4 h-4 icon-tabler icons-tabler-outline icon-tabler-arrow-up-right"
              >
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M17 7l-10 10" />
                <path d="M8 7l9 0l0 9" />
              </svg>
            </a>
            <div v-else class="text-sm">No Project Yet</div>
          </div>
          <div v-else class="text-base">{{ item }}</div>
        </template>
      </ListView>
    </div>
    <div v-else class="text-sm font-medium text-gray-700 w-full my-5 uppercase">
      <p>No Requests</p>
    </div>
    <div class="w-full p-4 flex justify-center" v-if="requestByGroup.loading">
      <LoadingIndicator class="w-5" />
    </div>
  </div>
</template>

<script setup>
import { defineProps, watch } from 'vue'
import {
  LoadingIndicator,
  createResource,
  Badge,
  Button,
  ListView,
} from 'frappe-ui'
import { ref } from 'vue'
import RequestDetailDialog from '@/components/localhost/RequestDetailDialog.vue'
import { truncateStr } from '@/helpers/utils'
import { redirectRoute } from '@/helpers/utils'

const showDialog = ref(false)
const selectedRequest = ref({})

const props = defineProps({
  localhost: {
    type: Object,
    required: true,
  },
})

// Filters for status checks
const FILTERS = {
  'All Requests': {
    emptyStateText: 'No requests found',
    filters: ['Pending', 'Rejected', 'Accepted', 'Pending Confirmation'],
  },
  'Pending': {
    emptyStateText: 'No pending requests',
    filters: ['Pending'],
  },
  'Accepted': {
    emptyStateText: 'No accepted requests',
    filters: ['Accepted'],
  },
  'Rejected': {
    emptyStateText: 'No rejected requests',
    filters: ['Rejected'],
  },

  'Pending Confirmation': {
    emptyStateText: 'No pending confirmations',
    filters: ['Pending Confirmation'],
  },
}

const selectedListFilter = ref('All Requests')

const requestByGroup = createResource({
  url: 'fossunited.api.hackathon.get_localhost_requests_by_team',
  params: {
    hackathon: props.localhost.data.parent_hackathon,
    localhost: props.localhost.data.name,
  },
  auto: true,
  transform(data) {
    if (!data) return []
    let rows = []
    if (data) {
      Object.entries(data).forEach((key) => {
        rows.push({
          group: key[1][0].team.team_name,
          collapsed: false,
          rows: key[1],
        })
      })
    }
    return rows
  },
})

const changeLocalhostRequestStatus = (id, status) => {
  return createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon Participant',
      name: id,
      fieldname: 'localhost_request_status',
      value: status,
    },
    onSuccess(data) {
      requestByGroup.fetch()
    },
  })
}

const acceptRequest = (member) => {
  changeLocalhostRequestStatus(member.name, 'Pending Confirmation').fetch()
}

const rejectRequest = (member) => {
  changeLocalhostRequestStatus(member.name, 'Rejected').fetch()
}

watch(selectedListFilter, (newFilter) => {
  requestByGroup.update({
    params: {
      hackathon: props.localhost.data.parent_hackathon,
      localhost: props.localhost.data.name,
      status: FILTERS[newFilter].filters,
    },
  })
  requestByGroup.fetch()
})
</script>
