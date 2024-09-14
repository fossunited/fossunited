<template>
  <div class="w-full flex flex-col md:flex-row gap-4 justify-between md:items-center">
    <div class="flex gap-2 items-center">
      <div v-if="event.is_external_event">
        <img :src="event.event_logo" :alt="event.event_name + ' Logo'" class="h-8" />
      </div>
      <div v-else>
        <CityBadge v-if="chapterType === 'City Community'" :name="event.chapter_name" />
        <FossClubBadge v-else-if="chapterType === 'FOSS Club'" :name="event.chapter_name" />
        <span v-else class="text-base font-medium">{{ event.chapter_name }}</span>
      </div>
      <div class="text-2xl">|</div>
      <h2 class="text-lg font-semibold">{{ event.event_name }}</h2>
    </div>
    <div class="flex gap-2 text-sm flex-wrap">
      <div>{{ event.event_location }}</div>
      <div>|</div>
      <div>
        <span v-if="dayjs(event.event_start_date).date() != dayjs(event.event_end_date).date()">
          {{ dayjs(event.event_start_date).format('Do') }} -
        </span>
        <span>{{ dayjs(event.event_end_date).format('Do MMM YYYY') }}</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { defineProps, computed } from 'vue'
import CityBadge from '@/components/CityBadge.vue'
import FossClubBadge from '@/components/FossClubBadge.vue'
import dayjs from 'dayjs'
import advancedFormat from 'dayjs/plugin/advancedFormat'

dayjs.extend(advancedFormat)

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const chapterType = computed(() => {
  let type = props.event.chapter.split('-').pop()
  return type
})
</script>
