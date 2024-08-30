<template>
  <Header />
  <div
    v-if="event.data && schedule.data"
    class="w-full flex flex-col items-center p-4"
  >
    <div class="max-w-screen-xl w-full">
      <Breadcrumb class="mt-2" :items="breadcrumb_items" />
      <EventHeader
        :event="event.data"
        class="my-4 border-b border-gray-900 pb-4"
      />
      <ScheduleHeader :event="event.data" class="py-2" />
      <div class="flex justify-between items-end gap-4 flex-wrap">
        <ScheduleDateToggle :dates="eventDays" class="mt-4" v-model="selectedDay" />
        <ScheduleViewToggle v-model="selectedScheduleView" class="mt-4 hidden sm:block" />
      </div>
      <ScheduleView :view="selectedScheduleView" :schedule="selectedSchedule" class="my-6" />
    </div>
  </div>
  <div v-else>
    <div
      class="max-w-screen-lg mx-auto mt-8 flex items-center justify-center min-h-[320px]"
    >
      <LoadingText class="text-lg" text="Loading schedules..." />
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import EventHeader from '@/components/schedule/EventHeader.vue'
import ScheduleHeader from '@/components/schedule/ScheduleHeader.vue'
import ScheduleDateToggle from '@/components/schedule/ScheduleDateToggle.vue'
import ScheduleViewToggle from '@/components/schedule/ScheduleViewToggle.vue'
import ScheduleView from '@/components/schedule/ScheduleView.vue'
import { ref, computed, watch, provide } from 'vue'
import { createResource, LoadingText, usePageMeta } from 'frappe-ui'
import { useRoute } from 'vue-router'

const route = useRoute()

const eventDays = ref([])
const selectedDay = ref(null)
const selectedSchedule = ref(null)
const selectedScheduleView = ref('vertical')

const event = createResource({
  url: 'fossunited.api.dashboard.get_event_from_permalink',
  makeParams() {
    return {
      permalink: route.params.permalink,
    }
  },
  auto: true,
  transform(data) {
    if (!data.schedule_page_description) {
      data.schedule_page_description = `Explore the full schedule for ${data.event_name} to plan your experience. From keynote sessions and workshops to panel discussions and networking breaks, our schedule is designed to offer a balanced mix of learning, inspiration, and collaboration.`
    }
  },
  onSuccess(data) {
    schedule.fetch()
  },
})

provide('event', event)

const schedule = createResource({
  url: 'fossunited.api.schedule.get_event_schedule',
  makeParams() {
    return {
      event_id: event.data.name,
    }
  },
  loading: true,
  onSuccess(data) {
    eventDays.value = Object.keys(data)
    selectedDay.value = eventDays.value[0]
  },
})

watch(selectedDay, (newVal) => {
  if (newVal) {
    selectedSchedule.value = schedule.data[newVal]
  }
})

const breadcrumb_items = computed(() => {
  return [
    {
      label: event.data.event_name,
      link: event.data.is_external_event
        ? event.data.external_event_url
        : getRedirectRoute(event.data.route),
    },
    {
      label: 'Schedule',
    },
  ]
})

usePageMeta(()=> {
  return {
    title: `${event.data.event_name} Schedule`,
  }
})

function getRedirectRoute(route) {
  return window.location.origin + '/' + route
}
</script>
