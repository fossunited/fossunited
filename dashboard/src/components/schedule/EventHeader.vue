<template>
  <div class="w-full flex flex-col md:flex-row gap-4 justify-between md:items-center">
    <router-link :to="`/${event.route}`" class="flex gap-2 items-center no-underline text-inherit">
      <div v-if="event.event_logo">
        <img :src="event.event_logo" :alt="event.event_name + ' Logo'" class="h-8" />
      </div>
      <div v-else>
        <CityBadge v-if="chapterType === 'City Community'" :name="event.chapter_name" />
        <FossClubBadge v-else-if="chapterType === 'FOSS Club'" :name="event.chapter_name" />
        <span v-else class="text-base font-medium">{{ event.chapter_name }}</span>
      </div>
      <div class="text-2xl">|</div>
      <h2 class="text-lg font-semibold">{{ event.event_name }}</h2>
    </router-link>
    <div class="flex gap-2 text-sm flex-wrap">
      <div><IconMapPin class="w-3 h-3" /></div>
      <div>
        <a
          v-if="event?.map_link"
          :href="event.map_link"
          class="text-sm underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ event.event_location }}
        </a>
        <div v-else class="text-sm">
          {{ event.event_location }}
        </div>
      </div>
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
import { computed } from 'vue'
import CityBadge from '@/components/CityBadge.vue'
import FossClubBadge from '@/components/FossClubBadge.vue'
import dayjs from 'dayjs'
import advancedFormat from 'dayjs/plugin/advancedFormat'
import { IconMapPin } from '@tabler/icons-vue'

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
