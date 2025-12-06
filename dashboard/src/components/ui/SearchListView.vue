<template>
  <div>
    <div class="flex flex-col flex-wrap md:flex-row gap-5 my-2 md:items-end">
      <FormControl
        v-if="searchable"
        v-model="search"
        type="search"
        :placeholder="searchPlaceholder"
        class="md:w-1/4"
        :class="searchClass"
      />

      <slot name="actions" :filtered-rows="filteredRows" :search="search">
        <Button
          v-if="exportable"
          icon-left="download"
          :label="exportLabel"
          @click="handleExport"
        />
      </slot>
    </div>

    <div v-if="search && showCount" class="text-sm text-ink-gray-5 mb-2">
      {{ filteredCount }} of {{ totalCount }} {{ itemLabel }}
    </div>

    <ListView
      v-bind="$attrs"
      :rows="filteredRows"
      :columns="columns"
      :row-key="rowKey"
      :options="mergedOptions"
    >
      <template v-for="(_, name) in $slots" #[name]="slotData">
        <slot :name="name" v-bind="slotData" />
      </template>
    </ListView>
  </div>
</template>

<script setup>
import { ListView, FormControl, Button } from 'frappe-ui'
import { ref, computed } from 'vue'
import { toast } from 'vue-sonner'

const props = defineProps({
  rows: { type: Array, required: true },
  columns: { type: Array, required: true },
  rowKey: { type: String, required: true },
  options: { type: Object, default: () => ({}) },

  searchable: { type: Boolean, default: true },
  searchPlaceholder: { type: String, default: 'Search...' },
  searchClass: { type: String, default: 'flex-1' },
  searchFields: { type: Array, default: null },
  showCount: { type: Boolean, default: true },
  itemLabel: { type: String, default: 'items' },

  exportable: { type: Boolean, default: true },
  exportLabel: { type: String, default: 'Download CSV' },
  exportFilename: { type: String, default: 'export' },
  exportColumns: { type: Array, default: null },
})

defineOptions({ inheritAttrs: false })

const search = ref('')

const isGrouped = computed(
  () =>
    props.rows.length > 0 &&
    props.rows.every((row) => row.group && row.rows && Array.isArray(row.rows)),
)

const getSearchableText = (row) => {
  if (props.searchFields) {
    return props.searchFields
      .map((field) => row[field])
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
  }

  return props.columns
    .map((col) => {
      const value = row[col.key]
      if (typeof value === 'boolean') return value ? 'yes' : 'no'
      return value
    })
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
}

const filteredRows = computed(() => {
  if (!search.value) return props.rows

  const term = search.value.toLowerCase().trim()

  if (isGrouped.value) {
    return props.rows
      .map((group) => ({
        ...group,
        rows: group.rows.filter((row) => getSearchableText(row).includes(term)),
      }))
      .filter((group) => group.rows.length > 0)
  }

  return props.rows.filter((row) => getSearchableText(row).includes(term))
})

const totalCount = computed(() => {
  if (isGrouped.value) {
    return props.rows.reduce((acc, group) => acc + group.rows.length, 0)
  }
  return props.rows.length
})

const filteredCount = computed(() => {
  if (isGrouped.value) {
    return filteredRows.value.reduce((acc, group) => acc + group.rows.length, 0)
  }
  return filteredRows.value.length
})

const mergedOptions = computed(() => ({
  ...props.options,
  emptyState: search.value
    ? {
        title: 'No matching results',
        description: 'Try adjusting your search term.',
        ...props.options.emptyState,
      }
    : props.options.emptyState,
}))

const escapeCSV = (str) => {
  const s = String(str ?? '')
  return s.includes(',') || s.includes('"') || s.includes('\n') ? `"${s.replace(/"/g, '""')}"` : s
}

const getFlatRows = () => {
  if (isGrouped.value) {
    return filteredRows.value.flatMap((group) => group.rows)
  }
  return filteredRows.value
}

const handleExport = () => {
  const flatRows = getFlatRows()

  if (!flatRows.length) {
    toast.error('No data to export')
    return
  }

  // Use exportColumns if provided, otherwise use all columns
  const columnsToExport = props.exportColumns || props.columns

  const headers = columnsToExport.map((col) => col.label || col.key)

  const rows = flatRows.map((row) =>
    columnsToExport.map((col) => {
      const value = row[col.key]
      if (typeof value === 'boolean') return value ? 'Yes' : 'No'
      return value ?? ''
    }),
  )

  const csv = [headers, ...rows].map((row) => row.map(escapeCSV).join(',')).join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)

  const searchSuffix = search.value ? '_filtered' : ''
  link.download = `${props.exportFilename}${searchSuffix}.csv`

  link.click()
  URL.revokeObjectURL(link.href)

  toast.success('CSV downloaded successfully')
}

defineExpose({ search, filteredRows, filteredCount, totalCount, handleExport })
</script>
