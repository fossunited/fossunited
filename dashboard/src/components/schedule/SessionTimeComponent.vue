<template>
  <div class="px-6 py-4 flex flex-col items-center gap-2 border border-gray-500 bg-white h-fit">
    <div class="flex gap-1 text-base font-medium">
      <span>{{ getFormattedTime(session.start_time) }}</span>
      <span v-if="session.category == 'Break'">-</span>
      <span v-if="session.category == 'Break'">{{ getFormattedTime(session.end_time) }}</span>
    </div>
    <div
      class="flex text-xs items-center gap-2 uppercase text-gray-600 divide-x-2 divide-gray-400"
      v-if="session.category !== 'Break'"
    >
      <span>Day {{ session.day }}</span>
      <span class="pl-2">{{ session.hall }}</span>
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
