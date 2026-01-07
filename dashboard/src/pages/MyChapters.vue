<template>
  <div v-if="chapters" class="p-4">
    <div class="prose">
      <div class="prose pb-0">
        <h2 class="mb-1">My Chapters</h2>
        <p class="text-sm mb-4">Manage the chapters you are a part of.</p>
      </div>
    </div>
    <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <ChapterCard v-for="chapter in chapters" :key="chapter.name" :chapter="chapter" />
    </div>
    <div class="mt-4">
      <div class="prose pt-4 mb-4">
        <h3 class="mb-0">Scheduled Events</h3>
        <p class="text-sm">Manage upcoming events.</p>
      </div>
      <div v-if="scheduled_events.length > 0" class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <EventCard v-for="event in scheduled_events" :key="event.name" :event="event" />
      </div>
      <div v-else class="text-base mt-6 text-gray-800">
        <div>There are no scheduled events.</div>
      </div>
      <div class="mt-8">
        <div class="prose pt-4 mb-4">
          <h3 class="mb-0">Concluded Events</h3>
          <p class="text-sm">View recently closed events and manage post-event tasks.</p>
        </div>
        <div v-if="concluded_events.length > 0" class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <EventCard v-for="event in concluded_events" :key="event.name" :event="event" />
        </div>
        <div v-else class="text-base mt-6 text-gray-800">
          <div>No concluded events found.</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { createResource } from 'frappe-ui'

import ChapterCard from '@/components/ChapterCard.vue'
import EventCard from '@/components/EventCard.vue'

const myChapters = createResource({
  url: 'fossunited.api.chapter.get_my_chapter_dashboard',
  auto: true,
})

const chapters = computed(() => myChapters.data?.chapters || [])
const scheduled_events = computed(() => myChapters.data?.scheduled || [])
const concluded_events = computed(() => myChapters.data?.recent_concluded || [])
</script>
