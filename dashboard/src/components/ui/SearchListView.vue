<template>
  <div>
    <div class="flex flex-col md:flex-row gap-2 my-2 md:items-end">
      <FormControl
        v-if="searchable"
        v-model="search"
        type="search"
        :placeholder="searchPlaceholder"
        class="max-w-xs"
        :class="searchClass"
      />

      <FormControl
        v-if="filterField && filterOptions"
        v-model="selectedFilter"
        type="select"
        :options="filterOptions"
        class="max-w-xs"
      />

      <slot name="actions" :filtered-rows="filteredRows" :search="search">
        <Button
          v-if="exportable"
          icon-left="download"
          :label="exportLabel"
          class="h-10 px-3"
          @click="handleExport"
        />
      </slot>
    </div>

    <div v-if="(search || activeFilterApplied) && showCount" class="text-sm text-ink-gray-5 mb-2">
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
import { debounce } from 'lodash-es'

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

  filterField: { type: String, default: null }, // eg: "status"
  filterOptions: { type: Array, default: null }, // eg: ["yes", "no"]
})

defineOptions({ inheritAttrs: false })

const searchRaw = ref('')
const search = computed({
  get: () => searchRaw.value,
  set: debounce((v) => {
    searchRaw.value = v
  }, 400),
})

const selectedFilter = ref(props.filterOptions?.[0] || 'All')

const activeFilterApplied = computed(() => {
  return (
    selectedFilter.value &&
    selectedFilter.value !== 'All' &&
    selectedFilter.value !== props.filterOptions?.[0]
  )
})

const isGrouped = computed(
  () => props.rows.length > 0 && props.rows.every((row) => row && Array.isArray(row.rows)),
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

const searchTextCache = new WeakMap()

const getSearchText = (row) => {
  if (!searchTextCache.has(row)) {
    searchTextCache.set(row, getSearchableText(row))
  }
  return searchTextCache.get(row)
}

const filteredRows = computed(() => {
  const term = search.value ? search.value.toLowerCase().trim() : ''
  const hasSearch = !!term
  const hasFilter = props.filterField && selectedFilter.value && selectedFilter.value !== 'All'

  // No filters applied, return original rows
  if (!hasSearch && !hasFilter) {
    return props.rows
  }

  if (isGrouped.value) {
    return props.rows
      .map((group) => {
        const filtered = group.rows.filter((row) => {
          // Apply search filter
          if (hasSearch && !getSearchText(row).includes(term)) {
            return false
          }
          // Apply status filter
          if (hasFilter && row[props.filterField] !== selectedFilter.value) {
            return false
          }
          return true
        })

        return {
          ...group,
          rows: filtered,
        }
      })
      .filter((group) => group.rows.length > 0)
  }

  return props.rows.filter((row) => {
    // Apply search filter
    if (hasSearch && !getSearchText(row).includes(term)) {
      return false
    }
    // Apply status filter
    if (hasFilter && row[props.filterField] !== selectedFilter.value) {
      return false
    }
    return true
  })
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
  emptyState:
    search.value || activeFilterApplied.value
      ? {
          title: 'No matching results',
          description: 'Try adjusting your filters.',
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

  const columnsToExport = props.exportColumns || props.columns
  const headers = columnsToExport.map((col) => col.label || col.key)

  const rows = flatRows.map((row) =>
    columnsToExport.map((col) => {
      if (typeof col.exportValue === 'function') {
        return col.exportValue(row)
      }

      const value = row[col.key]
      if (typeof value === 'boolean') return value ? 'Yes' : 'No'
      if (typeof value === 'object' && value !== null) return ''
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

defineExpose({ search, selectedFilter, filteredRows, filteredCount, totalCount, handleExport })
</script>
