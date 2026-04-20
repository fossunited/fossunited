<script setup>
import { IconArrowUpRight, IconMapPin, IconCalendarWeek, IconClock } from '@tabler/icons-vue'
import { computed } from 'vue'
import EventLogo from '@/components/event/EventLogo.vue'
import { getFormattedEventDate, getFormattedTime } from '@/helpers/date'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const icsUrl = computed(() => {
  const eventIds = encodeURIComponent(JSON.stringify([props.event.name]))
  return `/api/method/fossunited.api.chapter.generate_ics?event_ids=${eventIds}&download=1`
})

const eventDetailItems = computed(() => [
  {
    icon: IconMapPin,
    label: props.event.event_location || 'TBD',
    href: props.event.map_link || null,
    target: '_blank',
  },
  {
    icon: IconCalendarWeek,
    label: getFormattedEventDate(props.event.event_start_date, props.event.event_end_date),
    href: icsUrl.value,
    tooltip: 'Download ICS for event',
  },
  {
    icon: IconClock,
    label: `${getFormattedTime(props.event.event_start_date) + ' - ' + getFormattedTime(props.event.event_end_date)}`,
    href: icsUrl.value,
    tooltip: 'Download ICS for event',
  },
])
</script>
<template>
  <div class="flex flex-col gap-2">
    <div class="flex flex-col md:flex-row gap-3 md:gap-6 items-center md:items-start">
      <!-- Big logo: desktop only -->
      <div class="hidden md:block shrink-0">
        <slot name="logo">
          <EventLogo
            v-if="event.banner_image || event.event_logo"
            :logo-path="event.banner_image || event.event_logo"
          />
        </slot>
      </div>
      <div class="flex flex-col gap-3 flex-grow w-full">
        <!-- Title card — entire row links to event page -->
        <a
          :href="'/' + event.route"
          class="flex flex-row p-3 rounded border gap-3 bg-surface-gray-2 w-full h-fit items-center no-underline text-inherit hover:bg-surface-gray-3 transition-colors"
        >
          <!-- Small logo: mobile only, inline with event name -->
          <img
            v-if="event.banner_image || event.event_logo"
            :src="event.banner_image || event.event_logo"
            alt="Event logo"
            class="md:hidden h-7 w-7 object-contain rounded shrink-0"
          />
          <h2 class="font-semibold flex-grow">{{ event.event_name }}</h2>
          <IconArrowUpRight class="w-4 h-4 text-ink-gray-4 shrink-0" />
        </a>
        <!-- Date, Time, Location -->
        <div class="flex flex-col gap-3 md:gap-2">
          <div
            v-for="(item, index) in eventDetailItems"
            :key="index"
            class="flex items-center gap-2 text-base text-ink-gray-5"
          >
            <component :is="item.icon" class="w-5 h-5" />
            <a
              v-if="item.href"
              :href="item.href"
              :target="item.target || '_self'"
              :rel="item.target === '_blank' ? 'noopener noreferrer' : undefined"
              :title="item.tooltip"
              class="no-underline hover:underline text-ink-gray-5 hover:text-ink-gray-7"
            >{{ item.label }}</a>
            <span v-else>{{ item.label }}</span>
          </div>
        </div>
      </div>
    </div>
    <slot name="description"></slot>
  </div>
</template>
