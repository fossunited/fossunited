<template>
  <div v-if="chapters.data" class="p-4">
    <div class="prose">
      <div class="prose pb-0">
        <h2 class="mb-1">My Chapters</h2>
        <p class="text-sm mb-4">Manage the chapters you are a part of.</p>
      </div>
    </div>
    <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <ChapterCard v-for="chapter in chapters.data" :key="chapter.name" :chapter="chapter" />
    </div>
    <div class="mt-4">
      <div class="prose pt-4 mb-4">
        <h3 class="mb-0">Scheduled Events</h3>
        <p class="text-sm">Manage upcoming events.</p>
      </div>
      <div
        v-if="scheduled_events.data && scheduled_events.data.length > 0"
        class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <EventCard v-for="event in scheduled_events.data" :key="event.name" :event="event" />
      </div>
      <div v-else class="text-base mt-6 text-gray-800">
        <div>There are no scheduled events.</div>
      </div>
      <div class="mt-8">
        <div class="prose pt-4 mb-4">
          <h3 class="mb-0">Concluded Events</h3>
          <p class="text-sm">View past events and manage post-event tasks.</p>
        </div>
        <div v-if="concluded_events.data && concluded_events.data.length > 0" class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <EventCard v-for="event in concluded_events.data" :key="event.name" :event="event" />
        </div>
        <div v-else class="text-base mt-6 text-gray-800">
          <div>No concluded events found.</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { createListResource } from 'frappe-ui'
import { inject } from 'vue'
import ChapterCard from '@/components/ChapterCard.vue'
import EventCard from '@/components/EventCard.vue'

const session = inject('$session')

const concluded_events = createListResource({
  doctype: 'FOSS Chapter Event',
  fields: ['name', 'event_name', 'event_type', 'chapter_name', 'status', 'event_start_date'],
  filters: {
    event_end_date: ['<=', new Date()],
    status: ['in', ['Concluded', 'Cancelled']],
  },
  orderBy: 'event_start_date desc',
  pageLength: 999,
})

const scheduled_events = createListResource({
  doctype: 'FOSS Chapter Event',
  fields: ['name', 'event_name', 'event_type', 'chapter_name', 'status', 'event_start_date'],
  filters: {
    event_end_date: ['>', new Date()],
    status: ['in', ['Draft', 'Live']],
  },
  orderBy: 'event_start_date',
  pageLength: 999,
})

const chapters = createListResource({
  doctype: 'FOSS Chapter',
  fields: ['*'],
  filters: [['FOSS Chapter Lead Team Member', 'email', 'like', `%${session.user}%`]],
  auto: true,
  pageLength: 999,
  onSuccess(data) {
    if (!data.length) {
      return
    }
    scheduled_events.update({
      filters: {
        ...scheduled_events.filters,
        chapter: ['in', data.map((d) => d.name)],
      },
    })
    scheduled_events.fetch()
    // update concluded events filters as well
    concluded_events.update({
      filters: {
        ...concluded_events.filters,
        chapter: ['in', data.map((d) => d.name)],
      },
    })
    concluded_events.fetch()
  },
})


</script>
