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

  <div v-if="requests.loading && !groupedRequests.length" class="w-full p-8 flex justify-center">
    <LoadingIndicator class="w-6" />
  </div>

  <SearchListView
    v-else-if="groupedRequests.length > 0"
    :columns="columns"
    :rows="groupedRequests"
    row-key="name"
    :options="{
      onRowClick: (row) => {
        selectedRequest = row
        showDialog = true
      },
    }"
    search-placeholder="Search requests..."
    :search-fields="['full_name', 'team_name', 'organization', 'project_title', 'status']"
    export-filename="localhost_requests"
    item-label="participant requests"
    :export-columns="exportColumns"
    filter-field="localhost_request_status"
    :filter-options="['All', 'Pending', 'Pending Confirmation', 'Accepted', 'Rejected']"
  >
    <template #cell="{ item, row, column }">
      <div v-if="column.key === 'localhost_request_status'">
        <Badge
          :theme="getStatusTheme(row.localhost_request_status)"
          :label="row.localhost_request_status"
          size="sm"
        />
      </div>

      <div v-else-if="column.key === 'is_student'" class="ml-4">
        <span class="text-sm text-ink-gray-5">{{ row.is_student ? 'Yes' : 'No' }}</span>
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
        <span v-else class="text-sm text-ink-gray-4">—</span>
      </div>

      <div v-else-if="column.key === 'project_title'">
        <a
          v-if="row.project_route"
          class="text-sm flex items-center font-semibold hover:underline cursor-pointer"
          @click="redirectRoute(row.project_route)"
        >
          <span class="truncate">{{ row.project_title }}</span>
          <IconArrowUpRight class="w-4 h-4" />
        </a>
        <span v-else class="text-sm text-ink-gray-4">—</span>
      </div>

      <div v-else-if="column.key === 'actions'">
        <div v-if="row.localhost_request_status === 'Pending'" class="flex gap-2">
          <Button icon="check" label="Accept" theme="green" @click.stop="acceptRequest(row)" />
          <Button icon="x" label="Reject" theme="red" @click.stop="rejectRequest(row)" />
        </div>
      </div>

      <div v-else class="text-sm truncate text-wrap" :title="item || '—'">
        {{ item || '—' }}
      </div>
    </template>
  </SearchListView>

  <div v-else class="text-center py-12 text-ink-gray-4">
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
  { label: 'Name', key: 'full_name', width: '180px' },
  { label: 'Status', key: 'localhost_request_status', width: '150px' },
  { label: 'Email', key: 'email', width: '200px' },
  { label: 'Student', key: 'is_student', width: '80px' },
  { label: 'Organization', key: 'organization', width: '200px' },
  { label: 'Project', key: 'project_title', width: '220px' },
  { label: 'Git Profile', key: 'git_profile', width: '90px' },
  { label: 'Actions', key: 'actions', width: '100px' },
]

// Export columns include team_name and exclude actions
const exportColumns = [
  { label: 'Name', key: 'full_name' },
  { label: 'Email', key: 'email' },
  { label: 'Team', key: 'team_name' },
  { label: 'Status', key: 'localhost_request_status' },
  { label: 'Student', key: 'is_student' },
  { label: 'Organization', key: 'organization' },
  { label: 'Project', key: 'project_title' },
  { label: 'Git Profile', key: 'git_profile' },
]

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

  // Flatten the dict structure into a single array with team info
  const allRequests = []
  Object.entries(requests.data).forEach(([teamId, teamRequests]) => {
    teamRequests.forEach((request) => {
      allRequests.push({
        ...request,
        team_name: request.team?.team_name || 'Unknown Team',
      })
    })
  })

  // Group by team name
  const teamGroups = {}
  allRequests.forEach((request) => {
    const teamName = request.team_name
    if (!teamGroups[teamName]) {
      teamGroups[teamName] = []
    }
    teamGroups[teamName].push(request)
  })

  // Convert to array of groups, sorted alphabetically by team name
  groupedRequests.value = Object.entries(teamGroups)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([teamName, rows]) => {
      // Count statuses in this team
      const hasPending = rows.some((r) => r.localhost_request_status === 'Pending')
      const hasPendingConfirmation = rows.some(
        (r) => r.localhost_request_status === 'Pending Confirmation',
      )

      return {
        group: `${teamName} (${rows.length})`,
        // Collapse groups that have no pending or pending confirmation requests
        collapsed: !hasPending && !hasPendingConfirmation,
        rows: rows.sort((a, b) => {
          // Sort by full name within each team
          return (a.full_name || '').localeCompare(b.full_name || '')
        }),
      }
    })
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
