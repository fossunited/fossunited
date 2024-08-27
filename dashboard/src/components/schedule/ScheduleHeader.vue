<template>
  <div class="flex items-start gap-4">
    <ScheduleHeroIcon class="min-w-40 hidden md:block" />
    <div class="flex flex-col gap-2">
      <div class="prose">
        <h1 class="font-bond">Schedule</h1>
      </div>
      <div class="text-base text-gray-700">
        {{ event.schedule_page_description }}
      </div>
    </div>
  </div>
</template>
<script setup>
import ScheduleHeroIcon from '@/components/icons/ScheduleHeroIcon.vue'
import { defineProps } from 'vue'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})
</script>
