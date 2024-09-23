<template>
  <div v-if="events.data" class="p-4">
    <div class="prose">
      <div class="prose pb-0">
        <h2 class="mb-1">Review Talks</h2>
        <p class="text-sm mb-4">List of all upcoming events with proposal forms.</p>
      </div>
    </div>
    <div v-if="events.data.length > 0" class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card
        v-for="event in events.data"
        :key="event.name"
        :title="event.event_name"
        class="border-2 border-transparent !rounded-[8px] hover:border-gray-500 transition-colors hover:cursor-pointer"
        @click="$router.push('/review/' + event.event)"
      >
        <template #actions>
          <Tooltip text="Total Submissions">
            <div class="text-base px-3 py-1 bg-gray-100 rounded-sm">
              <span>{{ event.submission_count }}</span>
            </div>
          </Tooltip>
        </template>
        <div class="flex justify-between items-end">
          <span class="text-sm">{{ event.chapter_name }}</span>
          <div class="text-sm text-gray-600">
            <span>{{ formatDate(event.start_date) }}</span>
            <span v-if="formatDate(event.start_date) != formatDate(event.end_date)">
              - {{ formatDate(event.end_date) }}</span
            >
          </div>
        </div>
      </Card>
    </div>
    <div v-else class="flex flex-col gap-2 rounded-sm p-4 border bg-gray-50">
      <div class="text-sm font-medium uppercase text-gray-800">No Call For Proposals</div>
      <div class="text-xs text-gray-600">
        There are no CFPs open right now. There are no talks to review.
      </div>
    </div>
  </div>
</template>
<script setup>
import { createResource, Tooltip } from 'frappe-ui'

const events = createResource({
  url: 'fossunited.api.reviewer.get_events_by_open_cfp',
  auto: true,
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}
</script>
