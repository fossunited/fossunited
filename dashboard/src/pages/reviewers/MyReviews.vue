<template>
  <div class="p-4 max-w-2xl">
    <div class="prose pb-0">
      <h2 class="mb-1">Review Proposals</h2>
      <p class="text-sm mb-4">
        Open CFPs you can review. Use the button to open proposals in Frappe Desk — use
        the <b>Assigned to Me</b> filter or <b>Reviews</b> tab to add your review.
      </p>
    </div>

    <div v-if="!events.data" class="mt-4 text-sm text-ink-gray-5">Loading…</div>

    <div v-else-if="events.data.length === 0" class="flex flex-col gap-2 rounded p-4 border bg-surface-gray-1">
      <div class="text-sm font-medium uppercase text-ink-gray-8">No Open CFPs</div>
      <div class="text-xs text-ink-gray-5">There are no CFPs open for review right now.</div>
    </div>

    <div v-else class="mt-4 flex flex-col gap-3">
      <div
        v-for="event in events.data"
        :key="event.event"
        class="flex flex-col gap-3 p-4 border rounded hover:bg-surface-gray-1"
      >
        <div class="flex flex-col gap-1">
          <div class="text-xs uppercase text-ink-gray-5">
            {{ event.chapter_name }} · {{ dayjs(event.start_date).format('D MMM YYYY') }}
          </div>
          <h4 class="text-base font-semibold text-ink-gray-9">{{ event.event_name }}</h4>
        </div>

        <div class="flex flex-wrap gap-4 text-sm">
          <span class="text-ink-gray-7">{{ event.submission_count }} proposals</span>
          <span class="text-ink-green-3">{{ event.reviewed_count }} reviewed</span>
          <span class="text-orange-700">{{ event.not_reviewed_count }} pending</span>
        </div>

        <div v-if="event.active_phase" class="text-xs text-blue-700 bg-blue-50 border border-blue-200 rounded px-3 py-2">
          <b>Phase:</b> {{ event.active_phase.name }}
          <span v-if="event.active_phase.proposal_visibility === 'Only Assigned'"> · Only assigned proposals visible</span>
        </div>

        <div class="flex gap-2">
          <a :href="`/app/foss-event-cfp-submission?linked_cfp=${event.cfp}`" target="_blank">
            <Button label="Review in Desk" variant="solid" size="sm" />
          </a>
          <a :href="`/app/foss-event-cfp-submission?linked_cfp=${event.cfp}&_is_assigned=Yes`" target="_blank">
            <Button label="Assigned to Me" variant="outline" size="sm" />
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { createResource, Button } from 'frappe-ui'
import dayjs from 'dayjs'

const events = createResource({
  url: 'fossunited.api.reviewer.get_events_by_open_cfp',
  auto: true,
})
</script>
