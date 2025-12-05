<template>
  <div class="prose">
    <h3 class="mb-1">Attendee List</h3>
    <p class="text-sm">List of attendees for this event.</p>
  </div>
  <div class="flex flex-col flex-wrap md:flex-row gap-5 my-2 md:items-end">
    <FormControl
      v-model="searchName"
      type="search"
      label="Search"
      placeholder="Search by Name"
      class="md:w-1/4"
      @input="attendeesList.fetch()"
    />
    <Button size="md" icon-left="download" @click="downloadCSV">Download</Button>
  </div>
  <ListView
    v-if="attendeesList.data.tickets"
    class="h-[540px]"
    :columns="columns"
    :rows="groupedRows"
    :options="{
      selectable: false,
      showTooltip: false,
      resizeColumn: false,
      emptyState: {
        title: 'No attendees for this event',
        description: 'Attendees will be listed here once they buy tickets.',
      },
    }"
  >
    <template #group-header="{ group }">
      <span class="text-base font-medium leading-6 text-ink-gray-9">
        {{ group.group }} ({{ group.rows.length }})
      </span>
    </template>
    <template #cell="{ item, row, column }">
      <Checkbox v-if="column.key === 'wants_tshirt'" :model-value="item" disabled />
      <div v-else-if="column.key === 'tshirt_size'" class="text-base">
        {{ row.wants_tshirt ? item : '-' }}
      </div>
      <div v-else class="text-base">{{ item || '-' }}</div>
    </template>
  </ListView>
  <div v-if="attendeesList.loading" class="w-full h-[220px] flex items-center justify-center">
    <LoadingIndicator class="w-5 h-5" />
  </div>
</template>

<script setup>
import {
  createResource,
  ListView,
  LoadingIndicator,
  Checkbox,
  FormControl,
  Button,
} from 'frappe-ui'
import { toast } from 'vue-sonner'

import { defineProps, computed, ref, watchEffect } from 'vue'

const props = defineProps({
  event: { type: Object, required: true },
})

const searchName = ref('')
const groupedRows = ref([])

const attendeesList = createResource({
  url: 'fossunited.api.tickets.get_tickets_with_custom_fields',
  makeParams() {
    return {
      event_id: props.event.data.name,
      filters: { full_name: ['like', `%${searchName.value}%`] },
    }
  },
  params: () => ({}),
  auto: true,
  debounce: 500,
  onError: (e) => toast.error(e.message),
})

const customFields = computed(() => attendeesList.data?.custom_fields || [])

const tickets = computed(() => attendeesList.data?.tickets || [])

const columns = computed(() => [
  { label: 'Name', key: 'full_name' },
  { label: 'Designation', key: 'designation' },
  { label: 'Organization', key: 'organization' },
  { label: 'T-shirt Addon', key: 'wants_tshirt', width: 1 / 4 },
  { label: 'Tshirt Size', key: 'tshirt_size', width: 1 / 4 },
  ...customFields.value.map((f) => ({ label: f, key: `custom_field_${f}` })),
])

watchEffect(() => {
  if (!tickets.value) {
    groupedRows.value = []
    return
  }

  const grouped = {}
  tickets.value.forEach((ticket) => {
    if (!grouped[ticket.tier]) {
      grouped[ticket.tier] = { group: ticket.tier, collapsed: false, rows: [] }
    }
    grouped[ticket.tier].rows.push(ticket)
  })

  groupedRows.value = Object.values(grouped)
})

const escapeCSV = (str) => {
  const s = String(str)
  return s.includes(',') || s.includes('"') || s.includes('\n') ? `"${s.replace(/"/g, '""')}"` : s
}

const downloadCSV = () => {
  if (!attendeesList.data.tickets?.length) return toast.error('No data to download')

  const headers = [
    'Tier',
    'Name',
    'Email',
    'Designation',
    'Organization',
    'Wants T-shirt',
    'T-shirt Size',
    ...customFields.value,
  ]

  const rows = attendeesList.data.tickets.map((t) => [
    t.tier,
    t.full_name,
    t.email,
    t.designation || '',
    t.organization || '',
    t.wants_tshirt ? 'Yes' : 'No',
    t.tshirt_size || '',
    ...customFields.value.map((f) => t[`custom_field_${f}`] || ''),
  ])

  const csv = [headers, ...rows].map((row) => row.map(escapeCSV).join(',')).join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `attendees_${props.event.data.name}_${new Date().toISOString().split('T')[0]}.csv`
  link.click()

  toast.success('CSV downloaded successfully')
}
</script>
