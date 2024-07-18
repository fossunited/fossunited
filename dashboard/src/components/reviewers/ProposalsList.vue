<template>
  <div v-if="cfp_submissions.data">
    <div class="flex flex-col gap-2">
      <div class="text-base font-medium">Filters</div>
      <div class="flex gap-4 mb-5">
        <div class="flex gap-2 items-center">
          <label class="text-sm">Status:</label>
          <select
            class="border-none text-sm px-4 rounded w-44 h-fit items-center flex flex-col bg-gray-100 border-2"
            v-model="selectedStatusFilter"
          >
            <option
              v-for="(filter, index) in statusFilters"
              @click="filterByStatus(filter)"
            >
              {{ filter.label }}
            </option>
          </select>
        </div>
        <div v-if="selectedStatusFilter=='Reviewed'" class="flex gap-2 items-center">
          <label class="text-sm">Review Filter:</label>
          <select
            class="border-none text-sm px-4 rounded w-44 h-fit items-center flex flex-col bg-gray-100 border-2"
            v-model="selectedToApproveFilter"
          >
            <option
              v-for="(filter, index) in toApproveFilter"
              @click="filterByToApprove(filter)"
            >
              {{ filter.label }}
            </option>
          </select>
        </div>
      </div>
    </div>
    <ListView
      class="h-[480px]"
      :columns="[
        {
          label: 'Talk Title',
          key: 'talk_title',
        },
        {
          label: 'Status',
          key: 'review_status',
          width: 1 / 2,
        },
        {
          label: 'Review',
          key: 'reviewer_status',
        },
        {
          label: 'Remarks',
          key: 'reviewer_remarks',
        },
      ]"
      :rows="cfp_submissions.data"
      row-key="name"
      :options="{
        selectable: false,
        showTooltip: true,
        resizeColumn: true,
        onRowClick: (row) => {
          $router.push({
            name: 'SubmissionPage',
            params: {
              talk_id: row.name,
            },
          })
        },
        emptyState: {
          title: 'No Submissions',
          description: 'No submissions found.',
        }
      }"
    >
      <template #cell="{ item, row, column }">
        <div v-if="column.label == 'Status'">
          <Badge :theme="item == 'Reviewed' ? 'green' : 'gray'" :label="item" />
        </div>
        <div v-else-if="column.label == 'Review'">
          <Badge
            v-if="item"
            :theme="
              item == 'Yes'
                ? 'green'
                : item == 'Maybe'
                  ? 'orange'
                  : item == 'No'
                    ? 'red'
                    : 'gray'
            "
          >
            {{ { Yes: 'Approved', No: 'Reject', Maybe: 'Not Sure' }[item] }}
          </Badge>
          <div v-else class="text-sm text-gray-500">-</div>
        </div>
        <div v-else-if="column.label == 'Remarks'">
          <div v-if="item" class="text-sm truncate">{{ item }}</div>
          <div v-else class="text-sm text-gray-500">-</div>
        </div>
        <div v-else class="text-base truncate">
          {{ item }}
        </div>
      </template>
    </ListView>
  </div>
</template>
<script setup>
import { defineProps, ref } from 'vue'
import { createResource, ListView, Badge } from 'frappe-ui'

const props = defineProps({
  event: {
    type: String,
    required: true,
  },
})

const statusFilters = [
  {
    label: 'All',
    value: ['Reviewed', 'Not Reviewed'],
  },
  {
    label: 'Reviewed',
    value: ['Reviewed'],
  },
  {
    label: 'Not Reviewed',
    value: ['Not Reviewed'],
  },
]

const toApproveFilter = [
  {
    label: 'All',
    value: ['Yes', 'No', 'Maybe'],
  },
  {
    label: 'Approved',
    value: ['Yes'],
  },
  {
    label: 'Rejected',
    value: ['No'],
  },
  {
    label: 'Not Sure',
    value: ['Maybe'],
  },
]

const selectedStatusFilter = ref(statusFilters[0].label)
const selectedToApproveFilter = ref(toApproveFilter[0].label)

const cfp_submissions = createResource({
  url: 'fossunited.api.reviewer.get_cfp_submissions_by_reviewer_status',
  params: {
    event: props.event,
  },
  auto: true,
})

const filterByStatus = (filter) => {
  selectedToApproveFilter.value = toApproveFilter[0].label
  cfp_submissions.update({
    params: {
      event: props.event,
      status_filter: filter.value,
    }
  })
  cfp_submissions.fetch()
}

const filterByToApprove = (filter) => {
  cfp_submissions.update({
    params: {
      event: props.event,
      status_filter: ['Reviewed'],
      to_approve_filter: filter.value,
    }
  })
  cfp_submissions.fetch()
}
</script>
