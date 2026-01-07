<template>
  <RequestDetailDialog
    class="z-50 my-5"
    :participant="selectedRequest"
    :show-dialog="showDialog"
    @update:show-dialog="showDialog = $event"
    @accept-request="acceptRequest($event)"
    @reject-request="rejectRequest($event)"
  />

  <div class="prose mb-4">
    <h4>Requests</h4>
  </div>

  <div v-if="requests.loading" class="w-full p-8 flex justify-center">
    <LoadingIndicator class="w-6" />
  </div>

  <SearchListView
    v-else-if="groupedRequests.length > 0"
    class="h-[440px]"
    :columns="columns"
    :rows="groupedRequests"
    row-key="name"
    :options="{
      selectable: false,
      showTooltip: true,
      resizeColumn: true,
      onRowClick: (row) => {
        selectedRequest = row
        showDialog = true
      },
    }"
    search-placeholder="Search requests..."
    :search-fields="['full_name', 'team_name', 'organization', 'project_title']"
    export-filename="localhost_requests"
    item-label="requests"
  >
    <template #cell="{ item, row, column }">
      <div v-if="column.key === 'localhost_request_status'">
        <Badge
          :theme="getStatusTheme(row.localhost_request_status)"
          :label="row.localhost_request_status"
          size="lg"
        />
      </div>

      <div v-else-if="column.key === 'is_student'" class="ml-4">
        <span class="text-sm text-gray-600">{{ row.is_student ? 'Yes' : 'No' }}</span>
      </div>

      <div v-else-if="column.key === 'git_profile'">
        <a
          v-if="row.git_profile"
          :href="row.git_profile"
          target="_blank"
          class="text-sm flex items-center font-semibold hover:underline"
        >
          <span>Open</span>
          <IconArrowUpRight class="w-4 h-4" />
        </a>
        <span v-else class="text-sm text-gray-500">—</span>
      </div>

      <div v-else-if="column.key === 'project_title'">
        <a
          v-if="row.project_route"
          class="text-sm flex items-center font-semibold hover:underline cursor-pointer"
          @click="redirectRoute(row.project_route)"
        >
          <span>{{ truncateStr(row.project_title, 25) }}</span>
          <IconArrowUpRight class="w-4 h-4" />
        </a>
        <span v-else class="text-sm text-gray-500">—</span>
      </div>

      <div v-else-if="column.key === 'actions'">
        <div v-if="row.localhost_request_status === 'Pending'" class="flex gap-2">
          <Button icon="check" label="Accept" theme="green" @click.stop="acceptRequest(row)" />
          <Button icon="x" label="Reject" theme="red" @click.stop="rejectRequest(row)" />
        </div>
      </div>

      <div v-else class="text-sm">{{ item || '—' }}</div>
    </template>
  </SearchListView>

  <div v-else class="text-center py-12 text-gray-500">
    <p class="text-lg font-medium">No Requests</p>
    <p class="text-sm mt-1">There are no localhost requests yet.</p>
  </div>
</template>

<script setup>
import { ref, computed, watchEffect } from 'vue'
import { LoadingIndicator, createResource, Button, Badge } from 'frappe-ui'
import { truncateStr, redirectRoute } from '@/helpers/utils'
import RequestDetailDialog from '@/components/localhost/RequestDetailDialog.vue'
import SearchListView from '@/components/ui/SearchListView.vue'
import { IconArrowUpRight } from '@tabler/icons-vue'

const props = defineProps({
  localhost: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['updateRequest'])

const showDialog = ref(false)
const selectedRequest = ref({})
const groupedRequests = ref([])

const columns = [
  { label: 'Name', key: 'full_name' },
  { label: 'Status', key: 'localhost_request_status', width: 1 },
  { label: 'Team', key: 'team_name' },
  { label: 'Student', key: 'is_student', width: 1 / 2 },
  { label: 'Organization', key: 'organization' },
  { label: 'Project', key: 'project_title' },
  { label: 'Git Profile', key: 'git_profile' },
  { label: 'Actions', key: 'actions' },
]

const STATUS_ORDER = {
  Pending: 0,
  'Pending Confirmation': 1,
  Accepted: 2,
  Rejected: 3,
}

const getStatusTheme = (status) => {
  const themes = {
    Pending: 'orange',
    'Pending Confirmation': 'blue',
    Accepted: 'green',
    Rejected: 'red',
  }
  return themes[status] || 'gray'
}

const requests = createResource({
  url: 'fossunited.api.hackathon.get_localhost_requests_by_team',
  params: {
    hackathon: props.localhost.data.parent_hackathon,
    localhost: props.localhost.data.name,
  },
  auto: true,
})

watchEffect(() => {
  if (!requests.data) {
    groupedRequests.value = []
    return
  }
  // Flatten the dict structure into a single array
  const allRequests = []
  Object.entries(requests.data).forEach(([teamId, teamRequests]) => {
    teamRequests.forEach((request) => {
      allRequests.push({
        ...request,
        team_name: request.team?.team_name || 'Unknown Team',
      })
    })
  })
  // Group by status
  const groups = {}
  allRequests.forEach((request) => {
    const status = request.localhost_request_status || 'Pending'
    if (!groups[status]) {
      groups[status] = []
    }
    groups[status].push(request)
  })

  // Convert to array of groups, sorted by status order
  groupedRequests.value = Object.entries(groups)
    .sort(([a], [b]) => (STATUS_ORDER[a] ?? 99) - (STATUS_ORDER[b] ?? 99))
    .filter(([_, rows]) => rows.length > 0)
    .map(([status, rows]) => ({
      group: `${status} (${rows.length})`,
      collapsed: status === 'Accepted' || status === 'Rejected',
      rows: rows.sort((a, b) => {
        // Sort by team name, then by full name
        const teamCompare = (a.team_name || '').localeCompare(b.team_name || '')
        if (teamCompare !== 0) return teamCompare
        return (a.full_name || '').localeCompare(b.full_name || '')
      }),
    }))
})

const updateRequestStatus = (id, status) => {
  return createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon Participant',
      name: id,
      fieldname: 'localhost_request_status',
      value: status,
    },
    onSuccess() {
      requests.fetch()
      emit('updateRequest')
    },
  })
}

const acceptRequest = (member) => {
  updateRequestStatus(member.name, 'Pending Confirmation').fetch()
}

const rejectRequest = (member) => {
  updateRequestStatus(member.name, 'Rejected').fetch()
}
</script>
