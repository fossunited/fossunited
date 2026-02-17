<template>
  <div class="flex flex-col md:flex-row gap-3 md:gap-6 items-center md:items-start">
    <EventLogo v-if="cfpData.data.event.event_logo" :logo-path="cfpData.data.event.event_logo" />
    <div class="flex flex-col gap-3 flex-grow w-full">
      <div
        class="flex p-3 rounded border gap-4 bg-surface-gray-2 w-full h-fit justify-between items-center"
      >
        <h2 class="font-semibold">{{ cfpData.data.event_name }}</h2>
        <a
          :href="'/' + cfpData.data.event.route"
          class="text-sm md:text-base text-ink-gray-4 flex items-center gap-1 underline"
        >
          Go to event page
          <IconArrowUpRight class="w-4 h-4" />
        </a>
      </div>
      <!-- Date, Time, Location -->
      <div class="flex flex-col gap-3 md:gap-2">
        <div
          v-for="(item, index) in eventDetailItems"
          :key="index"
          class="flex items-center gap-2 text-base text-ink-gray-5"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { IconArrowUpRight, IconMapPin, IconCalendarWeek, IconClock } from '@tabler/icons-vue'
import { computed, inject } from 'vue'
import EventLogo from '@/components/event/EventLogo.vue'
import { getFormattedEventDate, getFormattedTime } from '@/helpers/date'

const cfpData = inject('$cfpData')

const eventDetailItems = computed(() => {
  let items = [
    {
      icon: IconMapPin,
      label: cfpData.data.event.event_location || 'TBD',
    },
    {
      icon: IconCalendarWeek,
      label: getFormattedEventDate(
        cfpData.data.event.event_start_date,
        cfpData.data.event.event_end_date,
      ),
    },
    {
      icon: IconClock,
      label: `${getFormattedTime(cfpData.data.event.event_start_date) + ' - ' + getFormattedTime(cfpData.data.event.event_end_date)}`,
    },
  ]

  return items
})
</script>
