<template>
  <div class="px-3 py-2 flex flex-col items-center gap-1 border border-outline-gray-4 bg-surface-white h-fit">
    <div class="flex gap-1 text-sm font-semibold">
      <span>{{ getFormattedTime(session.start_time) }}</span>
    </div>
    <div
      v-if="session.category !== 'Break'"
      class="flex text-[10px] items-center gap-1 uppercase text-ink-gray-5 divide-x divide-gray-400"
    ></div>
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
