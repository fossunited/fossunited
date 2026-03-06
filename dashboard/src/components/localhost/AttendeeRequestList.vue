<template>
  <RequestDetailDialog
    class="z-50 my-5"
    :participant="selectedRequest"
    :show-dialog="showDialog"
    @update:show-dialog="showDialog = $event"
    @accept-request="acceptRequest($event)"
    @reject-request="rejectRequest($event)"
  />

  <div class="flex items-center justify-between mb-4">
    <div class="text-base font-medium">
      {{ currentView === 'checkins' ? 'Check-ins' : 'Requests' }}
      <span v-if="currentView === 'checkins'" class="ml-2 text-sm font-normal text-ink-gray-5">
        ({{ checkins.data?.length || 0 }} checked-in out of {{ totalAccepted }} accepted
        participants)
      </span>
    </div>

    <div class="flex items-center gap-2">
      <div class="flex items-center gap-1 bg-surface-gray-2 rounded-lg p-1">
        <button
          class="px-3 py-1.5 text-sm rounded-md transition-colors"
          :class="
            currentView === 'requests'
              ? 'bg-surface-white text-ink-gray-9 font-medium shadow-sm'
              : 'text-ink-gray-5 hover:text-ink-gray-9'
          "
          @click="currentView = 'requests'"
        >
          Requests
        </button>
        <button
          class="px-3 py-1.5 text-sm rounded-md transition-colors"
          :class="
            currentView === 'checkins'
              ? 'bg-surface-white text-ink-gray-9 font-medium shadow-sm'
              : 'text-ink-gray-5 hover:text-ink-gray-9'
          "
          @click="currentView = 'checkins'"
        >
          Check-ins
        </button>
      </div>

      <Button
        v-if="currentView === 'checkins'"
        size="md"
        icon-left="refresh-cw"
        @click="refreshCheckins"
      >
        Refresh
      </Button>
    </div>
  </div>

  <!-- Check-Ins View -->
  <CheckInsTable
    v-if="currentView === 'checkins'"
    :checkins="checkins.data || []"
    name-field="full_name"
    docs-message="You can check-in participant during hackathon days"
    docs-url="https://docs.fossunited.org/localhost/#manage-attendees"
    :export-filename="`localhost-checkins-${props.localhost.data.name}`"
    :additional-columns="[{ key: 'organization', label: 'Organization', width: '200px' }]"
  />

  <div v-else>
    <div v-if="requests.loading && !groupedRequests.length" class="w-full p-8 flex justify-center">
      <LoadingIndicator class="w-6" />
    </div>

    <SearchListView
      v-else-if="groupedRequests.length > 0"
      class="flex-1 min-h-0"
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

        <div
          v-else-if="column.key === 'checkin' && row.localhost_request_status === 'Accepted'"
          class="flex gap-2"
        >
          <Button
            v-if="!row.has_checked_in_today"
            size="sm"
            label="Check-in"
            @click.stop="checkInParticipant(row)"
          />
          <Button
            v-else
            size="sm"
            label="Checked in"
            theme="green"
            variant="outline"
            @click.stop="confirmUndoCheckIn(row)"
          />
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
          <div
            v-if="['Pending', 'Pending Confirmation'].includes(row.localhost_request_status)"
            class="flex gap-2"
          >
            <Button
              v-if="row.localhost_request_status === 'Pending'"
              icon="check"
              label="Accept"
              theme="green"
              @click.stop="acceptRequest(row)"
            />
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
  </div>
</template>

<script setup>
import { ref, computed, watchEffect } from 'vue'
import { LoadingIndicator, createResource, Button, Badge, frappeRequest } from 'frappe-ui'
import { truncateStr, redirectRoute } from '@/helpers/utils'
import RequestDetailDialog from '@/components/localhost/RequestDetailDialog.vue'
import SearchListView from '@/components/ui/SearchListView.vue'
import CheckInsTable from '@/components/ui/CheckInsTable.vue'
import { IconArrowUpRight } from '@tabler/icons-vue'
import { toast } from 'vue-sonner'

const props = defineProps({
  localhost: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['updateRequest'])

const currentView = ref('requests')
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
  { label: 'Check-in', key: 'checkin', width: '140px' },
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

const checkins = createResource({
  url: 'fossunited.api.hackathon.get_localhost_checkins',
  params: { localhost_id: props.localhost.data.name },
  auto: true,
})

const totalAccepted = computed(() => {
  if (!requests.data) return 0
  // Count all accepted participants across all teams
  return Object.values(requests.data)
    .flat()
    .filter((r) => r.localhost_request_status === 'Accepted').length
})

watchEffect(() => {
  if (!requests.data) {
    groupedRequests.value = []
    return
  }

  // Build set of participants who checked in today (SAME AS RSVP)
  const checkedInToday = new Set()
  const today = new Date().toISOString().split('T')[0]

  ;(checkins.data || []).forEach((c) => {
    const date = new Date(c.check_in_time).toISOString().split('T')[0]
    if (date === today) {
      checkedInToday.add(c.parent)
    }
  })

  // Flatten requests and add check-in status
  const allRequests = []
  Object.entries(requests.data).forEach(([teamId, teamRequests]) => {
    teamRequests.forEach((request) => {
      allRequests.push({
        ...request,
        has_checked_in_today: checkedInToday.has(request.name),
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

  // Convert to array of groups
  groupedRequests.value = Object.entries(teamGroups)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([teamName, rows]) => {
      const hasPending = rows.some((r) => r.localhost_request_status === 'Pending')
      const hasPendingConfirmation = rows.some(
        (r) => r.localhost_request_status === 'Pending Confirmation',
      )

      return {
        group: `${teamName} (${rows.length})`,
        collapsed: !hasPending && !hasPendingConfirmation,
        rows: rows.sort((a, b) => (a.full_name || '').localeCompare(b.full_name || '')),
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

const refreshCheckins = () => {
  checkins.reload()
}

// Simple check-in function
const checkInParticipant = async (row) => {
  try {
    await frappeRequest({
      url: 'run_doc_method',
      params: {
        dt: 'FOSS Hackathon Participant',
        dn: row.name,
        method: 'add_check_in',
      },
    })

    toast.success(`Checked in ${row.full_name}`)
    requests.fetch()
    checkins.reload()
  } catch (err) {
    showError(err, `Failed to checkin ${row.full_name}`)
  }
}

// Undo check-in
const confirmUndoCheckIn = (row) => {
  if (window.confirm(`Remove check-in for ${row.full_name}?`)) {
    undoCheckIn(row)
  }
}
const undoCheckIn = async (row) => {
  try {
    await frappeRequest({
      url: 'run_doc_method',
      params: {
        dt: 'FOSS Hackathon Participant',
        dn: row.name,
        method: 'remove_today_check_in',
      },
    })

    toast.success('Check-in removed')
    requests.fetch()
    checkins.reload()
  } catch (err) {
    showError(err, `Failed to undo checkin ${row.full_name}`)
  }
}
</script>
