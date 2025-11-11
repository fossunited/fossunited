<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'
import { Badge } from 'frappe-ui'
import {
  IconClock,
  IconInfoCircleFilled,
  IconBuilding,
  IconAlertTriangleFilled,
} from '@tabler/icons-vue'

const schedule_item = defineModel({ required: true, type: Object })

const formatTime = (time) => {
  if (!time) return '--:--'
  return dayjs(`1970-01-01T${time}`).format('hh:mm A')
}

const getTypeColor = (type) => {
  const colors = {
    Talk: 'blue',
    'Lightning Talk': 'purple',
    Workshop: 'green',
    'Panel Discussion': 'orange',
    'Opening Note': 'yellow',
    Break: 'gray',
    Other: 'gray',
  }
  return colors[type] || 'gray'
}

const duration = computed(() => {
  if (!schedule_item.value.start_time || !schedule_item.value.end_time) {
    return null
  }

  const [startHour, startMin] = schedule_item.value.start_time.split(':').map(Number)
  const [endHour, endMin] = schedule_item.value.end_time.split(':').map(Number)

  const totalMinutes = endHour * 60 + endMin - (startHour * 60 + startMin)

  if (totalMinutes < 60) {
    return `${totalMinutes}m`
  }

  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`
})

const isIncomplete = computed(() => {
  return (
    !schedule_item.value.title ||
    !schedule_item.value.category ||
    !schedule_item.value.start_time ||
    !schedule_item.value.end_time ||
    !schedule_item.value.hall
  )
})
</script>

<template>
  <div
    class="p-4 rounded-lg border bg-white hover:border-gray-400 hover:shadow-sm transition-all cursor-pointer relative overflow-hidden"
    :class="{
      stripes: schedule_item.is_new,
      'border-amber-300 bg-amber-50/30': isIncomplete && !schedule_item.is_new,
    }"
  >
    <!-- Status Indicator -->
    <div
      class="absolute left-0 top-0 bottom-0 w-1 rounded-l-lg"
      :class="{
        'bg-gray-400': schedule_item.is_new,
        'bg-amber-500': isIncomplete && !schedule_item.is_new,
        'bg-green-500': !isIncomplete && !schedule_item.is_new,
      }"
    />

    <div class="pl-3 flex flex-col gap-2">
      <!-- Title and Category -->
      <div class="flex items-start justify-between gap-2">
        <h5 class="text-base font-semibold flex-1 leading-snug">
          {{ schedule_item.title || 'Untitled Schedule Item' }}
        </h5>
        <Badge
          v-if="schedule_item.category"
          :label="schedule_item.category"
          :theme="getTypeColor(schedule_item.category)"
          variant="subtle"
        />
      </div>

      <!-- Time, Duration, and Hall -->
      <div class="flex flex-wrap items-center gap-2 text-sm text-gray-600">
        <div class="flex items-center gap-1.5">
          <IconClock class="h-4 w-4" />
          <span>{{ formatTime(schedule_item.start_time) }}</span>
          <span>-</span>
          <span>{{ formatTime(schedule_item.end_time) }}</span>
        </div>

        <span v-if="duration" class="text-xs bg-gray-100 px-2 py-0.5 rounded-full">
          {{ duration }}
        </span>

        <div v-if="schedule_item.hall" class="flex items-center gap-1.5">
          <IconBuilding class="h-4 w-4" />
          <span class="font-medium">{{ schedule_item.hall }}</span>
        </div>
      </div>

      <!-- Warnings for incomplete items -->
      <div
        v-if="isIncomplete"
        class="flex items-center gap-1.5 text-xs text-amber-700 bg-amber-50 px-2 py-1 rounded"
      >
        <IconAlertTriangleFilled class="h-6 w-6" />
        <span>Incomplete information</span>
      </div>

      <!-- New item indicator -->
      <div
        v-if="schedule_item.is_new"
        class="flex items-center gap-1.5 text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded"
      >
        <IconInfoCircleFilled class="h-4 w-4" />
        <span>New item - click to complete</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stripes {
  background-color: #ffffff;
  background-image: url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%234b4b4b' fill-opacity='0.09' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E");
}
</style>
