<script setup>
import { IconHomeFilled } from '@tabler/icons-vue'
import dayjs from 'dayjs'
import { Badge } from 'frappe-ui'
const schedule_item = defineModel({ required: true, type: Object })

const formatTime = (time) => {
  return dayjs(`1970-01-01T${time}`).format('hh:mm a')
}
</script>
<template>
  <div
    class="p-3 rounded border bg-white flex gap-2 hover:border-gray-400 transition-colors cursor-pointer"
    :class="schedule_item.is_new ? 'stripes' : ''"
  >
    <div class="w-[3px] bg-gray-900 rounded"></div>
    <div class="flex flex-col gap-1">
      <h5 class="text-base font-semibold">{{ schedule_item.title }}</h5>
      <div class="flex gap-2">
        <div class="flex items-center gap-1 text-sm">
          <span>{{ formatTime(schedule_item.start_time) }}</span>
          <span>- {{ formatTime(schedule_item.end_time) }}</span>
        </div>
        <Badge :label="schedule_item.hall" class="w-fit" variant="subtle" />
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
