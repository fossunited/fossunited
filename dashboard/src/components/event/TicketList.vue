<template>
  <div class="prose">
    <h3 class="mb-1">Attendee List</h3>
    <p class="text-sm">List of attendees for this event.</p>
  </div>
  <SearchListView
    v-if="attendeesList.data.tickets"
    :rows="groupedRows"
    :columns="columns"
    row-key="id"
    search-placeholder="Search attendees..."
    item-label="attendees"
    export-filename="event_attendees"
    :export-columns="[{ label: 'Tier', key: 'tier' }, ...columns]"
    :options="{
      selectable: false,
      emptyState: {
        title: 'No attendees yet',
        description: 'Attendees will appear once they register.',
      },
    }"
  >
    <template #group-header="{ group }">
      <span class="text-base font-medium"> {{ group.group }} ({{ group.rows.length }}) </span>
    </template>

    <template #cell="{ item, row, column }">
      <Checkbox v-if="column.key === 'wants_tshirt'" :model-value="item" disabled />
      <div v-else>{{ item || '-' }}</div>
    </template>
  </SearchListView>
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
import SearchListView from '@/components/ui/SearchListView.vue'

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
  if (!tickets.value || tickets.value.length === 0) {
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
  if (!attendeesList.data?.tickets?.length) return toast.error('No data to download')

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
  URL.revokeObjectURL(link.href)

  toast.success('CSV downloaded successfully')
}
</script>
