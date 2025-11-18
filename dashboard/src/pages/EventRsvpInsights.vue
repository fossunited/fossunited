<template>
  <div v-if="submissions.data && rsvp_form.data" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-col gap-4 mt-5">
      <div class="flex items-center justify-between">
        <div class="font-semibold text-gray-800">Attendees</div>
        <Button size="md" icon-left="download" @click="downloadAttendeeList">Download</Button>
      </div>

      <ListView
        v-model:rows="groupedRows"
        :columns="listColumns"
        row-key="name"
        :options="{
          selectable: false,
          showTooltip: true,
          resizeColumn: true,
          emptyState: {
            description: 'No one has RSVPed for the event yet.',
          },
        }"
      >
        <template #group-header="{ group }">
          <span class="text-base font-medium leading-6 text-ink-gray-9">
            {{ group.group }} ({{ group.rows.length }})
          </span>
        </template>

        <template #cell="{ item, row, column }">
          <div v-if="column.key === 'confirm_attendance'">
            <span
              class="px-2 py-1 rounded text-sm font-medium"
              :class="
                Number(row.confirm_attendance || 0) === 1
                  ? 'bg-green-100 text-green-700'
                  : 'bg-red-100 text-red-700'
              "
            >
              {{ Number(row.confirm_attendance || 0) === 1 ? 'Yes' : 'No' }}
            </span>
          </div>

          <div v-else-if="column.key === 'actions'">
            <!-- show actions when host approval is required -->
            <div class="flex gap-2">
              <Button
                size="sm"
                label="Accept"
                variant="solid"
                :disabled="row.status === 'Accepted'"
                @click="() => updateRsvpStatus(row, 'Accepted')"
              />
              <Button
                size="sm"
                label="Reject"
                theme="red"
                :disabled="row.status === 'Rejected'"
                @click="() => updateRsvpStatus(row, 'Rejected')"
              />
            </div>
          </div>

          <div v-else>
            <span class="text-base">{{ item }}</span>
          </div>
        </template>
      </ListView>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { inject, ref, computed, watchEffect } from 'vue'
import { createListResource, createResource, ListView, Button } from 'frappe-ui'
import { toast } from 'vue-sonner'

const route = useRoute()
const session = inject('$session')

const rsvp_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event RSVP',
    fields: ['*'],
    filters: {
      event: route.params.id,
    },
  },
  auto: true,
})

const isEventLead = ref(false)
const event_lead = createResource({
  url: 'fossunited.api.chapter.check_if_chapter_or_event_core_member',
  makeParams() {
    return {
      event: route.params.id,
    }
  },
  onSuccess(data) {
    isEventLead.value = data
  },
  auto: true,
})

const submissions = createResource({
  url: 'fossunited.api.chapter.get_submissions_with_answers',
  params: {
    event_id: route.params.id,
    full_answers: false,
  },
  auto: true,
})

const listColumns = computed(() => {
  const columns = new Map()

  // Collect keys from all submissions
  if (Array.isArray(submissions.data)) {
    submissions.data.forEach((submission) => {
      Object.keys(submission).forEach((key) => {
        if (key !== 'confirm_attendance' && key !== 'status' && !columns.has(key)) {
          columns.set(key, { key, label: key }) // Use key as label directly
        }
      })
    })
  }

  // include confirm_attendance and status
  const result = [
    { key: 'confirm_attendance', label: 'Attending', icon: 'check-circle' },
    ...Array.from(columns.values()),
  ]

  // for host approval, add an actions column
  if (rsvp_form.data?.requires_host_approval) {
    result.push({ key: 'actions', label: 'Actions' })
  }

  return result
})

const groupedRows = ref([])

const updateRsvpStatus = (row, status) => {
  if (!row?.name) {
    toast.error('Invalid row')
    return
  }

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Event RSVP Submission',
      name: row.name,
      fieldname: {
        status,
        confirm_attendance: status === 'Accepted' ? 1 : 0,
      },
    },
    onSuccess() {
      toast.success(`RSVP ${status}`)
      submissions.fetch()
    },
    onError(err) {
      toast.error(err.message || 'Update failed')
    },
  }).fetch()
}

watchEffect(() => {
  const rows = Array.isArray(submissions.data) ? submissions.data : []

  const pending = []
  const accepted = []
  const rejected = []
  const notAttending = []

  const requiresHostApproval = Boolean(rsvp_form.data?.requires_host_approval)

  for (const row of rows) {
    const confirm = Number(row?.confirm_attendance || 0) === 1
    const status = String(row?.status || '').trim()

    if (requiresHostApproval) {
      if (status === 'Pending') {
        pending.push(row)
      } else if (status === 'Accepted' && confirm) {
        accepted.push(row)
      } else if (status === 'Rejected') {
        rejected.push(row)
      } else {
        // everything else falls into Not attending (covers accepted but confirm=false,
        // missing status, or other odd cases)
        notAttending.push(row)
      }
    } else {
      // legacy behaviour: grouping based purely on confirm_attendance
      if (confirm) {
        accepted.push(row)
      } else {
        notAttending.push(row)
      }
    }
  }

  if (requiresHostApproval) {
    groupedRows.value = [
      { group: 'Pending requests', collapsed: false, rows: pending },
      { group: 'Attending event', collapsed: false, rows: accepted },
      { group: 'Not attending', collapsed: true, rows: notAttending },
      { group: 'Rejected attendees', collapsed: true, rows: rejected },
    ]
  } else {
    groupedRows.value = [
      { group: 'Attending event', collapsed: false, rows: accepted },
      { group: 'Not attending', collapsed: true, rows: notAttending },
    ]
  }
})

const downloadAttendeeList = () => {
  const eventId = route.params.id
  window.open(
    `/api/method/fossunited.api.chapter.download_attendee_list_csv?event_id=${eventId}`,
    '_self',
  )
}
</script>
