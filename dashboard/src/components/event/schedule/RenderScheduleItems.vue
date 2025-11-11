<script setup>
import { computed, ref } from 'vue'
import { FormControl, Switch } from 'frappe-ui'
import ScheduleItem from './ScheduleItem.vue'
import dayjs from 'dayjs'

const emit = defineEmits(['modify-item'])
const schedule_items = defineModel('schedule', { type: Array, default: [] })

// Filter and sort options
const groupBy = ref('hall') // 'hall', 'time', 'none'
const sortBy = ref('time') // 'time', 'title'
const showOnlyNewItems = ref(false)

const SORT_OPTIONS = [
  { label: 'Start Time', value: 'time' },
  { label: 'Title', value: 'title' },
]

const GROUP_OPTIONS = [
  { label: 'Hall', value: 'hall' },
  { label: 'Time', value: 'time' },
  { label: 'None', value: 'none' },
]

// Filter items based on showOnlyNewItems toggle
const filteredItems = computed(() => {
  if (showOnlyNewItems.value) {
    // When ON, show ONLY new items
    return schedule_items.value.filter((item) => item.is_new)
  }
  // When OFF, show all items
  return schedule_items.value
})

// Sort items
const sortedItems = computed(() => {
  const items = [...filteredItems.value]

  if (sortBy.value === 'time') {
    return items.sort((a, b) => {
      if (!a.start_time && !b.start_time) return 0
      if (!a.start_time) return 1
      if (!b.start_time) return -1
      return a.start_time.localeCompare(b.start_time)
    })
  }

  if (sortBy.value === 'title') {
    return items.sort((a, b) => {
      const titleA = a.title?.toLowerCase() || ''
      const titleB = b.title?.toLowerCase() || ''
      return titleA.localeCompare(titleB)
    })
  }

  return items
})

// Group items
const groupedItems = computed(() => {
  if (groupBy.value === 'none') {
    return [{ key: 'all', label: null, items: sortedItems.value }]
  }

  const groups = {}

  sortedItems.value.forEach((item) => {
    let key, label

    if (groupBy.value === 'hall') {
      key = item.hall || 'No Hall'
      label = item.hall || 'No Hall Assigned'
    } else if (groupBy.value === 'time') {
      if (!item.start_time) {
        key = 'no-time'
        label = 'No Time Set'
      } else {
        const hour = parseInt(item.start_time.split(':')[0])
        if (hour < 12) {
          key = 'morning'
          label = 'Morning (Before 12 PM)'
        } else if (hour < 17) {
          key = 'afternoon'
          label = 'Afternoon (12 PM - 5 PM)'
        } else {
          key = 'evening'
          label = 'Evening (After 5 PM)'
        }
      }
    }

    if (!groups[key]) {
      groups[key] = { key, label, items: [] }
    }

    groups[key].items.push(item)
  })

  // Sort groups for time-based grouping
  if (groupBy.value === 'time') {
    const order = ['morning', 'afternoon', 'evening', 'no-time']
    return order.map((key) => groups[key]).filter(Boolean)
  }

  return Object.values(groups)
})

const newItemsCount = computed(() => schedule_items.value.filter((item) => item.is_new).length)
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Filters and Controls -->
    <div class="bg-gray-50 p-4 rounded-lg border">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <FormControl
          v-model="groupBy"
          label="Group By"
          type="select"
          :options="GROUP_OPTIONS"
          variant="outline"
        />

        <FormControl
          v-model="sortBy"
          label="Sort By"
          type="select"
          :options="SORT_OPTIONS"
          variant="outline"
        />

        <Switch
          v-model="showOnlyNewItems"
          label="Show Only New Items"
          :description="`${newItemsCount} new item(s)`"
        />
      </div>

      <!-- Summary -->
      <div class="mt-3 pt-3 border-t text-sm text-gray-600">
        Showing {{ filteredItems.length }} of {{ schedule_items.length }} items
      </div>
    </div>

    <!-- Grouped Schedule Items -->
    <div v-if="filteredItems.length === 0" class="text-center py-8 text-gray-500">
      <p v-if="showOnlyNewItems">No new schedule items</p>
      <p v-else>No schedule items to display</p>
      <p v-if="showOnlyNewItems && newItemsCount === 0" class="text-sm mt-2">
        All items are complete
      </p>
    </div>

    <div v-else class="flex flex-col gap-6">
      <div v-for="group in groupedItems" :key="group.key" class="flex flex-col gap-3">
        <!-- Group Header -->
        <div v-if="group.label" class="flex items-center gap-2 pb-2 border-b">
          <h4 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">
            {{ group.label }}
          </h4>
          <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
            {{ group.items.length }}
          </span>
        </div>

        <!-- Items in Group -->
        <div class="flex flex-col gap-2">
          <ScheduleItem
            v-for="item in group.items"
            :key="item.idx"
            v-model="schedule_items[schedule_items.findIndex((i) => i.idx === item.idx)]"
            @click="emit('modify-item', item)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
