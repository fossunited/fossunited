<template>
  <div class="flex flex-col h-full">
    <!-- Controls -->
    <div class="flex-shrink-0">
      <div class="flex flex-col md:flex-row gap-2 my-2 md:items-end flex-wrap">
        <FormControl
          v-if="searchable"
          v-model="searchRaw"
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

        <!-- Group by pill selector — only when multiple options provided -->
        <div v-if="groupByOptions && groupByOptions.length > 1" class="flex items-center gap-2">
          <span class="text-sm text-ink-gray-5">Group by:</span>
          <div class="flex border border-outline-gray-2 rounded-lg overflow-hidden">
            <button
              v-for="(opt, i) in groupByOptions"
              :key="opt.value"
              class="px-3 py-1 text-sm transition-colors"
              :class="
                activeGroupByIndex === i
                  ? 'bg-surface-gray-3 text-ink-gray-9 font-medium'
                  : 'text-ink-gray-5 hover:text-ink-gray-8'
              "
              @click="activeGroupByIndex = i"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <slot name="actions" :filtered-rows="visibleRows" :search="searchRaw">
          <Button
            v-if="exportable"
            icon-left="download"
            :label="exportLabel"
            class="h-10 px-3"
            @click="handleExport"
          />
        </slot>
      </div>

      <div
        v-if="(debouncedSearch || activeFilterApplied) && showCount"
        class="text-sm text-ink-gray-5 mb-2"
      >
        {{ filteredCount }} of {{ totalCount }} {{ itemLabel }}
      </div>
    </div>

    <!-- scroll control; ListView expands to full content height inside -->
    <div class="overflow-y-auto overflow-x-auto max-h-[calc(100vh-220px)]">
      <ListView
        v-bind="$attrs"
        :rows="listRows"
        :columns="reactiveColumns"
        :row-key="rowKey"
        :options="mergedOptions"
      >
        <template v-for="(_, name) in $slots" #[name]="slotData">
          <slot :name="name" v-bind="slotData" />
        </template>
      </ListView>
    </div>

    <!-- Row detail drawer -->
    <Dialog v-if="rowDrawer" v-model="showDrawer" :options="{ size: 'lg' }">
      <template #body-title>
        <span class="font-semibold text-ink-gray-9">{{ drawerTitle || 'Details' }}</span>
      </template>
      <template #body-content>
        <div v-if="selectedRow" class="flex flex-col divide-y divide-outline-gray-1 mt-1">
          <div
            v-for="col in columns.filter(c => c.drawer !== false)"
            :key="col.key"
            class="flex flex-col gap-1 py-3 first:pt-0"
          >
            <span class="text-xs font-medium text-ink-gray-4 uppercase tracking-wide">{{ col.label }}</span>
            <slot name="drawer-cell" :column="col" :item="selectedRow[col.key]" :row="selectedRow">
              <span class="text-sm text-ink-gray-7 break-words whitespace-pre-wrap">
                {{ selectedRow[col.key] ?? '—' }}
              </span>
            </slot>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ListView, FormControl, Button, Dialog } from 'frappe-ui'
import { ref, computed, reactive, watch, onUnmounted } from 'vue'
import { debounce } from 'lodash-es'
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

  filterField: { type: String, default: null },
  filterOptions: { type: Array, default: null },

  // Simple grouping (single field, no selector UI)
  groupBy: { type: String, default: null },
  groupOrder: { type: Array, default: null },
  defaultCollapsed: { type: [Boolean, Array], default: false },

  // Each option: { label, value, order?, defaultCollapsed? }
  groupByOptions: { type: Array, default: null },

  rowDrawer: { type: Boolean, default: false },
  drawerTitleKey: { type: String, default: null },
})

defineOptions({ inheritAttrs: false })

// Reactive so dynamic columns (from computed) stay in sync;
// reactive() enables ListView's column resize mutation tracking.
const reactiveColumns = computed(() => reactive(props.columns))

// Search
const searchRaw = ref('')
const debouncedSearch = ref('')

const applySearch = debounce((v) => {
  debouncedSearch.value = v
}, 400)

watch(searchRaw, applySearch)
onUnmounted(() => applySearch.cancel())

// Filter dropdown

const selectedFilter = ref(props.filterOptions?.[0] || 'All')

const activeFilterApplied = computed(
  () =>
    selectedFilter.value &&
    selectedFilter.value !== 'All' &&
    selectedFilter.value !== props.filterOptions?.[0],
)

// Active groupBy option

const activeGroupByIndex = ref(0)

// Resolved groupBy field, order, defaultCollapsed —
// groupByOptions takes precedence over simple groupBy props.
const activeOption = computed(() => props.groupByOptions?.[activeGroupByIndex.value] ?? null)

const effectiveGroupBy = computed(() => activeOption.value?.value ?? props.groupBy ?? null)
const effectiveGroupOrder = computed(() => activeOption.value?.order ?? props.groupOrder ?? null)
const effectiveDefaultCollapsed = computed(
  () => activeOption.value?.defaultCollapsed ?? props.defaultCollapsed ?? false,
)

// Collapse state
// Keyed by group string — survives group object recreation across re-renders.
// ListView mutates group.collapsed; we bridge via getter/setter so Vue tracks it.
const collapseState = reactive({})

// Group detection
// Pre-grouped: caller passes [{ group, rows[] }] directly
const isPreGrouped = computed(() => props.rows.length > 0 && Array.isArray(props.rows[0]?.rows))

const isGrouped = computed(() => isPreGrouped.value || !!effectiveGroupBy.value)

// Canonical groups
const allGroups = computed(() => {
  if (!isGrouped.value) return null

  if (isPreGrouped.value) {
    return props.rows.map((g) => ({ key: g.group, rows: g.rows }))
  }

  const groupMap = new Map()
  for (const row of props.rows) {
    const key = String(row[effectiveGroupBy.value] ?? 'Other')
    if (!groupMap.has(key)) groupMap.set(key, [])
    groupMap.get(key).push(row)
  }

  const order = effectiveGroupOrder.value
    ? [
        ...effectiveGroupOrder.value.filter((k) => groupMap.has(k)),
        ...[...groupMap.keys()].filter((k) => !effectiveGroupOrder.value.includes(k)),
      ]
    : [...groupMap.keys()]

  return order.map((key) => ({ key, rows: groupMap.get(key) }))
})

// Initialize collapse state for newly seen group keys
watch(
  allGroups,
  (groups) => {
    if (!groups) return
    const d = effectiveDefaultCollapsed.value
    for (const { key } of groups) {
      if (!(key in collapseState)) {
        if (d === true) collapseState[key] = true
        else if (Array.isArray(d)) collapseState[key] = d.includes(key)
        else collapseState[key] = false
      }
    }
  },
  { immediate: true },
)

// Expand all while searching; restore defaults when search cleared
watch(debouncedSearch, (term, prev) => {
  if (!allGroups.value) return
  if (term) {
    for (const { key } of allGroups.value) collapseState[key] = false
  } else if (prev && !term) {
    const d = effectiveDefaultCollapsed.value
    for (const { key } of allGroups.value) {
      if (d === true) collapseState[key] = true
      else if (Array.isArray(d)) collapseState[key] = d.includes(key)
      else collapseState[key] = false
    }
  }
})

// Row matching
const getSearchText = (row) => {
  if (props.searchFields) {
    return props.searchFields
      .map((f) => row[f])
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
  }
  return props.columns
    .map((col) => {
      const v = row[col.key]
      return typeof v === 'boolean' ? (v ? 'yes' : 'no') : v
    })
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
}

const matchesRow = (row) => {
  const term = debouncedSearch.value.toLowerCase().trim()
  if (term && !getSearchText(row).includes(term)) return false
  if (activeFilterApplied.value && row[props.filterField] !== selectedFilter.value) return false
  return true
}

// Filtered data — never mutates props
const filteredGroups = computed(() => {
  if (!allGroups.value) return null
  return allGroups.value
    .map(({ key, rows }) => ({ key, rows: rows.filter(matchesRow) }))
    .filter((g) => g.rows.length > 0)
})

const filteredFlatRows = computed(() => {
  if (isGrouped.value) return null
  return props.rows.filter(matchesRow)
})

// Counts
const totalCount = computed(() => {
  if (allGroups.value) return allGroups.value.reduce((s, g) => s + g.rows.length, 0)
  return props.rows.length
})

const filteredCount = computed(() => {
  if (filteredGroups.value) return filteredGroups.value.reduce((s, g) => s + g.rows.length, 0)
  return filteredFlatRows.value?.length ?? props.rows.length
})

// Flat filtered rows — for export and actions slot
const visibleRows = computed(() => {
  if (filteredGroups.value) return filteredGroups.value.flatMap((g) => g.rows)
  return filteredFlatRows.value ?? props.rows
})

// getter/setter on collapsed bridges ListView's direct mutation to collapseState
const listRows = computed(() => {
  if (filteredGroups.value) {
    return filteredGroups.value.map(({ key, rows }) => ({
      group: key,
      rows,
      get collapsed() {
        return collapseState[key] ?? false
      },
      set collapsed(v) {
        collapseState[key] = v
      },
    }))
  }
  return filteredFlatRows.value ?? props.rows
})

// Row drawer
const selectedRow = ref(null)
const showDrawer = computed({
  get: () => !!selectedRow.value,
  set: (v) => { if (!v) selectedRow.value = null },
})
const drawerTitle = computed(() => {
  if (!selectedRow.value) return ''
  if (props.drawerTitleKey) return String(selectedRow.value[props.drawerTitleKey] ?? '')
  return ''
})

// ListView options

const mergedOptions = computed(() => ({
  selectable: false,
  showTooltip: true,
  resizeColumn: true,
  ...props.options,
  ...(props.rowDrawer ? { onRowClick: (row) => { selectedRow.value = row } } : {}),
  emptyState:
    debouncedSearch.value || activeFilterApplied.value
      ? { title: 'No matching results', description: 'Try adjusting your filters.' }
      : props.options.emptyState,
}))

// Export
const escapeCSV = (str) => {
  const s = String(str ?? '')
  return s.includes(',') || s.includes('"') || s.includes('\n') ? `"${s.replace(/"/g, '""')}"` : s
}

const handleExport = () => {
  const rows = visibleRows.value
  if (!rows.length) {
    toast.error('No data to export')
    return
  }
  const cols = props.exportColumns || props.columns
  const headers = cols.map((c) => c.label || c.key)
  const data = rows.map((row) =>
    cols.map((col) => {
      if (typeof col.exportValue === 'function') return col.exportValue(row)
      const v = row[col.key]
      if (typeof v === 'boolean') return v ? 'Yes' : 'No'
      if (typeof v === 'object' && v !== null) return ''
      return v ?? ''
    }),
  )
  const csv = [headers, ...data].map((r) => r.map(escapeCSV).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${props.exportFilename}${debouncedSearch.value ? '_filtered' : ''}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
  toast.success('CSV downloaded successfully')
}

defineExpose({ searchRaw, selectedFilter, visibleRows, filteredCount, totalCount, handleExport })
</script>
