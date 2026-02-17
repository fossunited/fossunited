<template>
  <div class="flex items-start gap-4">
    <ScheduleHeroIcon class="min-w-40 hidden md:block" />
    <div class="flex flex-col gap-2">
      <div class="prose">
        <h1 class="font-bond">Schedule</h1>
      </div>
      <div class="text-base text-ink-gray-6" v-html="sanitizedScheduleDesc"></div>
    </div>
  </div>
</template>
<script setup>
import ScheduleHeroIcon from '@/components/icons/ScheduleHeroIcon.vue'
import { defineProps, computed } from 'vue'
import DOMPurify from 'dompurify'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const sanitizedScheduleDesc = computed(() =>
  DOMPurify.sanitize(props.event?.schedule_page_description ?? ''),
)
</script>
