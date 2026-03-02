<template>
  <div>
    <DocsInfo :message="docsMessage" :docs-url="docsUrl" />

    <SearchListView
      :rows="checkinGroups"
      :columns="columns"
      :search-placeholder="searchPlaceholder"
      :item-label="itemLabel"
      :export-filename="exportFilename"
      :export-columns="exportColumns"
    >
      <template #group-header="{ group }">
        <span class="text-base font-medium leading-6 text-ink-gray-9">
          {{ formatFullDate(group.group) }} - {{ group.rows.length }} check-ins
        </span>
      </template>

      <template #cell="{ item, column }">
        <span v-if="column.key === 'check_in_time'" class="text-sm text-ink-gray-6">
          {{ formatTimeOnly(item) }}
        </span>
        <span v-else class="text-base block truncate text-wrap">{{ item }}</span>
      </template>
    </SearchListView>
  </div>
</template>

<script setup>
import { computed, ref, watchEffect } from 'vue'
import SearchListView from '@/components/ui/SearchListView.vue'
import DocsInfo from '@/components/DocsInfo.vue'
import { formatFullDate, formatTimeOnly } from '@/helpers/date'

const props = defineProps({
  checkins: { type: Array, default: () => [] },
  nameField: { type: String, default: 'name1' },
  docsMessage: { type: String, default: 'Check-ins is available during event days.' },
  docsUrl: { type: String, default: '' },
  searchPlaceholder: { type: String, default: 'Search check-ins...' },
  itemLabel: { type: String, default: 'check-ins' },
  exportFilename: { type: String, required: true },
  additionalColumns: { type: Array, default: () => [] },
})

const checkinGroups = ref([])

// Base columns
const columns = computed(() => [
  { key: props.nameField, label: 'Name', width: '250px' },
  { key: 'email', label: 'Email', width: '200px' },
  ...props.additionalColumns,
  { key: 'check_in_time', label: 'Checked-in Time', width: '1fr' },
])

const exportColumns = computed(() => [
  { key: 'date', label: 'Date' },
  { key: props.nameField, label: 'Name', width: '250px' },
  { key: 'email', label: 'Email' },
  ...props.additionalColumns,
  { key: 'check_in_time', label: 'Check-in Time' },
])

// Group check-ins by date
watchEffect(() => {
  const list = props.checkins || []
  const byDate = {}

  list.forEach((checkin) => {
    const date = new Date(checkin.check_in_time).toISOString().split('T')[0]
    if (!byDate[date]) byDate[date] = []
    byDate[date].push({ ...checkin, date })
  })

  const dates = Object.keys(byDate).sort().reverse()
  const existingStates = Object.fromEntries(checkinGroups.value.map((g) => [g.group, g.collapsed]))

  checkinGroups.value = dates.map((date) => ({
    group: date,
    collapsed: existingStates[date] ?? false,
    rows: byDate[date],
  }))
})
</script>
