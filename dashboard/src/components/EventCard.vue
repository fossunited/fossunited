<template>
  <Card
    :title="event.event_name"
    class="border-2 border-transparent hover:border-gray-500 transition-colors hover:cursor-pointer"
    @click="() => $router.push(`/event/${event.name}`)"
  >
    <div class="flex justify-between">
      <div class="text-sm font-medium">
        {{ event.chapter_name }}
      </div>
      <Badge :variant="'subtle'" :theme="badgeColors[event.status]" :label="event.status"></Badge>
    </div>
    <div class="text-sm font-medium">
      {{
        new Date(event.event_start_date).toLocaleDateString('en-IN', {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
        })
      }}
    </div>
  </Card>
</template>
<script setup>
import { Card, Badge } from 'frappe-ui'

const badgeColors = {
  Draft: 'orange',
  Approved: 'green',
  Live: 'green',
  Concluded: 'gray',
  Cancelled: 'red',
}
defineProps({
  event: {
    type: Object,
    required: true,
  },
})
</script>
