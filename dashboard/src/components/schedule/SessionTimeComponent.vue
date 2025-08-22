<template>
  <div class="px-3 py-2 flex flex-col items-center gap-1 border border-gray-500 bg-white h-fit">
    <div class="flex gap-1 text-sm font-semibold">
      <span>{{ getFormattedTime(session.start_time) }}</span>
      <span v-if="session.category == 'Break'">-</span>
      <span v-if="session.category == 'Break'">{{ getFormattedTime(session.end_time) }}</span>
    </div>
    <div
      v-if="session.category !== 'Break'"
      class="flex text-[10px] items-center gap-1 uppercase text-gray-600 divide-x divide-gray-400"
    >
      <span>Day {{ session.day }}</span>
      <span class="pl-1">{{ session.hall }}</span>
    </div>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  session: {
    type: Object,
    required: true,
  },
})

function getFormattedTime(time) {
  return dayjs(`1970-01-01 ${time}`).format('hh:mm A')
}
</script>
